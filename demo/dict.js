// 성분 사전 탭: 매장에 있는 성분을 이름(한글·영어·동의어)으로 찾고, 누르면 설명 시트
const Dict = (() => {
  const { esc } = View;
  const words = {};  // 성분 id → 찾을 말 모음
  for (const [w, ids] of Object.entries(OB.syn.ingredient)) for (const id of ids) words[id] = (words[id] || "") + " " + w.toLowerCase();

  function match(id, q) {
    const d = OB.dict[id];
    return !q || (d.name + " " + d.en_name + words[id]).toLowerCase().replace(/\s+/g, "").includes(q);
  }

  function list(q, count) {
    q = q.toLowerCase().replace(/\s+/g, "");
    const ids = Object.keys(OB.dict).filter(id => count[id] && match(id, q))
      .sort((a, b) => Score.hotBonus(b) - Score.hotBonus(a) || count[b] - count[a]);
    if (!ids.length) return `<p class="empty">매장 제품에 든 성분 중에 "${esc(q)}"는 없어요.</p>`;
    return `<h2 class="rh">매장 제품에 든 성분 <b>${ids.length}</b>개 <small>요즘 뜨는 순 · 많은 순</small></h2><ul class="dl">` + ids.map(id => {
      const d = OB.dict[id], up = Score.hotBonus(id) ? `<em class="up">요즘 뜸</em>` : "";
      return `<li><button type="button" data-act="ing" data-val="${esc(id)}"><b>${esc(d.name)}</b>${up}<span>${esc(d.fx)}</span><small>${esc(d.en_name)} · 매장 ${count[id]}개</small></button></li>`;
    }).join("") + `</ul>`;
  }

  return { list };
})();
