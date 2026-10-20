# 사용법: python3 make_demo.py → ../site/ 에 깃허브 사이트 첫 화면 = 추천 찾기 체험판(가짜 매장 데이터)을 만든다
# 실제 매장 제품·진열 위치·가격은 하나도 넣지 않음. 성분 사전·트렌드(공개 정보)만 실제 데이터를 씀
import json, os, random, shutil
import tag_products
here = os.path.dirname(os.path.abspath(__file__))
app, out = os.path.join(here, "app"), os.path.join(here, "..", "site")
KEEP = {"manifest.json", "sw.js", "icon-192.png", "icon-512.png", ".nojekyll", "og.png"}  # 휴대폰 설치용 파일·링크 미리보기 이미지는 그대로 둠
SITE = "https://parkeunsoo36-netizen.github.io/offbeauty-recommend-note/"
DESC = "손님 말 한마디로 필요한 성분, 매장 제품, 진열 위치까지. 명동 매장 직원용 K뷰티 추천 도구 체험판"
FORMS = ["크림", "세럼앰플", "토너", "패드", "팩마스크", "선케어", "클렌저"]
BRANDS = ["체험브랜드 A", "체험브랜드 B", "체험브랜드 C", "체험브랜드 D"]
ZONES = "ABDE"
N = 60

def fake(i, hero, others, rnd, brand):  # 제품 이름·고민은 대표 성분(hero) 하나로 맞춤 → 추천 이유와 이름이 어긋나지 않게
    form = FORMS[i % len(FORMS)]
    if form == "선케어" and tag_products.DIC[hero]["time"] == "밤": form = "크림"
    ings = [hero] + others
    name = f"{brand.split()[-1]} {tag_products.DIC[hero]['name']} {form} (예시)"
    zone, rack = rnd.choice(ZONES), rnd.randint(1, 6)
    p = {"id": f"demo{i:03d}", "name": name, "brand": brand, "form": form, "price": rnd.randrange(8000, 40000, 1000),
         "ingredients": ings, "loc": {"floor": "1F", "zone": zone, "rack": str(rack), "tier": 1, "slot": 1, "badge": f"1F {zone}-{rack}"},
         "rank": i, "photo": "미확인", "viral": []}
    p = tag_products.tag(p)
    p["concerns"] = tag_products.tag({**p, "ingredients": [hero]})["concerns"]  # 주의 표시(warn)는 성분 전체 기준 그대로
    return p

def products(ob, rnd):
    pool = list(dict.fromkeys([k for k in ob["hot"] if k in tag_products.DIC] + [k for k in tag_products.DIC if tag_products.DIC[k]["concerns"]]))[:60]
    heroes = [k for k in pool if tag_products.DIC[k]["concerns"]][:40]  # 요즘 뜨는 성분부터 대표 성분으로
    ps = []
    for i in range(N):
        h = heroes[i % len(heroes)]
        mild = [k for k in pool if k != h and not tag_products.DIC[k]["strong"] and tag_products.DIC[k]["time"] != "밤"]  # 보조 성분은 순한 것만
        brand = BRANDS[(i + i // len(heroes)) % len(BRANDS)]  # 같은 대표 성분이 다시 나오면 다른 브랜드로 → 이름 중복 없음
        ps.append(fake(i, h, rnd.sample(mild, 2), rnd, brand))
    for p in ps[:3]: p["viral"] = [[ob["last"], next(iter(ob["countries"])), "체험판 예시: 요즘 뜨는 성분이 든 제품"]]
    return ps

def page():
    html = open(os.path.join(app, "index.html"), encoding="utf-8").read()
    html = html.replace("<title>오프뷰티 추천 찾기</title>\n", "")  # 제목은 head 안으로 옮김
    meta = (f'<title>오프뷰티 추천 찾기 체험판</title><meta name="description" content="{DESC}">'
            f'<meta property="og:type" content="website"><meta property="og:url" content="{SITE}"><meta property="og:title" content="오프뷰티 추천 찾기 체험판">'
            f'<meta property="og:description" content="{DESC}"><meta property="og:image" content="{SITE}og.png"><meta property="og:image:width" content="1200">'
            '<meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image">')
    head = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">' + meta +
            '<link rel="manifest" href="manifest.json"><meta name="theme-color" content="#0E7A6B"><link rel="apple-touch-icon" href="icon-192.png">'
            '<meta name="apple-mobile-web-app-capable" content="yes"></head><body>\n')
    sw = "<script>if('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js');</script>\n"
    note = '<p class="demo">체험판이에요. 제품 이름·진열 위치·가격은 예시 값이고, 성분 설명과 트렌드는 실제 데이터예요.</p>\n'
    return head + html.replace('<main class="wrap">', '<main class="wrap">\n' + note, 1) + sw + "</body></html>\n"

if __name__ == "__main__":
    js = open(os.path.join(app, "data.js"), encoding="utf-8").read()
    ob = json.loads(js[js.index("=") + 1:].strip().rstrip(";"))
    ob["products"] = products(ob, random.Random(7))
    for f in os.listdir(out):  # 지난 화면 파일 정리 (설치용 파일은 남김)
        fp = os.path.join(out, f)
        if f not in KEEP: shutil.rmtree(fp) if os.path.isdir(fp) else os.remove(fp)
    for f in os.listdir(app):
        if f not in ("data.js", "index.html", "gate.js"): shutil.copy(os.path.join(app, f), out)
    data = "window.OB = " + json.dumps(ob, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";\n"
    open(os.path.join(out, "data.js"), "w", encoding="utf-8").write(data)
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page())
    print("체험판 완료:", len(ob["products"]), "개 예시 제품 →", out)
