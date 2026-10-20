# 사용법: python3 check.py → app/data.js 가 정상인지 점검. 문제가 있으면 이유를 출력하고 실패(종료 코드 1)
import json, os, sys, datetime
here = os.path.dirname(os.path.abspath(__file__))
MIN_PRODUCTS, MIN_DICT, MAX_AGE_DAYS = 400, 50, 3  # 지금 제품 503개, 성분 210개

def load():
    js = open(os.path.join(here, "app", "data.js"), encoding="utf-8").read()
    head, tail = "window.OB = ", ";\n"
    if not (js.startswith(head) and js.endswith(tail)): raise ValueError("data.js 형식이 깨짐")
    return json.loads(js[len(head):-len(tail)])

def problems(ob, today):
    out = []
    if len(ob["products"]) < MIN_PRODUCTS: out.append(f"제품이 {len(ob['products'])}개뿐 (최소 {MIN_PRODUCTS})")
    if len(ob["dict"]) < MIN_DICT: out.append(f"성분 사전이 {len(ob['dict'])}개뿐")
    if not ob["feed"]: out.append("트렌드 카드가 없음")
    if [p["id"] for p in ob["products"] if not p.get("loc", {}).get("badge")]: out.append("위치 없는 제품이 있음")
    if [i for p in ob["products"] if isinstance(p["ingredients"], list) for i in p["ingredients"] if i not in ob["dict"]]:
        out.append("사전에 없는 성분을 쓰는 제품이 있음")
    age = (today - datetime.date.fromisoformat(ob["last"])).days
    if age > MAX_AGE_DAYS: out.append(f"트렌드가 {age}일 전 것 (최근 {MAX_AGE_DAYS}일 안이어야 함)")
    return out

if __name__ == "__main__":
    try: bad = problems(load(), datetime.date.today())
    except Exception as e: bad = [f"읽기 실패: {e}"]
    print("점검 통과" if not bad else "점검 실패: " + " / ".join(bad))
    sys.exit(1 if bad else 0)
