# 사용법: python3 fetch_stats.py → 최근 14일 트렌드 영상의 조회수·좋아요·댓글 수를 유튜브에서 받아 video_stats.json 에 저장
# 유튜브 Data API videos.list(무료, 50개당 1 할당량). 키는 환경이 넣어 줌. 저장·공유 수는 유튜브가 공개하지 않아 못 받음
import json, glob, os, re, datetime, urllib.request
here = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(here, "video_stats.json")
API = "https://www.googleapis.com/youtube/v3/videos?part=statistics&maxResults=50&id="

def video_ids():
    ids = set()
    for f in sorted(glob.glob(os.path.join(here, "..", "data", "*.json")))[-14:]:
        for it in json.load(open(f, encoding="utf-8")).get("items", []):
            for v in it.get("vid", []):
                m = re.search(r"(?:v=|youtu\.be/|shorts/)([\w-]{11})", v.get("url", ""))
                if m: ids.add(m.group(1))
    return sorted(ids)

def fetch(batch):
    with urllib.request.urlopen(API + ",".join(batch), timeout=30) as r:
        items = json.load(r).get("items", [])
    num = lambda s, k: int(s.get(k, 0))
    return {it["id"]: {"views": num(it["statistics"], "viewCount"), "likes": num(it["statistics"], "likeCount"),
                       "comments": num(it["statistics"], "commentCount")} for it in items}

if __name__ == "__main__":
    ids, stats, used = video_ids(), {}, 0
    for i in range(0, len(ids), 50):
        try: stats.update(fetch(ids[i:i + 50])); used += 1
        except Exception as e: print("멈춤:", e); break  # 할당량·오류면 받은 것까지만 저장
    old = json.load(open(out, encoding="utf-8")) if os.path.exists(out) else {}
    old.update(stats)
    json.dump({"_date": datetime.date.today().isoformat(), **{k: v for k, v in old.items() if k != "_date"}}, open(out, "w", encoding="utf-8"))
    print(len(ids), "개 영상 중", len(stats), "개 받음, 할당량", used, "사용")
