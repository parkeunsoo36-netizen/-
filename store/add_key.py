# 사용법: python3 add_key.py 상품코드끝6자리 "성분id,성분id" 출처URL → key_ingredients.json 에 기록 (웹에서 확인한 주요 성분)
import json, sys, os
here = os.path.dirname(os.path.abspath(__file__))
kp, pp = os.path.join(here, "key_ingredients.json"), os.path.join(here, "products.json")
key, ids = json.load(open(kp, encoding="utf-8")), {p["id"] for p in json.load(open(pp, encoding="utf-8"))}
dic = json.load(open(os.path.join(here, "ingredient_dict.json"), encoding="utf-8"))
for tail, ings, src in zip(*[iter(sys.argv[1:])] * 3):
    code = next(i for i in ids if i.endswith(tail))
    bad = [i for i in ings.split(",") if i not in dic]
    if bad: print("사전에 없음", tail, bad); continue
    key[code] = {"ing": ings.split(","), "src": src}
json.dump(key, open(kp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(key), "개 기록")
