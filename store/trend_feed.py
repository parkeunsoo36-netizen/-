# 트렌드 데이터를 추천 화면용으로 줄인다: 최근 성분 순위(요즘 뜨는 성분) + 트렌드 탭 카드 목록
# make_page_data.py 가 불러 씀
import json, glob, os, re, math, collections, datetime
here = os.path.dirname(os.path.abspath(__file__))
DAYS = 14  # 최근 14일치만 화면에 넣음

def load_items():
    files = sorted(glob.glob(os.path.join(here, "..", "data", "*.json")))[-DAYS:]
    items, names = [], {}
    for f in files:
        day = json.load(open(f, encoding="utf-8"))
        for c, v in day.get("countries", {}).items(): names[c] = v["name"]
        for it in day.get("items", []): items.append({**it, "_d": day["date"]})
    return items, names

def ing_ids(it, syn):
    return sorted({i for pair in it.get("ing", []) for w in pair for i in syn.get(w.lower(), syn.get(w, []))})

def hot(items, syn, top=20):  # 최근일수록 무게: 마지막 3일 ×3, 4~7일 ×2, 그 전 ×1
    last = max(datetime.date.fromisoformat(it["_d"]) for it in items)
    score = collections.Counter()
    for it in items:
        age = (last - datetime.date.fromisoformat(it["_d"])).days
        for i in ing_ids(it, syn): score[i] += 3 if age < 3 else 2 if age < 7 else 1
    return [i for i, _ in score.most_common(top)]

def vid_id(url):
    m = re.search(r"(?:v=|youtu\.be/|shorts/)([\w-]{11})", url)
    return m.group(1) if m else ""

def popularity(s):  # 인기 점수: 조회수 + 좋아요(×1.5) + 댓글(×2), 큰 숫자가 독차지하지 않게 log
    return round(math.log10(s["views"] + 1) + 1.5 * math.log10(s["likes"] + 1) + 2 * math.log10(s["comments"] + 1), 2)

def best(it, stats):  # 트렌드 항목의 영상 중 가장 인기 있는 영상 숫자
    rows = [stats[i] for i in (vid_id(v["url"]) for v in it.get("vid", [])) if i in stats]
    return max(rows, key=popularity, default=None)

def card(it, syn, stats):  # 트렌드 탭 카드 1장
    vids = [{"title": v["title"], "url": v["url"], **stats.get(vid_id(v["url"]), {"views": v.get("views")})} for v in it.get("vid", [])[:3]]
    top = best(it, stats)
    return {"d": it["_d"], "c": it["c"], "cat": it.get("cat", ""), "kw": it.get("kw", []), "t": it["t"],
            "ing": ing_ids(it, syn), "ing_ko": [p[0] for p in it.get("ing", [])], "why": it.get("why", ""),
            "look": it.get("look", ""), "pitch": it.get("pitch", ""), "vid": vids,
            "pop": popularity(top) if top else 0, "st": top}

PER_COUNTRY = 30  # 화면은 나라별 TOP 10 + 더 보기라서, 나라마다 인기 상위 30장만 넣음 (페이지 가볍게)

def feed(items, syn, stats):  # 트렌드 탭 카드 목록: 나라별 인기순 상위 PER_COUNTRY장
    cards = [card(it, syn, stats) for it in reversed(items)]
    cards.sort(key=lambda c: (c["pop"], c["d"]), reverse=True)  # 화면과 같은 순서: 인기순, 같으면 최신순
    kept, n = [], collections.Counter()
    for c in cards:
        n[c["c"]] += 1
        if n[c["c"]] <= PER_COUNTRY: kept.append(c)
    return kept
