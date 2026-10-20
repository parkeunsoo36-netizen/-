// 화면 그리기만 한다 (상태는 main.js). 모든 글자는 esc()를 거친다
const View = (() => {
  const LABEL = { 세럼앰플: "세럼·앰플", 팩마스크: "팩·마스크" };
  const lab = v => LABEL[v] || v;
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const btn = (act, cat, val, text, on) =>
    `<button type="button" class="chip${on ? " on" : ""}" data-act="${act}" data-cat="${cat}" data-val="${esc(val)}" aria-pressed="${!!on}">${esc(text)}</button>`;

  function selected(st, countries) {  // 고른 조건 칩 (× 로 하나씩 빼기)
    const items = [];
    for (const c of ["concern", "skin", "form", "time", "ingredient"])
      for (const v of st[c]) items.push([c, v, c === "ingredient" ? OB.dict[v].name : lab(v)]);
    for (const w of st.word) items.push(["word", w, `"${w}"`]);
    if (st.country) items.push(["country", st.country, "손님 " + countries[st.country]]);
    if (!items.length) return "";
    return items.map(([c, v, t]) => `<button type="button" class="sel" data-act="remove" data-cat="${c}" data-val="${esc(v)}">${esc(t)}<span aria-hidden="true">×</span></button>`).join("")
      + `<button type="button" class="reset" data-act="reset">초기화</button>`;
  }

  function group(title, cat, opts, st) {
    const on = v => cat === "country" ? st.country === v[0] : st[cat].includes(v[0]);
    return `<div class="grp"><h3>${title}</h3><div class="opts">${opts.map(v => btn("toggle", cat, v[0], v[1], on(v))).join("")}</div></div>`;
  }

  function filters(st, F, countries) {
    const pair = arr => arr.map(v => [v, lab(v)]);
    return group("고민", "concern", pair(F.concern), st) + group("피부 타입", "skin", pair(F.skin), st)
      + group("제형", "form", pair(F.form), st) + group("사용 시간", "time", pair(F.time), st)
      + group("손님 국가 <small>고르면 그 나라 트렌드 성분에 +1</small>", "country", Object.entries(countries), st);
  }

  function summary(st) {
    const n = ["concern", "skin", "form", "time"].reduce((a, c) => a + st[c].length, 0) + (st.country ? 1 : 0);
    return n ? `조건 ${n}개 고름` : "고민·피부·제형으로 고르기";
  }

  function ingCards(list, st) {
    if (!list.length) return "";
    const head = st.concern.length || st.skin.length || Score.picked(st).length ? "추천 성분" : "요즘 뜨는 성분";
    return `<h2>${head} <small>누르면 이 성분 든 제품만 보여요</small></h2><div class="ings">` + list.map(x =>
      `<button type="button" class="ing${st.ingredient.includes(x.id) ? " on" : ""}" data-act="toggle" data-cat="ingredient" data-val="${esc(x.id)}" aria-pressed="${st.ingredient.includes(x.id)}">
        <b>${esc(x.d.name)}</b><span>${esc(x.d.fx)}</span><em>${Score.hotBonus(x.id) ? "요즘 뜸 · " : ""}매장 ${x.n}개</em></button>`).join("") + `</div>`;
  }

  return { esc, lab, selected, filters, summary, ingCards };
})();
