# 사용법: python3 make_demo.py → ../site/demo/ 에 깃허브용 체험판(가짜 매장 데이터) 추천 찾기 페이지를 만든다
# 실제 매장 제품·진열 위치·가격은 하나도 넣지 않음. 성분 사전·트렌드(공개 정보)만 실제 데이터를 씀
import json, os, random, shutil
import tag_products
here = os.path.dirname(os.path.abspath(__file__))
app, out = os.path.join(here, "app"), os.path.join(here, "..", "site", "demo")
FORMS = ["크림", "세럼앰플", "토너", "패드", "팩마스크", "선케어", "클렌저"]
BRANDS = ["체험브랜드 A", "체험브랜드 B", "체험브랜드 C", "체험브랜드 D"]
ZONES = "ABDE"
N = 60

def fake(i, ings, rnd):
    form = FORMS[i % len(FORMS)]
    name = f"{BRANDS[i % len(BRANDS)].split()[-1]} {tag_products.DIC[ings[0]]['name']} {form} (예시)"
    zone, rack = rnd.choice(ZONES), rnd.randint(1, 6)
    p = {"id": f"demo{i:03d}", "name": name, "brand": BRANDS[i % len(BRANDS)], "form": form, "price": rnd.randrange(8000, 40000, 1000),
         "ingredients": ings, "loc": {"floor": "1F", "zone": zone, "rack": str(rack), "tier": 1, "slot": 1, "badge": f"1F {zone}-{rack}"},
         "rank": i, "photo": "미확인", "viral": []}
    return tag_products.tag(p)

def products(ob, rnd):
    pool = [k for k in ob["hot"] if k in tag_products.DIC] + [k for k in tag_products.DIC if tag_products.DIC[k]["concerns"]]
    ps = [fake(i, sorted(set(rnd.sample(pool[:60], 3))), rnd) for i in range(N)]
    for p in ps[:3]: p["viral"] = [[ob["last"], next(iter(ob["countries"])), "체험판 예시: 요즘 뜨는 성분이 든 제품"]]
    return ps

def page():
    html = open(os.path.join(app, "index.html"), encoding="utf-8").read()
    head = '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"></head><body>\n'
    note = '<p class="demo">체험판이에요. 제품 이름·진열 위치·가격은 예시 값이고, 성분 설명과 트렌드는 실제 데이터예요.</p>\n'
    return head + html.replace('<main class="wrap">', '<main class="wrap">\n' + note, 1) + "</body></html>\n"

if __name__ == "__main__":
    js = open(os.path.join(app, "data.js"), encoding="utf-8").read()
    ob = json.loads(js[js.index("=") + 1:].strip().rstrip(";"))
    ob["products"] = products(ob, random.Random(7))
    shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
    for f in os.listdir(app):
        if f not in ("data.js", "index.html", "gate.js"): shutil.copy(os.path.join(app, f), out)
    data = "window.OB = " + json.dumps(ob, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";\n"
    open(os.path.join(out, "data.js"), "w", encoding="utf-8").write(data)
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page())
    print("체험판 완료:", len(ob["products"]), "개 예시 제품 →", out)
