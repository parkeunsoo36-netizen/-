// 제품 한 줄(카드)과 결과 목록
const Card = (() => {
  const { esc, lab } = View;
  const won = n => n ? n.toLocaleString("ko-KR") + "원" : "";

  function keyIngs(p, st) {  // 고른 고민·성분과 관련된 성분부터 4개 (누르면 설명 시트)
    if (!Array.isArray(p.ingredients)) return `<span class="unk">성분 미확인</span>`;
    const sel = Score.picked(st);
    const rel = id => sel.includes(id) ? 2 : OB.dict[id].concerns.some(c => st.concern.includes(c)) ? 1 : 0;
    const ids = [...p.ingredients].sort((a, b) => rel(b) - rel(a)).slice(0, 4);
    return ids.map(id => `<button type="button" class="ki${rel(id) ? " hit" : ""}" data-act="ing" data-val="${esc(id)}">${esc(OB.dict[id].name)}</button>`).join("");
  }

  function where(loc) {
    const tier = loc.tier ? ` <small>${loc.tier}단</small>` : "";
    return `<div class="loc"><small>${esc(loc.floor)}</small><b>${esc(loc.badge.replace(loc.floor + " ", ""))}</b>${tier}</div>`;
  }

  function one(r, st) {
    const p = r.p;
    const warn = r.warn.length ? `<p class="warn">⚠️ 민감성 손님 주의: ${esc(r.warn.join(", "))}</p>` : "";
    const hot = p.viral.length ? `<p class="viral">인기급상승 <span>${esc([...new Set(p.viral.map(v => OB.countries[v[1]] || v[1]))].join("·"))} 트렌드에 나옴</span></p>` : "";
    const why = r.why.length ? `<p class="why">${r.why.map(w => `<span>${esc(w)}</span>`).join("")}</p>` : "";
    return `<li class="card" data-act="prod" data-val="${esc(p.id)}" role="button" tabindex="0" aria-label="${esc(p.name)} 효능 보기">${where(p.loc)}<div class="body">
      ${hot}<p class="brand">${esc(p.brand)} · ${esc(lab(p.form))}</p><h4>${esc(p.name)}</h4>
      <p class="kis">${keyIngs(p, st)}</p>${why}${warn}</div><div class="price">${won(p.price)}<span class="tap">효능 보기 ›</span></div></li>`;
  }

  function list(rows, st, shown, hasCond) {
    const head = hasCond ? `우리 매장 제품 <b>${rows.length}</b>개` : `인기급상승·많이 팔리는 순 <small>조건을 고르면 맞는 순서로 바뀌어요</small>`;
    if (!rows.length) return `<h2>${head}</h2><p class="empty">맞는 제품이 없어요. 조건을 하나 빼 보세요.</p>`;
    const more = rows.length > shown ? `<button type="button" class="more" data-act="more">더 보기 (${rows.length - shown}개 남음)</button>` : "";
    return `<h2>${head}</h2><ol class="list">${rows.slice(0, shown).map(r => one(r, st)).join("")}</ol>${more}`;
  }

  return { list };
})();
