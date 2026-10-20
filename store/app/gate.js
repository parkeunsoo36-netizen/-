// 비밀번호 화면: 맞으면 매장 데이터를 풀어서(window.OB) 나머지 화면 스크립트를 순서대로 불러온다 (깃허브 사이트용)
(() => {
  const L = window.OB_LOCK, KEY = "ob-staff-pw";
  const b64 = s => Uint8Array.from(atob(s), c => c.charCodeAt(0));

  async function open(pw) {
    const base = await crypto.subtle.importKey("raw", new TextEncoder().encode(pw), "PBKDF2", false, ["deriveKey"]);
    const key = await crypto.subtle.deriveKey({ name: "PBKDF2", salt: b64(L.salt), iterations: L.iter, hash: "SHA-256" },
      base, { name: "AES-GCM", length: 256 }, false, ["decrypt"]);
    const buf = await crypto.subtle.decrypt({ name: "AES-GCM", iv: b64(L.iv) }, key, b64(L.ct));
    return JSON.parse(new TextDecoder().decode(buf));
  }

  function load(i) {  // 화면 스크립트를 순서대로 하나씩
    if (i >= L.scripts.length) return;
    const s = document.createElement("script"); s.src = L.scripts[i]; s.onload = () => load(i + 1); document.body.append(s);
  }

  async function tryPw(pw, box, remember) {
    try { window.OB = await open(pw); } catch (e) { return false; }
    if (remember) try { localStorage.setItem(KEY, pw); } catch (e) {}
    box.remove(); load(0); return true;
  }

  function form() {
    const box = document.createElement("div"); box.className = "gate";
    box.innerHTML = `<form><h2>매장 직원용 추천 찾기</h2><p>비밀번호를 입력하세요</p>
      <input type="password" autocomplete="current-password" aria-label="비밀번호" required>
      <label><input type="checkbox" checked> 이 기기에서 기억</label><button type="submit">열기</button><p class="err" hidden>비밀번호가 맞지 않아요</p></form>`;
    document.body.append(box);
    const f = box.querySelector("form"), err = box.querySelector(".err");
    f.onsubmit = async e => { e.preventDefault(); err.hidden = true; f.querySelector("button").textContent = "여는 중…";
      if (!await tryPw(f.querySelector("[type=password]").value, box, f.querySelector("[type=checkbox]").checked)) { err.hidden = false; f.querySelector("button").textContent = "열기"; } };
    return box;
  }

  const box = form();
  let saved = null; try { saved = localStorage.getItem(KEY); } catch (e) {}
  if (saved) tryPw(saved, box, false).then(ok => { if (!ok) try { localStorage.removeItem(KEY); } catch (e) {} });
})();
