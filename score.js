// 적합도 = 고민×3 + 피부×2 + 제형×2 + 시간×1 + 국가트렌드×1. 건성+피지 조절 성분은 아래로, 민감성+강한 성분은 ⚠️
// 트렌드에 언급된 매장 제품(인기급상승)은 조건에 맞으면 맨 위로. 추천 성분은 요즘 뜨는 성분에 가산점
const Score = (() => {
  const has = (arr, sel) => Array.isArray(arr) && sel.some(x => arr.includes(x));
  const DRY_SEBUM = 3;
  const flat = s => s.toLowerCase().replace(/\s+/g, "");
  const LOW = {};  // 동의어 사전 성분 말 → 소문자로 찾기
  for (const [k, v] of Object.entries(OB.syn.ingredient)) LOW[k.toLowerCase()] = [...new Set([...(LOW[k.toLowerCase()] || []), ...v])];
  const wordIds = w => LOW[w.toLowerCase()] || [];
  const picked = st => [...st.ingredient, ...st.word.flatMap(wordIds)];  // 고른 성분 + 검색어가 가리키는 성분
  const wordHit = (p, w) => flat(p.name).includes(flat(w)) || has(p.ingredients, wordIds(w));  // 건성 손님에게 피지 조절 강한 제품을 이만큼 아래로

  function passes(p, st) {  // 고른 고민·제형·성분이 하나도 안 맞으면 목록에서 뺀다
    if (st.form.length && !st.form.includes(p.form)) return false;
    if (st.concern.length && !has(p.concerns, st.concern)) return false;
    if (st.ingredient.length && !has(p.ingredients, st.ingredient)) return false;
    if (!st.word.every(w => wordHit(p, w))) return false;  // 검색어마다 상품명 또는 성분에 있어야 함
    return true;
  }

  function points(p, st, trend) {
    const why = st.concern.filter(c => has(p.concerns, [c]));
    let s = why.length * 3;
    if (has(p.skin, st.skin)) { s += 2; why.push(st.skin.filter(k => p.skin.includes(k)).join("·")); }
    if (st.form.includes(p.form)) s += 2;
    if (st.time.length && (st.time.includes(p.time) || p.time === "상관없음")) { s += 1; why.push(st.time.join("·")); }
    if (st.country && has(p.ingredients, trend[st.country] || [])) { s += 1; why.push("손님 나라 트렌드"); }
    if (st.skin.includes("건성") && p.sebum) s -= DRY_SEBUM;
    return { s, why };
  }

  const TOP_VIRAL = 3;  // 인기급상승 제품은 맨 위에 최대 3개 (나머지는 적합도 순서대로)

  function products(list, st, trend) {
    const sens = st.skin.includes("민감성");
    const rows = list.filter(p => passes(p, st))
      .map(p => ({ p, ...points(p, st, trend), warn: sens ? p.warn : [] }))
      .sort((a, b) => b.s - a.s || (a.p.rank || 999) - (b.p.rank || 999));
    const top = rows.filter(r => r.p.viral.length).slice(0, TOP_VIRAL);
    return [...top, ...rows.filter(r => !top.includes(r))];
  }

  function hotBonus(id) {  // 요즘 뜨는 성분 순위: 1~5위 +3, 6~10위 +2, 11~20위 +1
    const r = OB.hot.indexOf(id);
    return r < 0 ? 0 : r < 5 ? 3 : r < 10 ? 2 : 1;
  }

  function ingPoints(id, d, st, trend) {
    const c = d.concerns.filter(x => st.concern.includes(x)).length;
    const sel = picked(st).includes(id);
    if (st.concern.length && !c && !sel) return 0;  // 고른 고민과 상관없는 성분은 빼기
    let s = c * 3 + hotBonus(id);
    if (has(d.skin, st.skin)) s += 2;
    if ((trend[st.country] || []).includes(id)) s += 1;
    if (sel) s += 100;
    if (st.skin.includes("민감성") && d.strong) s -= 5;
    if (st.skin.includes("건성") && d.sebum) s -= 3;
    if (st.time.includes("아침") && d.time === "밤") s -= 5;
    return s;
  }

  function ingredients(dict, st, trend, count) {  // 추천 성분 3개 (매장에 있는 성분만)
    return Object.entries(dict)
      .map(([id, d]) => ({ id, d, s: ingPoints(id, d, st, trend), n: count[id] || 0 }))
      .filter(x => x.s > 0 && x.n > 0)
      .sort((a, b) => b.s - a.s || b.n - a.n)
      .slice(0, 3);
  }

  return { products, ingredients, hotBonus, picked };
})();
