// 트렌드 탭: 요즘 뜨는 성분 + 나라별 트렌드 카드. 카드를 누르면 자세한 내용 시트
const Trend = (() => {
  const { esc } = View;
  const short = n => n.replace(/\(.*?\)/g, "").trim();
  const PLAIN = ["향료", "글리세린", "정제수", "부틸렌글라이콜"];  // 제목에 쓰기엔 흔한 성분
  const md = d => d.slice(5).replace("-", "/");

  function title(c) {  // "핵심 성분 1~2개 · 고민", 20자 이내. 제품명·브랜드 없이
    const names = c.ing.map(id => short(OB.dict[id].name)).filter(n => n.length <= 9 && !PLAIN.includes(n));
    const pool = names.length ? names : c.ing_ko.map(short).filter(n => n.length <= 9 && !PLAIN.includes(n));
    const kw = c.kw[0] ? " · " + c.kw[0] : "";
    for (const k of [2, 1]) { const t = pool.slice(0, k).join("·") + kw; if (t.length <= 20) return t; }
    return (pool[0] || c.kw[0] || "트렌드").slice(0, 20);
  }

  function hotChips(count) {
    const ids = OB.hot.filter(id => count[id]).slice(0, 10);
    return `<h2>요즘 뜨는 성분 <small>최근 트렌드에 많이 나온 순, 매장에 있는 성분만</small></h2><div class="hot">` +
      ids.map((id, i) => `<button type="button" class="hotchip" data-act="ing" data-val="${esc(id)}"><i>${i + 1}</i>${esc(short(OB.dict[id].name))}<em>${count[id]}</em></button>`).join("") + `</div>`;
  }

  function countryRow(sel) {
    const opt = [["", "전체"], ...Object.entries(OB.countries)];
    return `<div class="opts">` + opt.map(([c, n]) => `<button type="button" class="chip${sel === c ? " on" : ""}" data-act="tcountry" data-val="${c}" aria-pressed="${sel === c}">${esc(n)}</button>`).join("") + `</div>`;
  }

  function num(n) {  // 12345 → 1.2만
    return n >= 1e8 ? (n / 1e8).toFixed(1).replace(".0", "") + "억" : n >= 1e4 ? (n / 1e4).toFixed(1).replace(".0", "") + "만"
      : n >= 1e3 ? (n / 1e3).toFixed(1).replace(".0", "") + "천" : String(n);
  }

  function stats(s) {
    return s ? `<span class="ts">조회 ${num(s.views)} · 좋아요 ${num(s.likes)} · 댓글 ${num(s.comments)}</span>` : "";
  }

  function row(c, i, rank, count) {
    const n = c.ing.reduce((a, id) => a + (count[id] ? 1 : 0), 0);
    const store = n ? `<em>매장 성분 ${n}</em>` : "";
    return `<li><button type="button" class="tcard" data-act="tcard" data-val="${i}">
      <b><i class="trk">${rank}</i>${esc(title(c))}</b><span>${esc(OB.countries[c.c] || c.c)} · ${md(c.d)}${c.cat && c.cat !== "스킨케어" ? " · " + esc(c.cat) : ""}</span>${stats(c.st)}${store}</button></li>`;
  }

  function page(tc, shown, count) {  // 인기 점수 순 (조회수·좋아요·댓글). 처음 10개, 더 보기로 20개씩
    const list = OB.feed.map((c, i) => [c, i]).filter(([c]) => !tc || c.c === tc)
      .sort(([a], [b]) => b.pop - a.pop || b.d.localeCompare(a.d));
    const more = list.length > shown ? `<button type="button" class="more" data-act="tmore">더 보기 (${list.length - shown}개 남음)</button>` : "";
    return hotChips(count) + `<h2>나라별 인기 트렌드 TOP ${Math.min(10, list.length)} <small>최근 2주 유튜브 조회수·좋아요·댓글 기준</small></h2>` + countryRow(tc)
      + `<ol class="tlist">${list.slice(0, shown).map(([c, i], k) => row(c, i, k + 1, count)).join("")}</ol>${more}`;
  }

  function sheet(i, count) {
    const c = OB.feed[i];
    const ings = c.ing.filter(id => count[id]).map(id => `<button type="button" class="ki hit" data-act="ing" data-val="${esc(id)}">${esc(short(OB.dict[id].name))}</button>`).join("");
    const vids = c.vid.map(v => `<li><a href="${esc(v.url)}" target="_blank" rel="noopener">${esc(v.title)}</a>${v.views ? ` <small>조회 ${num(v.views)}${v.likes != null ? ` · 좋아요 ${num(v.likes)} · 댓글 ${num(v.comments)}` : ""}</small>` : ""}</li>`).join("");
    const sec = (h, b) => b ? `<details><summary>${h}</summary>${b}</details>` : "";
    return `<h3>${esc(title(c))}</h3><p class="sub">${esc(OB.countries[c.c] || c.c)} · ${md(c.d)} · ${esc(c.t)}</p>
      <p>${esc(c.why)}</p>${ings ? `<p class="kis">${ings}</p><p class="sub">성분을 누르면 설명과 매장 제품을 볼 수 있어요</p>` : ""}
      ${sec("매장에서 확인하는 법", `<p>${esc(c.look)}</p>`)}${sec("영어 추천 멘트", `<p lang="en">${esc(c.pitch)}</p>`)}${sec("영상·출처", vids && `<ul class="vids">${vids}</ul>`)}`;
  }

  return { page, sheet };
})();
