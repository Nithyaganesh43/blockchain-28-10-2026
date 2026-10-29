const http = require("http");
const fs = require("fs");
const path = require("path");

const ROOT = __dirname;
const PORT = Number(process.env.PORT) || 3000;
const logs = [];
const hits = {
  1: 0,
  2: 0,
  3: 0,
  4: 0,
  5: 0,
  6: 0,
  s1: 0,
  s2: 0,
  s3: 0,
  s4: 0,
  s5: 0,
  s6: 0,
  m: 0,
};
const INDEXES = ["1", "2", "3", "4", "5", "6", "s1", "s2", "s3", "s4", "s5", "s6", "m"];

function record(req, pathname) {
  try {
    const index = pathname === "/" ? "/" : pathname.replace(/^\/|\/$/g, "");
    logs.push({
      time: new Intl.DateTimeFormat("en-US", {
        timeZone: "Asia/Kolkata",
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
      })
        .format(new Date())
        .replace(/\u202f/g, " ")
        .toLowerCase(),
      ip: clientIp(req),
      index,
    });
    if (Object.prototype.hasOwnProperty.call(hits, index)) hits[index] += 1;
  } catch (err) {}
}

function clientIp(req) {
  const forwarded = req.headers["x-forwarded-for"];
  const ip = forwarded
    ? String(forwarded).split(",")[0].trim()
    : req.socket.remoteAddress || "";
  return ip.replace(/^::ffff:/, "");
}

function sendText(res, status, message) {
  res.writeHead(status, { "Content-Type": "text/plain; charset=utf-8" });
  res.end(message);
}

const scriptCache = new Map();

async function collect(dir, prefix = "") {
  const names = await fs.promises.readdir(dir);
  const groups = await Promise.all(
    names.map(async (name) => {
      const abs = path.join(dir, name);
      const rel = prefix ? `${prefix}/${name}` : name;
      const stat = await fs.promises.stat(abs);
      if (stat.isDirectory()) return collect(abs, rel);
      const data = await fs.promises.readFile(abs);
      return [{ rel, b64: data.toString("base64") }];
    })
  );
  return groups.flat();
}

function toScript(files) {
  const dirs = new Set();
  for (const file of files) {
    const parts = file.rel.split("/");
    for (let i = 1; i < parts.length; i++) dirs.add(parts.slice(0, i).join("\\"));
  }

  const lines = ["$root = (Get-Location).Path"];
  for (const dir of [...dirs].sort()) {
    lines.push(
      `New-Item -ItemType Directory -Force -Path (Join-Path $root '${dir}') | Out-Null`
    );
  }
  for (const file of files) {
    const rel = file.rel.replaceAll("/", "\\");
    lines.push(
      `[IO.File]::WriteAllBytes((Join-Path $root '${rel}'), [Convert]::FromBase64String('${file.b64}'))`
    );
  }
  return lines.join("\n");
}

const server = http.createServer((req, res) => {
  handle(req, res).catch(() => {
    try {
      if (!res.headersSent) res.end();
    } catch (err) {}
  });
});

async function handle(req, res) {
  if (req.method !== "GET") {
    sendText(res, 404, "Not found\n");
    return;
  }

  const pathname = req.url.split("?")[0];
  if (pathname === "/log") {
    try {
      const lines = INDEXES.map((key) => `${key}: ${hits[key] || 0}`);
      lines.push("", `Total api calls: ${logs.length}`, "");
      for (const entry of logs) {
        lines.push(`${entry.time}  ${entry.ip}  ${entry.index}`);
      }
      sendText(res, 200, lines.join("\n") + "\n");
    } catch (err) {
      sendText(
        res,
        200,
        INDEXES.map((key) => `${key}: 0`).join("\n") + "\n"
      );
    }
    return;
  }

  record(req, pathname);

  if (pathname === "/") {
    sendText(
      res,
      200,
      [ 
        "Open the folder powershell where you want the files",
        "Run for exprimenet 1 (Merkle tree verification): iex(irm https://cse2026bc.onrender.com/1)",
        "Run for exprimenet 2 (Custom blockchain): iex(irm https://cse2026bc.onrender.com/2)",
        "Run for exprimenet 3 (Blockchain prototype): iex(irm https://cse2026bc.onrender.com/3)",
        "Run for exprimenet 4 (Consensus): iex(irm https://cse2026bc.onrender.com/4)",
        "Run for exprimenet 5 (Wallet): iex(irm https://cse2026bc.onrender.com/5)",
        "Run for exprimenet 6 (Voting): iex(irm https://cse2026bc.onrender.com/6)", 
        "Download Lab manual: https://cse2026bc.onrender.com/m",
        "",
      ].join("\n")
    );
    return;
  }

  if (pathname === "/m") {
    const manual = path.join(ROOT, "Blockchain Technologies Lab Manual.pdf");
    let stat;
    try {
      stat = await fs.promises.stat(manual);
    } catch (err) {
      sendText(res, 404, "Not found\n");
      return;
    }
    res.writeHead(200, {
      "Content-Type": "application/pdf",
      "Content-Length": stat.size,
      "Content-Disposition":
        'attachment; filename="Blockchain Technologies Lab Manual.pdf"',
    });
    fs.createReadStream(manual).pipe(res);
    return;
  }

  const match = /^\/(s?[1-6])\/?$/.exec(pathname);
  if (!match) {
    sendText(res, 404, "Not found\n");
    return;
  }

  const id = match[1];
  let pending = scriptCache.get(id);
  if (!pending) {
    pending = collect(path.join(ROOT, id))
      .then((files) => toScript(files))
      .catch((err) => {
        scriptCache.delete(id);
        throw err;
      });
    scriptCache.set(id, pending);
  }

  let script;
  try {
    script = await pending;
  } catch (err) {
    sendText(res, 404, "Not found\n");
    return;
  }

  sendText(res, 200, script);
}

server.listen(PORT, () => {
  console.log(`http://localhost:${PORT}/{id}`);
  console.log("In the folder where the files should land:");
  console.log(`iex(irm http://localhost:${PORT}/1)`);
});
