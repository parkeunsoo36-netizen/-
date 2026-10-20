# 사용법: python3 make_page_data.py → app/data.js (추천 찾기 화면이 읽는 데이터. 매장 정보라 비공개 페이지에만 씀)
import json, os, collections
import trend_feed, find_viral
here = os.path.dirname(os.path.abspath(__file__))
load = lambda *p: json.load(open(os.path.join(here, *p), encoding="utf-8"))
ZONES = "ABDE"  # 스킨케어 1·2차, 선·클렌징, 마스크팩 (색조·헤어바디·건기식 제외)
P_KEYS = ["id", "name", "brand", "form", "price", "ingredients", "concerns", "skin", "time", "loc", "rank", "warn", "sebum", "photo"]
D_KEYS = ["name", "fx", "good", "caution", "concerns", "skin", "strong", "sebum", "time", "en"]

def english(k, v, cau):  # 영어 설명용: INCI 이름 + 주의 문구 번역 (en_caution.json)
    name = min(v["inci"], key=len) if v["inci"] else k.title()  # 가장 짧은 INCI 이름
    return {"en_name": name, "en_caution": cau.get(v["caution"], "")}

def products():
    return [{k: p[k] for k in P_KEYS} for p in load("products.json") if p["loc"]["zone"] in ZONES and p["form"] != "기타"]

def by_country(items, syn, top=15):  # 나라별로 많이 나온 성분 15개 (손님 국가 +1 점용)
    out = collections.defaultdict(collections.Counter)
    for it in items: out[it["c"]].update(trend_feed.ing_ids(it, syn))
    return {c: [i for i, _ in n.most_common(top)] for c, n in out.items()}

if __name__ == "__main__":
    syn = load("synonyms.json")
    cau = load("en_caution.json")
    dic = {k: {**{f: v[f] for f in D_KEYS}, **english(k, v, cau)} for k, v in load("ingredient_dict.json").items()}
    items, names = trend_feed.load_items()
    sp = os.path.join(here, "video_stats.json")  # fetch_stats.py 가 만든 영상 숫자 (없으면 인기 점수 0)
    stats = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else {}
    ps, si = products(), syn["ingredient"]
    viral = find_viral.viral(ps, items)
    for p in ps: p["viral"] = viral.get(p["id"], [])
    data = {"products": ps, "dict": dic, "syn": syn, "trend": by_country(items, si), "countries": names,
            "hot": trend_feed.hot(items, si), "feed": trend_feed.feed(items, si, stats),
            "last": max(it["_d"] for it in items)}
    js = "window.OB = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";\n"
    open(os.path.join(here, "app", "data.js"), "w", encoding="utf-8").write(js)
    print(len(ps), "제품,", len(dic), "성분, 트렌드", len(items), "건, 바이럴 제품", len(viral), "개, 뜨는 성분", data["hot"][:8])
