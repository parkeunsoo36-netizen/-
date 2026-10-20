# 사용법: python3 rebuild.py            → 매일: 새 트렌드로 app/data.js 만들고 점검
#        python3 rebuild.py 진열안.xlsx → 매장 진열이 바뀐 날: 제품 목록부터 전부 다시 만들고 점검
# 점검에 실패하면 어제 data.js 로 되돌리고 실패(종료 코드 1) → 그날은 페이지를 다시 올리지 않음
import os, shutil, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(here, "app", "data.js")
PREV = os.path.join(here, "data.prev.js")  # 어제 것 백업은 app/ 밖에 둠 (페이지에 같이 올라가지 않게)

def steps(excel):
    full = [["make_dicts.py"], ["excel_to_products.py", excel], ["apply_manual.py"], ["tag_products.py"]] if excel else []
    return full + [["make_page_data.py"], ["check.py"]]

def run(step):
    print("▶", " ".join(step), flush=True)
    return subprocess.run([sys.executable, os.path.join(here, step[0]), *step[1:]], cwd=here).returncode == 0

def main(excel=None):
    if os.path.exists(DATA): shutil.copy(DATA, PREV)
    for step in steps(excel):
        if run(step): continue
        if os.path.exists(PREV): shutil.copy(PREV, DATA)
        print(f"멈춤: {step[0]} 에서 실패 → 어제 data.js 로 되돌림. 오늘은 페이지를 다시 올리지 마세요.")
        return 1
    print("완료: 새 data.js 준비됨")
    return 0

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:2]))
