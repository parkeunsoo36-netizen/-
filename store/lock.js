// 사용법: node lock.js → 깃허브 사이트용 비밀번호 페이지(../site/staff/)를 만든다
// 매장 데이터(app/data.js)는 비밀번호로 암호화(AES-256-GCM, PBKDF2 60만 회)해서 data.enc.js 로만 내보냄. 원본은 절대 복사하지 않음
const fs = require("fs"), path = require("path"), crypto = require("crypto");
const here = __dirname, app = path.join(here, "app"), out = path.join(here, "..", "site", "staff");
const PW_FILE = path.join(here, ".staff_password");  // 비밀번호 한 줄. 공유 폴더에만 있고 깃허브에는 안 올림
const ITER = 600000;

function encrypt(text, pw) {
  const salt = crypto.randomBytes(16), iv = crypto.randomBytes(12);
  const key = crypto.pbkdf2Sync(pw, salt, ITER, 32, "sha256");
  const c = crypto.createCipheriv("aes-256-gcm", key, iv);
  const ct = Buffer.concat([c.update(text, "utf8"), c.final(), c.getAuthTag()]);  // 브라우저 WebCrypto 형식: 암호문 + 태그
  return { iter: ITER, salt: salt.toString("base64"), iv: iv.toString("base64"), ct: ct.toString("base64") };
}

function page(scripts) {  // index.html 에서 스크립트 태그를 빼고, 잠금 화면(gate.js)만 남김
  const html = fs.readFileSync(path.join(app, "index.html"), "utf8").replace(/<script src="[^"]+"><\/script>\n?/g, "");
  const head = '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><meta name="robots" content="noindex"></head><body>\n';
  return head + html + '<script src="data.enc.js"></script>\n<script src="gate.js"></script>\n</body></html>\n';
}

function main() {
  if (!fs.existsSync(PW_FILE)) { console.log("비밀번호 파일이 없어 잠금 페이지를 만들지 않음"); return; }
  const pw = fs.readFileSync(PW_FILE, "utf8").trim();
  const js = fs.readFileSync(path.join(app, "data.js"), "utf8");
  const json = js.slice(js.indexOf("=") + 1).trim().replace(/;$/, "");
  const scripts = [...fs.readFileSync(path.join(app, "index.html"), "utf8").matchAll(/<script src="([^"]+)">/g)].map(m => m[1]).filter(s => s !== "data.js");
  fs.rmSync(out, { recursive: true, force: true }); fs.mkdirSync(out, { recursive: true });
  for (const f of fs.readdirSync(app)) if (f !== "data.js" && f !== "index.html") fs.copyFileSync(path.join(app, f), path.join(out, f));
  fs.writeFileSync(path.join(out, "data.enc.js"), "window.OB_LOCK = " + JSON.stringify({ ...encrypt(json, pw), scripts }) + ";\n");
  fs.writeFileSync(path.join(out, "index.html"), page(scripts));
  console.log("잠금 페이지 완료:", out);
}
main();
