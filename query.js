// 손님 말 → 조건(고민·피부·제형·시간) + 검색어. 동의어 사전에서 긴 말부터 찾아서 지운다
// 성분·제품 이름(예: 리들샷, 나이아신아마이드, 조선미녀)은 입력한 말 그대로 검색어로 남긴다 → 상품명 또는 성분으로 찾음
const Query = (() => {
  const CATS = ["concern", "skin", "form", "time", "ingredient"];
  let keys = null;

  function buildKeys(syn) {
    const m = new Map();
    for (const c of CATS) for (const [w, v] of Object.entries(syn[c])) {
      const k = w.toLowerCase();
      if (k.length < 2) continue;
      if (!m.has(k)) m.set(k, []);
      m.get(k).push([c, v]);
    }
    return [...m.entries()].sort((a, b) => b[0].length - a[0].length);
  }

  function find(text, w) {  // 영어는 단어 단위로, 한글·한자·일본어는 글자 그대로
    if (!/^[\x00-\x7f]+$/.test(w)) return text.indexOf(w);
    const safe = w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const m = new RegExp("(^|[^a-z0-9])" + safe + "(?=$|[^a-z0-9])").exec(text);
    return m ? m.index + m[1].length : -1;
  }

  function add(out, hits, w) {
    for (const [c, v] of hits) {
      if (c === "ingredient") { if (!out.word.includes(w)) out.word.push(w); continue; }
      for (const x of [].concat(v)) if (!out[c].includes(x)) out[c].push(x);
    }
  }

  function nameWords(t, names) {  // 남은 말 중 우리 매장 상품명에 들어 있는 말 (브랜드·라인 이름)
    return t.split(/\s+/).filter(w => w.length >= 2 && names.some(n => n.includes(w)));
  }

  function parse(text, syn, names) {
    keys = keys || buildKeys(syn);
    let t = " " + text.toLowerCase() + " ";
    const out = { concern: [], skin: [], form: [], time: [], word: [] };
    for (const [w, hits] of keys) {
      let i;
      while ((i = find(t, w)) >= 0) {
        add(out, hits, w);
        t = t.slice(0, i) + " ".repeat(w.length) + t.slice(i + w.length);
      }
    }
    nameWords(t, names).forEach(w => out.word.includes(w) || out.word.push(w));
    const found = Object.values(out).some(v => v.length);
    return { out, found };
  }

  return { parse };
})();
