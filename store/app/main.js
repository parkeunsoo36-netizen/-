// 상태를 들고 있고, 버튼·검색을 받아서 다시 그린다 (탭: 추천 찾기 / 트렌드)
(() => {
  const F = {
    concern: ["잡티·미백", "여드름", "모공·피지", "민감·진정", "보습·건조", "노화·탄력", "자외선", "다크서클·눈가"],
    skin: ["지성", "건성", "수부지", "복합성", "민감성", "중성"],
    form: ["크림", "세럼앰플", "토너", "패드", "팩마스크", "선케어", "클렌저"],
    time: ["아침", "밤"],
  };
  const blank = () => ({ concern: [], skin: [], form: [], time: [], ingredient: [], word: [], country: "", shown: 20 });
  let st = blank(), open = false, tab = "find", sh = null, tc = "", tshown = 10;
  const $ = id => document.getElementById(id);
  const names = OB.products.map(p => p.name.toLowerCase());
  const count = {};
  OB.products.forEach(p => Array.isArray(p.ingredients) && p.ingredients.forEach(i => count[i] = (count[i] || 0) + 1));
  const hasCond = () => ["concern", "skin", "form", "time", "ingredient", "word"].some(c => st[c].length) || !!st.country;

  function inView() {  // 지금 조건(추천 성분 빼고)에 맞는 제품에 든 성분 수 → 눌러도 0개가 안 나오는 성분만 추천
    const n = {};
    for (const r of Score.products(OB.products, { ...st, ingredient: [] }, OB.trend))
      if (Array.isArray(r.p.ingredients)) r.p.ingredients.forEach(i => n[i] = (n[i] || 0) + 1);
    return n;
  }

  function renderFind() {
    $("chips").innerHTML = View.selected(st, OB.countries);
    $("sumtext").textContent = View.summary(st);
    $("toggle").setAttribute("aria-expanded", open);
    $("panel").hidden = !open;
    if (open) $("panel").innerHTML = View.filters(st, F, OB.countries);
    $("ings").innerHTML = View.ingCards(Score.ingredients(OB.dict, st, OB.trend, inView()), st);
    $("results").innerHTML = Card.list(Score.products(OB.products, st, OB.trend), st, st.shown, hasCond());
    $("examples").hidden = hasCond();
  }

  function render() {
    for (const v of ["find", "dict", "trend"]) $(v).hidden = tab !== v;
    document.body.dataset.tab = tab;  // 추천 찾기 탭만 2단계 디자인
    $("form").hidden = tab !== "find";
    $("title").textContent = { find: "추천 찾기", dict: "성분 사전", trend: "트렌드" }[tab];
    document.querySelectorAll(".tabbar button").forEach(b => b.setAttribute("aria-current", b.dataset.val === tab ? "page" : "false"));
    if (tab === "find") renderFind();
    if (tab === "dict") $("dlist").innerHTML = Dict.list($("dq").value, count);
    if (tab === "trend") $("trend").innerHTML = Trend.page(tc, tshown, count);
    $("sheet").hidden = !sh;
    if (sh) $("sheetbody").innerHTML = sheetHtml();
  }

  function sheetHtml() {
    if (sh.k === "ing") return Sheet.html(sh.v, st.ingredient.includes(sh.v));
    if (sh.k === "prod") return Product.html(sh.v, st);
    return Trend.sheet(sh.v, count);
  }

  function toggle(cat, val) {
    if (cat === "country") st.country = st.country === val ? "" : val;
    else st[cat] = st[cat].includes(val) ? st[cat].filter(v => v !== val) : [...st[cat], val];
    st.shown = 20;
  }

  function act(b) {
    const { act: a, cat, val } = b.dataset;
    if (a === "toggle") { toggle(cat, val); if (b.closest("#sheet")) { sh = null; tab = "find"; scrollTo(0, 0); } }
    if (a === "remove") cat === "country" ? (st.country = "") : (st[cat] = st[cat].filter(v => v !== val));
    if (a === "reset") st = blank();
    if (a === "more") st.shown += 20;
    if (a === "panel") open = !open;
    if (a === "say") return search(b.textContent);
    if (a === "ing") sh = { k: "ing", v: val };
    if (a === "tcard") sh = { k: "trend", v: +val };
    if (a === "prod") sh = { k: "prod", v: val };
    if (a === "lang") Sheet.setLang(val);
    if (a === "close") sh = null;
    if (a === "tab") { tab = val; sh = null; scrollTo(0, 0); }
    if (a === "tcountry") { tc = val; tshown = 10; }
    if (a === "tmore") tshown += 20;
    render();
  }

  function search(text) {
    const { out, found } = Query.parse(text, OB.syn, names);
    $("hint").textContent = found ? "" : `"${text}"에서 아는 말을 못 찾았어요. 고민이나 성분 이름으로 써 보세요.`;
    for (const c of Object.keys(out)) out[c].forEach(v => st[c].includes(v) || st[c].push(v));
    st.shown = 20; tab = "find";
    render();
  }

  document.addEventListener("click", e => { const b = e.target.closest("[data-act]"); if (b) act(b); });
  document.addEventListener("keydown", e => {
    if (e.key === "Escape" && sh) { sh = null; render(); }
    if (e.key === "Enter" && e.target.matches("li[data-act]")) act(e.target);
  });
  $("dq").addEventListener("input", () => { $("dlist").innerHTML = Dict.list($("dq").value, count); });
  $("form").addEventListener("submit", e => {
    e.preventDefault();
    const q = $("q").value.trim();
    if (q) { search(q); $("q").value = ""; $("q").blur(); }
  });
  render();
})();
