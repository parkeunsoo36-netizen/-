# 사용법: python3 excel_to_products.py 진열안.xlsx → products.json (엑셀에 없는 칸은 "미확인")
import json, re, sys, os
import openpyxl
here = os.path.dirname(os.path.abspath(__file__))
ZONE = {"스킨케어 1차": "A", "스킨케어 2차": "B", "색조": "C", "선클렌징": "D", "마스크팩": "E", "헤어바디": "F", "건기식": "G"}
FORM = [("팩마스크", "마스크|팩|패치"), ("선케어", r"선 ?크림|선 ?스틱|선 ?세럼|(^|\s)선(\s|$)|썬|SPF"), ("클렌저", "클렌|폼|워시"),
        ("패드", "패드"), ("토너", "토너|스킨|미스트|자음수"), ("세럼앰플", "세럼|앰플|에센스|샷|스팟|엘릭서"), ("크림", "크림|밤|로션|에멀젼|유액|수딩젤")]
SYN = json.load(open(os.path.join(here, "synonyms.json"), encoding="utf-8"))["ingredient"]
UNK = "미확인"
KEY = json.load(open(os.path.join(here, "key_ingredients.json"), encoding="utf-8"))  # 웹에서 확인한 주요 성분 {상품코드: {ing, src}}

def split_name(raw):  # "[%][닥터스초이스]닥터멜락신 티엑스 크림" → 표시, 이름, 브랜드
    tags = re.findall(r"\[([^\]]*)\]", raw)
    name = re.sub(r"\[[^\]]*\]", "", raw).strip()
    return tags, name, name.split()[0] if name else UNK

def guess_form(name, zone):
    if zone in "FG": return "기타"
    if re.search(r"세트|키트|\d종", name): return "세트"  # 여러 제형 묶음
    for f in ("선케어", "클렌저"):  # "선크림"·"클렌징밤"은 뒤 단어(크림·밤)보다 이쪽이 우선
        if re.search(dict(FORM)[f], name, re.I): return f
    hits = [(m.start(), f) for f, pat in FORM for m in re.finditer(pat, name, re.I)]
    return max(hits)[1] if hits else UNK  # 상품명 맨 뒤쪽 제형 단어가 실제 제형

SKIP = {"eye", "hair", "sugar", "calcium", "protein"}  # 상품명에선 성분 뜻이 아닌 영어 단어

def name_hit(w, low):
    if w in SKIP: return False
    if w.isascii(): return len(w) >= 3 and re.search(rf"(?<![a-z]){re.escape(w)}(?![a-z])", low)
    return w in low

def name_ingredients(name):  # 상품명에 적힌 성분만(추측 아님)
    low = name.lower()
    hits = {i for w, ids in SYN.items() if name_hit(w, low) for i in ids}
    return sorted(hits)

def location(zone, rack, tier, slot):
    return {"floor": "1F", "zone": zone, "rack": str(rack), "tier": tier, "slot": slot, "badge": f"1F {zone}-{rack}" + (str(tier) if isinstance(rack, str) else "")}

def product(zone, r):
    rack, tier, slot, rank, code, raw, price = r[:7]
    tags, name, brand = split_name(str(raw))
    ing, web = name_ingredients(name), KEY.get(str(code), {})
    allv = sorted(set(ing) | set(web.get("ing", [])))
    return {"id": str(code), "name": name, "brand": brand, "form": guess_form(name, zone), "price": price,
            "ingredients": allv or UNK, "ingredients_from": web.get("src") or ("상품명" if ing else UNK), "full_inci": UNK,
            "concerns": UNK, "skin": UNK, "time": UNK, "loc": location(zone, rack, tier, slot),
            "photo": UNK, "rank": rank, "tags": tags}

def read(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    out = []
    for ws in wb.worksheets[1:]:
        zone = ZONE.get(ws.title, "?")
        out += [product(zone, r) for r in ws.iter_rows(min_row=3, values_only=True) if r[4] and r[4] != "상품코드"]
    return out

if __name__ == "__main__":
    ps = read(sys.argv[1])
    json.dump(ps, open(os.path.join(here, "products.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(ps), "제품")
