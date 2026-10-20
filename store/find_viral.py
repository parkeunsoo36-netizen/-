# 트렌드 데이터(../data/*.json)에서 우리 매장 제품이 언급된 것을 찾는다 (브랜드 + 제품 고유 단어가 같이 나와야 인정)
# make_page_data.py 가 불러 씀. 브랜드 영어 이름은 viral_brands.json
import json, glob, os, re
here = os.path.dirname(os.path.abspath(__file__))
ALIAS = json.load(open(os.path.join(here, "viral_brands.json"), encoding="utf-8"))
GENERIC = set(("크림 세럼 앰플 토너 패드 마스크 마스크팩 에센스 선크림 클렌저 클렌징 폼 오일 젤 로션 미스트 시트 "
               "대용량 기획 세트 리필 증정 더블 플러스 리얼 퍼펙트 수분 진정 미백 앤 오리지널 스킨 케어 립 아이 "
               "시카 각질 칼슘 콜라겐 비타민 히알루론 2스텝 하이드로겔 리프팅 데일리").split())

def text(it):
    return " ".join([it["t"], it["why"], it.get("q", "")] + [v["title"] for v in it.get("vid", [])])

def keywords(name):  # 상품명에서 브랜드·용량·흔한 말을 뺀 고유 단어
    name = re.sub(r"\(.*?\)|\d+(\.\d+)?\s*(ml|g|매입|매|개입|ea|개|종)\b", " ", name, flags=re.I)
    return [w for w in name.split()[1:] if len(w) >= 2 and w not in GENERIC and not re.fullmatch(r"[\d+*x%.A-Za-z]{1,4}", w)]

def brand_in(brand, t):
    return brand in t or any(re.search(r"(^|[^a-z])" + re.escape(a) + r"($|[^a-z])", t.lower()) for a in ALIAS.get(brand, []))

def is_hit(p, t):
    if not brand_in(p["brand"], t): return False
    flat = t.replace(" ", "")
    hit = [w for w in keywords(p["name"]) if w in flat]
    return len(hit) >= 2 or any(len(w) >= 3 for w in hit)  # 2글자 단어 하나만 맞으면 우연일 수 있어서 제외

def viral(products, items):  # {상품코드: [(날짜, 나라, 트렌드 제목), ...]}
    out = {}
    for p in products:
        hits = [(it["_d"], it["c"], it["t"]) for it in items if is_hit(p, text(it))]
        if hits: out[p["id"]] = sorted(hits, reverse=True)
    return out
