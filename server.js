const http = require("http");
const fs = require("fs");
const path = require("path");

const ROOT = __dirname;
const PORT = Number(process.env.PORT) || 3000;

function sendText(res, status, message) {
  res.writeHead(status, { "Content-Type": "text/plain; charset=utf-8" });
  res.end(message);
}

function collect(dir, prefix, files) {
  for (const name of fs.readdirSync(dir)) {
    const abs = path.join(dir, name);
    const rel = prefix ? `${prefix}/${name}` : name;
    if (fs.statSync(abs).isDirectory()) collect(abs, rel, files);
    else files.push({ rel, b64: fs.readFileSync(abs).toString("base64") });
  }
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
  if (req.method !== "GET") {
    sendText(res, 404, "Not found\n");
    return;
  }

  const pathname = req.url.split("?")[0];
  if (pathname === "/") {
    sendText(
      res,
      200,
      [
        "1. Open a terminal in this folder.",
        "2. Run node server.js",
        "3. Open the folder where you want the files.",
        "4. Run iex(irm http://localhost:3000/1)",
        "5. Use 2, 3, 4, 5, or 6 instead of 1 for the other folders.",
        "",
      ].join("\n")
    );
    return;
  }

  const match = /^\/([1-6])\/?$/.exec(pathname);
  if (!match) {
    sendText(res, 404, "Not found\n");
    return;
  }

  const folder = path.join(ROOT, match[1]);
  const files = [];
  try {
    collect(folder, "", files);
  } catch (err) {
    sendText(res, 404, "Not found\n");
    return;
  }

  sendText(res, 200, toScript(files));
});

server.listen(PORT, () => {
  console.log(`http://localhost:${PORT}/{id}`);
  console.log("In the folder where the files should land:");
  console.log(`iex(irm http://localhost:${PORT}/1)`);
});
