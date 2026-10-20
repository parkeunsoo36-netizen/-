# 사용법: python3 tag_products.py → products.json 의 고민·피부 타입·사용 시간을 성분 사전으로 계산 (성분 미확인이면 미확인)
import json, re, os
here = os.path.dirname(os.path.abspath(__file__))
pp = os.path.join(here, "products.json")
DIC = json.load(open(os.path.join(here, "ingredient_dict.json"), encoding="utf-8"))
UNK = "미확인"

def concerns(ings):
    return sorted({c for i in ings for c in DIC[i]["concerns"]}) or UNK

def skin(ings):
    s = {t for i in ings for t in DIC[i]["skin"]}
    if any(DIC[i]["strong"] for i in ings): s.discard("민감성")  # 강한 각질·레티놀 성분은 민감성 추천 안 함
    return sorted(s | {"중성"}) if s else UNK

def time(p, ings):
    if re.search(r"슬리핑|나이트|수면", p["name"]) or any(DIC[i]["time"] == "밤" for i in ings): return "밤"
    if p["form"] == "선케어" or re.search(r"톤업|데이", p["name"]): return "아침"
    return "상관없음" if ings else UNK

def tag(p):
    ings = p["ingredients"] if isinstance(p["ingredients"], list) else []
    p["concerns"], p["skin"] = (concerns(ings), skin(ings)) if ings else (UNK, UNK)
    p["time"] = time(p, ings)
    for c, pat in (("자외선", "^선케어 "), ("다크서클·눈가", "아이 ?크림|아이 ?패치|아이백|눈가|다크서클|아이존")):  # 상품명·제형에 적힌 고민
        if re.search(pat, p["form"] + " " + p["name"]):
            p["concerns"] = sorted(set([] if p["concerns"] == UNK else p["concerns"]) | {c})
    p["warn"] = sorted(DIC[i]["name"] for i in ings if DIC[i]["strong"])  # 민감성 손님 ⚠️ 표시용
    p["sebum"] = any(DIC[i]["sebum"] for i in ings)                      # 건성 손님 순위 낮춤용
    return p

if __name__ == "__main__":
    ps = [tag(p) for p in json.load(open(pp, encoding="utf-8"))]
    json.dump(ps, open(pp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(ps), "제품, 고민 계산", sum(p["concerns"] != UNK for p in ps), "개")
