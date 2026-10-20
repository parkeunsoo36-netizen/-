# 추천 찾기 (매장 직원용)

손님이 말한 고민·제품을 듣고 **필요한 성분 → 매장 제품 → 진열 위치 → 설명**까지 3번 터치 안에 찾는 페이지입니다.
매일 아침 유튜브 트렌드를 반영해 최근 뜨는 성분과 바이럴 제품을 위로 올립니다.

> 매장 진열 위치·가격·상품 목록은 비공개라 이 저장소에 없습니다(`.gitignore`).
> `app/data.js`, `products.json` 등은 비공개 작업 공간에서만 만들어집니다.

## 화면 (`app/`, 순수 HTML/CSS/JS)
| 파일 | 하는 일 |
|---|---|
| `index.html` / `style.css` | 화면 틀과 디자인 (탭 3개: 추천 찾기 · 성분 사전 · 트렌드) |
| `query.js` | 검색어를 고민·피부·제형·시간·성분으로 해석 (동의어 사전 사용) |
| `score.js` | 적합도 = 고민×3 + 피부×2 + 제형×2 + 시간×1 + 국가 트렌드×1, 바이럴 제품 상단 |
| `view.js` / `card.js` | 결과 요약, 추천 성분 카드, 제품 카드(위치 박스) |
| `sheet.js` / `product.js` | 성분·제품 설명 바텀시트 (한국어/영어) |
| `trend.js` | 나라별 인기 TOP 10 (조회수·좋아요·댓글 종합) |
| `dict.js` | 성분 사전 검색 |
| `main.js` | 상태 관리와 탭 전환 |

## 데이터 만들기 (Python)
순서대로 실행: `make_dicts.py` → `excel_to_products.py <진열안.xlsx>` → `apply_manual.py` → `tag_products.py` → `fetch_stats.py` → `make_page_data.py`

| 파일 | 하는 일 |
|---|---|
| `make_dicts.py` | 성분 사전(`ingredient_dict.json`)과 동의어 사전(`synonyms.json`) 생성 |
| `excel_to_products.py` | 매장 진열 엑셀 → `products.json` (확인 못 한 칸은 "미확인") |
| `add_key.py` / `apply_manual.py` | 웹에서 확인한 주요 성분, 직접 입력한 성분 반영 |
| `tag_products.py` | 성분으로 고민·피부 타입·사용 시간·주의 표시 계산 |
| `fetch_stats.py` | 유튜브 영상 조회수·좋아요·댓글 갱신 (무료 할당량 안에서) |
| `find_viral.py` / `viral_brands.json` | 트렌드 영상에 나온 매장 제품 찾기 (인기급상승) |
| `trend_feed.py` | 트렌드 카드와 인기 점수 계산 |
| `make_page_data.py` | 위 결과를 `app/data.js` 하나로 묶음 |

`manual/직접입력.csv`는 빈 양식입니다(사용법은 `manual/README.md`).
