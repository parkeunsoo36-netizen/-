# 사용법: python3 apply_manual.py → manual/직접입력.csv 에 적은 성분·전성분·사진을 products.json 에 반영 (웹 조사보다 우선)
# 주요 성분은 한글·영어 아무거나 쉼표로 (예: 나이아신아마이드, 병풀, retinol). 사전에 없는 말은 알려주고 건너뜀
import csv, json, os
here = os.path.dirname(os.path.abspath(__file__))
pp = os.path.join(here, "products.json")
SYN = json.load(open(os.path.join(here, "synonyms.json"), encoding="utf-8"))["ingredient"]

def to_ids(text):
    ids, unknown = set(), []
    for w in [x.strip() for x in text.replace("/", ",").split(",") if x.strip()]:
        hit = SYN.get(w) or SYN.get(w.lower()) or SYN.get(w.replace(" ", ""))
        ids.update(hit) if hit else unknown.append(w)
    return sorted(ids), unknown

def apply(p, r):
    ids, unknown = to_ids(r["주요 성분"] + "," + r["전성분"])
    if ids: p["ingredients"], p["ingredients_from"] = ids, "직접 입력"
    if r["전성분"].strip(): p["full_inci"] = r["전성분"].strip()
    if r["사진"].strip(): p["photo"] = r["사진"].strip()
    return unknown

if __name__ == "__main__":
    ps = json.load(open(pp, encoding="utf-8"))
    by = {p["id"]: p for p in ps}
    rows = [r for r in csv.DictReader(open(os.path.join(here, "manual", "직접입력.csv"), encoding="utf-8-sig"))
            if r["상품코드"] in by and (r["주요 성분"] + r["전성분"] + r["사진"]).strip()]
    for r in rows:
        unknown = apply(by[r["상품코드"]], r)
        if unknown: print(r["상품명"], "→ 사전에 없는 말:", ", ".join(unknown))
    json.dump(ps, open(pp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(rows), "개 제품에 직접 입력 반영")
