# 사용법: python3 make_dicts.py → ../ingredients.json 을 성분 사전(ingredient_dict.json)과 동의어 사전(synonyms.json)으로 정리
import json, re, os
here = os.path.dirname(os.path.abspath(__file__))
src = json.load(open(os.path.join(here, "..", "ingredients.json"), encoding="utf-8"))
DROP = {"exosome", "teca", "complex", "fish", "plant", "low", "molecular", "peptide", "ferment", "lysate"}
CONCERN = {"잡티·미백": "잡티|미백|톤|기미|색소|광채|칙칙", "여드름": "여드름|트러블|뾰루지|acne",
           "모공·피지": "모공|피지|블랙헤드|각질", "민감·진정": "진정|민감|붉|홍조|자극|장벽",
           "보습·건조": "보습|건조|수분|당김", "노화·탄력": "주름|탄력|노화|안티에이징|리프팅",
           "자외선": "자외선|선크림|UV", "다크서클·눈가": "눈가|다크서클|붓기"}
STRONG = {"retinol", "retinal", "hpr", "glycolic acid", "lactic acid", "mandelic acid", "salicylic acid", "lha", "azelaic acid"}
NIGHT = STRONG | {"bakuchiol"}  # 밤 사용 권장 성분
NAME = {"peptide": "펩타이드", "centella": "병풀(시카)", "collagen": "콜라겐", "hyaluronic acid": "히알루론산", "ceramide": "세라마이드",
        "vitamin c": "비타민C", "probiotics": "유산균", "egf": "EGF", "pdrn": "PDRN", "copper": "구리펩타이드", "argireline": "아르지렐린"}
SEBUM = {"salicylic acid", "lha", "zinc pca", "zinc", "kaolin clay", "bentonite clay", "betaine salicylate", "tea tree oil", "volcanic ash", "charcoal"}
SKIN_HINT = {  # 성분 → 잘 맞는 피부 타입 (제품 피부 타입 계산용)
    "지성·복합성": SEBUM | {"niacinamide", "tea tree", "heartleaf", "pha", "green tea", "silica", "witch hazel"},
    "건성·수부지": {"hyaluronic acid", "ceramide", "squalane", "shea butter", "panthenol", "urea", "honey", "collagen", "petroleum jelly",
                 "snail mucin", "beta-glucan", "polyglutamic acid", "trehalose", "bird's nest", "jellyfish collagen", "cholesterol"},
    "민감성": {"centella", "madecassoside", "asiaticoside", "panthenol", "allantoin", "aloe vera", "mugwort", "chamomile", "azulene",
            "heartleaf", "oat extract", "ectoin", "bisabolol", "ceramide"}}

def fam(nm):  # build.py 와 같은 규칙: 변형 성분은 한 가족으로 묶음
    s = re.sub(r"\(.*?\)", "", nm.lower()).strip()
    return " ".join(w for w in s.split() if w not in DROP) or s

def concerns(text):
    return [c for c, pat in CONCERN.items() if re.search(pat, text, re.I)]

def short_ko(names):  # 목록에 쓸 짧은 이름: 괄호 뺀 가장 짧은 한글 이름
    return min((re.sub(r"\(.*?\)", "", n).strip() for n in names), key=len)

NEW = {  # ingredients.json 에 없는데 매장 상품명에 나오는 성분
    "idebenone": ("이데베논", "강력한 항산화 성분, 탄력·광노화 케어", "칙칙하고 탄력 떨어진 피부", "strong antioxidant for firmer, brighter skin", ""),
    "pearl": ("진주 추출물", "광채·톤 개선", "칙칙한 톤", "adds glow and evens tone", ""),
    "bee venom": ("봉독", "탄력·진정 케어", "탄력 저하·트러블 피부", "firms and soothes", "벌 알레르기 있으면 피하기"),
    "charcoal": ("숯", "피지·노폐물 흡착", "지성·모공 고민", "absorbs oil and impurities", "건성은 자주 쓰지 않기"),
    "bird's nest": ("제비집 추출물", "영양·보습, 탄력", "건조·탄력 저하 피부", "nourishes and hydrates", ""),
    "ferulic acid": ("페룰릭애씨드", "비타민C와 함께 쓰는 항산화, 톤 개선", "잡티·광노화", "antioxidant that boosts vitamin C", "낮엔 선크림 함께"),
    "lingzhi": ("영지버섯 추출물", "진정·영양", "지친·민감 피부", "soothes and nourishes", ""),
    "jellyfish collagen": ("해파리 추출물", "수분·탄력", "건조 피부", "hydrates and plumps", ""),
}

def build():
    dic = {k: {"ko": [v[0]], "inci": [], "fx": v[1], "good": v[2], "en": v[3], "caution": v[4]} for k, v in NEW.items()}
    for inci, v in src.items():
        e = dic.setdefault(fam(v["nm"]), {"ko": [], "inci": [], "fx": v["fx"], "good": v["good"], "en": v["en"], "caution": v["tip"]})
        e["ko"].append(v["ko"]); e["inci"].append(inci)
    for k, e in dic.items():
        e["name"] = NAME.get(k) or short_ko(e["ko"])
        e["time"] = "밤" if k in NIGHT else "상관없음"
        e["concerns"] = concerns(e["fx"] + " " + e["good"])
        e["strong"] = k in STRONG      # 민감성 경고용
        e["sebum"] = k in SEBUM        # 건성 순위 낮춤용
        e["skin"] = [t for g, ks in SKIN_HINT.items() if k in ks for t in g.split("·")]
        e["ko"], e["inci"] = sorted(set(e["ko"])), sorted(set(e["inci"]))
    return dic

EXTRA_ING = {  # 오타·줄임말·묶음 이름 → 성분 사전 id (여러 개면 묶음)
    "펩타이드": ["peptide"], "펩타민": ["peptide"], "펩티드": ["peptide"], "peptide": ["peptide"],
    "나이아신": ["niacinamide"], "나이아신 아마이드": ["niacinamide"], "니아신아마이드": ["niacinamide"], "나이아신아미드": ["niacinamide"],
    "비타민c": ["vitamin c", "ethyl ascorbic acid"], "비타c": ["vitamin c"], "vit c": ["vitamin c"], "비씨": ["vitamin c"],
    "시카": ["centella"], "센텔라": ["centella"], "그린티": ["green tea"], "녹차": ["green tea"], "cica": ["centella"], "병풀": ["centella"], "마데카": ["madecassoside"],
    "피디알엔": ["pdrn"], "연어": ["pdrn"], "레티노이드": ["retinol", "retinal", "hpr"], "레티날": ["retinal"],
    "aha": ["glycolic acid", "lactic acid", "mandelic acid"], "bha": ["salicylic acid", "betaine salicylate"], "pha": ["pha", "lactobionic acid"],
    "트라넥삼산": ["tranexamic acid"], "txa": ["tranexamic acid"], "히알루론": ["hyaluronic acid"], "히알루": ["hyaluronic acid"],
    "세라": ["ceramide"], "달팽이": ["snail mucin"], "스네일": ["snail mucin"], "티트리": ["tea tree", "tea tree oil"],
    "어성초": ["heartleaf"], "도쿠다미": ["heartleaf"], "쑥": ["mugwort"], "알부틴": ["alpha arbutin", "arbutin"],
    "비타민": ["vitamins"], "비타 씨": ["vitamin c"], "비타-라이트": ["vitamin c"], "비타민-c": ["vitamin c"], "vc": ["vitamin c"], "아세로라": ["vitamin c"],
    "청귤": ["green tangerine"], "유자": ["yuja"], "알로에": ["aloe vera"], "꿀": ["honey"], "허니": ["honey"], "라이스": ["rice extract"], "쌀": ["rice extract"],
    "홍삼": ["korean red ginseng"], "인삼": ["ginseng"], "캐비어": ["caviar extract"], "석류": ["pomegranate"], "머그워트": ["mugwort"], "노니": ["noni fruit"],
    "판테톨": ["panthenol"], "바세린": ["petroleum jelly"], "리들샷": ["spicule"], "스피큘": ["spicule"], "니들샷": ["spicule"], "징크": ["zinc"], "칼슘": ["calcium"],
    "레티-에이": ["retinol"], "레티 ": ["retinol"], "니코틴아마이드": ["niacinamide"], "비타민 b3": ["niacinamide"], "아줄렌": ["azulene"], "카모마일": ["chamomile"], "캐모마일": ["chamomile"],
    "로즈마리": ["rosemary"], "라벤더": ["lavender oil"], "트러플": ["truffle"], "말차": ["green tea"], "히알": ["hyaluronic acid"], "프로폴리스": ["propolis"], "폴리스": ["propolis"],
    "이데베논": ["idebenone"], "진주": ["pearl"], "봉독": ["bee venom"], "숯": ["charcoal"], "제비집": ["bird's nest"], "버드 네스트": ["bird's nest"], "페룰릭": ["ferulic acid"],
    "영지": ["lingzhi"], "젤리피쉬": ["jellyfish collagen"], "콩 단백질": ["soybean"], "마이크로바이옴": ["probiotics"], "바이옴": ["probiotics"], "pdrn": ["pdrn"], "egf": ["egf"], "이지에프": ["egf"], "티엑스": ["tranexamic acid"],
    "글루타치온": ["glutathione"], "콜라겐": ["collagen"], "판테놀": ["panthenol"], "프로폴리스": ["propolis"],
}
CONCERN_SYN = {"잡티·미백": "잡티 미백 기미 주근깨 색소 톤업 칙칙 다크스팟 dark spot brightening whitening 美白 シミ",
               "여드름": "여드름 트러블 뾰루지 좁쌀 acne pimple breakout 痘痘 ニキビ",
               "모공·피지": "모공 피지 블랙헤드 화이트헤드 번들 유분 pore sebum blackhead 毛孔 毛穴",
               "민감·진정": "민감 진정 홍조 붉은기 자극 장벽 따가움 sensitive redness calming 敏感 敏感肌",
               "보습·건조": "보습 건조 수분 속건조 당김 각질 dry hydrating moisture 保湿 乾燥",
               "노화·탄력": "노화 탄력 주름 처짐 리프팅 안티에이징 wrinkle anti-aging firming 抗老 しわ",
               "자외선": "자외선 선크림 선블록 썬 sunscreen spf uv 防晒 日焼け止め",
               "다크서클·눈가": "다크서클 눈가 눈밑 붓기 아이크림 dark circle eye"}
SKIN_SYN = {"지성": "지성 기름 번들 oily 油性", "건성": "건성 건조피부 dry 干性", "수부지": "수부지 속건조 수분부족지성 dehydrated",
            "복합성": "복합성 복합 combination 混合", "민감성": "민감성 예민 sensitive 敏感肌", "중성": "중성 보통 normal"}
FORM_SYN = {"크림": "크림 cream 수분크림 balm", "세럼앰플": "세럼 앰플 에센스 serum ampoule essence 精华",
            "토너": "토너 스킨 toner 化妆水", "패드": "패드 pad 토너패드", "팩마스크": "팩 마스크 마스크팩 시트 패치 mask sheet 面膜 パック",
            "선케어": "선크림 선스틱 선세럼 sunscreen sun", "클렌저": "클렌저 클렌징 폼 오일 cleanser cleansing 洗面奶"}
TIME_SYN = {"아침": "아침 낮 데이 morning day 早上", "밤": "밤 저녁 나이트 자기전 수면 night sleeping 晚上 夜"}

def words(table):
    return {w.lower(): k for k, ws in table.items() for w in ws.split()}

def ing_synonyms(dic):
    syn = {}
    for k, e in dic.items():
        names = [k] + e["inci"] + e["ko"] + [re.sub(r"\(.*?\)", "", n).strip() for n in e["ko"]]
        for n in names: syn.setdefault(n.lower(), []).append(k) if k not in syn.get(n.lower(), []) else None
    for w, ids in EXTRA_ING.items(): syn[w.lower()] = [i for i in ids if i in dic]
    return syn

if __name__ == "__main__":
    dic = build()
    syn = {"ingredient": ing_synonyms(dic), "concern": words(CONCERN_SYN), "skin": words(SKIN_SYN),
           "form": words(FORM_SYN), "time": words(TIME_SYN)}
    json.dump(dic, open(os.path.join(here, "ingredient_dict.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(syn, open(os.path.join(here, "synonyms.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(dic), "성분,", len(syn["ingredient"]), "성분 검색어")
