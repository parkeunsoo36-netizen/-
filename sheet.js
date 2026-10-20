// 성분 설명 바텀시트. 한국어·영어 중 골라 보기 (고른 언어는 이 휴대폰에 기억)
const Sheet = (() => {
  const { esc } = View;
  const EN = { "잡티·미백": "dark spots & dullness", "여드름": "acne", "모공·피지": "pores & oil", "민감·진정": "sensitive, calming",
    "보습·건조": "dryness, hydration", "노화·탄력": "wrinkles & firmness", "자외선": "sun protection", "다크서클·눈가": "eye area",
    "지성": "oily", "건성": "dry", "수부지": "dehydrated oily", "복합성": "combination", "민감성": "sensitive", "중성": "normal",
    "밤": "Night only", "아침": "Morning", "상관없음": "Morning or night" };
  let lang = "ko";
  try { lang = localStorage.getItem("ob-lang") || "ko"; } catch (e) {}
  const row = (k, v) => v ? `<div class="row2"><dt>${k}</dt><dd>${esc(v)}</dd></div>` : "";

  function ko(d) {
    const warn = d.strong ? `<p class="warn">⚠️ 자극이 있을 수 있는 성분이에요. 민감성 손님은 주의</p>` : "";
    return `<h3>${esc(d.name)}</h3><p class="sub">${esc(d.en_name)}</p><dl>${row("효과", d.fx)}${row("이런 피부에", d.good)}
      ${row("고민", d.concerns.join(", "))}${row("사용 시간", d.time === "밤" ? "밤에만" : "아침·밤 모두")}${row("주의", d.caution)}</dl>${warn}`;
  }

  function en(d) {
    const good = [...d.concerns.map(c => EN[c]), ...d.skin.map(s => EN[s] + " skin")].join(", ");
    const warn = d.strong ? `<p class="warn">⚠️ Can be irritating. Take care with sensitive skin.</p>` : "";
    return `<h3>${esc(d.en_name)}</h3><p class="sub">${esc(d.name)}</p><dl>${row("What it does", d.en.charAt(0).toUpperCase() + d.en.slice(1))}${row("Good for", good)}
      ${row("When", EN[d.time] || "")}${row("Caution", d.en_caution)}</dl>${warn}`;
  }

  function html(id, inFilter) {
    const d = OB.dict[id];
    const tab = (l, t) => `<button type="button" class="tab${lang === l ? " on" : ""}" data-act="lang" data-val="${l}" aria-pressed="${lang === l}">${t}</button>`;
    const go = inFilter ? "이 성분 조건 빼기" : "이 성분 든 제품만 보기";
    return `<div class="tabs">${tab("ko", "한국어")}${tab("en", "English")}</div>${lang === "en" ? en(d) : ko(d)}
      <button type="button" class="go" data-act="toggle" data-cat="ingredient" data-val="${esc(id)}">${go}</button>`;
  }

  function setLang(l) {
    lang = l;
    try { localStorage.setItem("ob-lang", l); } catch (e) {}
  }

  return { html, setLang, EN, get lang() { return lang; } };
})();
