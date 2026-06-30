"""
산단 정착 AI — 외국인 근로자 다국어 정착 지원 챗봇
2026 산업통상부 공공데이터 활용 아이디어 공모전

실행 방법:
1. pip install streamlit google-generativeai folium streamlit-folium
2. 아래 GEMINI_API_KEY 자리에 본인 키 입력 (AIza...로 시작)
3. python -m streamlit run app_gemini_v2.py
"""

import streamlit as st
import json
import os
import folium
from streamlit_folium import st_folium
import google.generativeai as genai

# ────────────────────────────────────────────
# 0. API 키 설정
# ────────────────────────────────────────────
# 우선순위: 1) Streamlit secrets (Streamlit Cloud 배포용)
#           2) 환경변수 (로컬 개발용)
GEMINI_API_KEY = ""

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ────────────────────────────────────────────
# 1. 페이지 설정
# ────────────────────────────────────────────
st.set_page_config(
    page_title="산단 정착 AI",
    page_icon="🏭",
    layout="wide"
)

# ────────────────────────────────────────────
# 2. 지식베이스 로드
# ────────────────────────────────────────────
@st.cache_data
def load_knowledge_base():
    path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

kb = load_knowledge_base()

# ────────────────────────────────────────────
# 3. 기관 좌표 데이터
# ────────────────────────────────────────────
# 외국인 지원센터 좌표
SUPPORT_CENTER_COORDS = {
    "안산시외국인주민상담지원센터": {"위도": 37.3199, "경도": 126.8319},
    "안산시다문화가족지원센터":      {"위도": 37.3180, "경도": 126.8350},
    "화성시외국인복지센터":          {"위도": 37.0780, "경도": 126.9490},
    "평택외국인복지센터":            {"위도": 36.9921, "경도": 127.1127},
    "아산시 가족센터":               {"위도": 36.7890, "경도": 127.0040},
    "천안시다문화가족지원센터":      {"위도": 36.8050, "경도": 127.1440},
    "김해시가족센터":                {"위도": 35.2280, "경도": 128.8810},
}

# 병원 좌표
HOSPITAL_COORDS = {
    "근로복지공단 안산병원":       {"위도": 37.3211, "경도": 126.8295},
    "고려대학교 안산병원":         {"위도": 37.3155, "경도": 126.8520},
    "화성중앙종합병원":            {"위도": 37.0760, "경도": 126.9530},
    "평택성모병원":                {"위도": 36.9870, "경도": 127.0890},
    "아산충무병원":                {"위도": 36.7920, "경도": 127.0030},
    "순천향대학교 부속 천안병원":  {"위도": 36.8110, "경도": 127.1130},
    "천안의료원":                  {"위도": 36.8060, "경도": 127.1520},
    "김해신세계의원":              {"위도": 35.2240, "경도": 128.8890},
}

# 출입국관서 좌표
IMMIGRATION_COORDS = {
    "안산출입국·외국인사무소":              {"위도": 37.3175, "경도": 126.8270},
    "수원출입국·외국인청 (화성 관할)":      {"위도": 37.2636, "경도": 127.0286},
    "수원출입국·외국인청 평택출장소":       {"위도": 36.9940, "경도": 127.0930},
    "대전출입국·외국인사무소 (아산 관할)":  {"위도": 36.3219, "경도": 127.4180},
    "대전출입국·외국인사무소 천안출장소":   {"위도": 36.8090, "경도": 127.1480},
}

# 산단 좌표 (전체 - 지도 탭용)
SANDAN_COORDS = [
    {"이름": "지사(외국인)",         "시도": "부산", "위도": 35.144534, "경도": 128.825731},
    {"이름": "미음(외국인)",         "시도": "부산", "위도": 35.15,     "경도": 128.879},
    {"이름": "달성차(외국인)",       "시도": "대구", "위도": 35.729694, "경도": 128.454039},
    {"이름": "평동(외국인)",         "시도": "광주", "위도": 35.132211, "경도": 126.768588},
    {"이름": "오성(외국인)",         "시도": "경기", "위도": 37.006,    "경도": 126.984},
    {"이름": "장안첨단(1)(외국인)",  "시도": "경기", "위도": 37.110885, "경도": 126.838894},
    {"이름": "장안첨단(2)(외국인)",  "시도": "경기", "위도": 37.104730, "경도": 126.848824},
    {"이름": "당동(외국인)",         "시도": "경기", "위도": 37.867995, "경도": 126.784348},
    {"이름": "문막반계(외국인)",     "시도": "강원", "위도": 37.298,    "경도": 127.802},
    {"이름": "오창(외국인)",         "시도": "충북", "위도": 36.715,    "경도": 127.424},
    {"이름": "산수(외국인)",         "시도": "충북", "위도": 36.896752, "경도": 127.484698},
    {"이름": "인주(외국인)",         "시도": "충남", "위도": 36.889,    "경도": 126.873},
    {"이름": "천안3(외국인)",        "시도": "충남", "위도": 36.82,     "경도": 127.112},
    {"이름": "천안5(외국인)",        "시도": "충남", "위도": 36.737,    "경도": 127.287},
    {"이름": "탕정(외국인)",         "시도": "충남", "위도": 36.798,    "경도": 127.058},
    {"이름": "송산(외국인)",         "시도": "충남", "위도": 36.974,    "경도": 126.693},
    {"이름": "국가식품클러스터(외국인)", "시도": "전북", "위도": 35.980182, "경도": 127.083259},
    {"이름": "익산제3(외국인)",      "시도": "전북", "위도": 36.02,     "경도": 127.018},
    {"이름": "대불(외국인)",         "시도": "전남", "위도": 34.754,    "경도": 126.444},
    {"이름": "구미4(외국인)",        "시도": "경북", "위도": 36.139,    "경도": 128.44},
    {"이름": "영일만(외국인)",       "시도": "경북", "위도": 36.112,    "경도": 129.429},
    {"이름": "사천(외국인)",         "시도": "경남", "위도": 35.069261, "경도": 128.057250},
]

# ────────────────────────────────────────────
# 4. 산업단지 드롭다운 목록
# ────────────────────────────────────────────
SANDAN_LIST = [
    {"이름": "안산 반월·시화산업단지", "지역": "안산", "시도": "경기도",   "위도": 37.3219, "경도": 126.8309},
    {"이름": "화성 장안첨단산업단지",  "지역": "화성", "시도": "경기도",   "위도": 37.1109, "경도": 126.8389},
    {"이름": "평택 오성산업단지",      "지역": "평택", "시도": "경기도",   "위도": 37.006,  "경도": 126.984},
    {"이름": "아산 인주국가산업단지",  "지역": "아산", "시도": "충청남도", "위도": 36.889,  "경도": 126.873},
    {"이름": "천안 천안3산업단지",     "지역": "천안", "시도": "충청남도", "위도": 36.82,   "경도": 127.112},
    {"이름": "김해 서부산업단지",      "지역": "김해", "시도": "경상남도", "위도": 35.228,  "경도": 128.889},
]

# ────────────────────────────────────────────
# 5. 지원 언어 목록
# ────────────────────────────────────────────
LANG_LIST = [
    {"label": "한국어",                         "code": "ko"},
    {"label": "베트남어 (Tiếng Việt)",          "code": "vi"},
    {"label": "네팔어 (नेपाली)",                "code": "ne"},
    {"label": "인도네시아어 (Bahasa Indonesia)", "code": "id"},
    {"label": "미얀마어 (မြန်မာဘာသာ)",         "code": "my"},
    {"label": "태국어 (ภาษาไทย)",              "code": "th"},
    {"label": "영어 (English)",                 "code": "en"},
]

PLACEHOLDER = {
    "한국어":                         "질문을 입력하세요 (예: 안산 지원센터 어디 있어요?)",
    "베트남어 (Tiếng Việt)":          "Nhập câu hỏi của bạn...",
    "네팔어 (नेपाली)":                "आफ्नो प्रश्न टाइप गर्नुहोस्...",
    "인도네시아어 (Bahasa Indonesia)": "Ketik pertanyaan Anda...",
    "미얀마어 (မြန်မာဘာသာ)":         "သင့်မေးခွန်းကို ရိုက်ထည့်ပါ...",
    "태국어 (ภาษาไทย)":              "พิมพ์คำถามของคุณ...",
    "영어 (English)":                 "Type your question here...",
}

# ────────────────────────────────────────────
# 6. RAG 검색
# ────────────────────────────────────────────
REGION_KEYWORDS = ["안산", "화성", "평택", "아산", "천안", "김해"]

# 키워드는 단순 명사뿐 아니라, 명사가 빠진 채로 자주 들어오는
# 실제 의도 표현(돈/급여/다침/연장 등)까지 포함해서 매칭률을 높임
TOPIC_KEYWORDS = {
    "지원센터": [
        "지원센터", "상담", "외국인센터", "복지센터", "센터", "어디", "도와",
        "문의", "민원", "통역", "상담원", "가까운 곳", "근처에 뭐",
        "support", "center", "help", "trung tâm", "केन्द्र", "pusat", "ဌာန", "ศูนย์"
    ],
    "병원": [
        "병원", "의원", "응급", "산재", "다쳤", "다친", "아파", "아프", "진료", "치료",
        "수술", "사고", "허리", "손가락", "베였", "화상", "약", "응급실",
        "hospital", "doctor", "clinic", "injury", "bệnh viện", "अस्पताल",
        "rumah sakit", "ဆေးရုံ", "โรงพยาบาล"
    ],
    "은행": [
        "은행", "계좌", "통장", "돈", "급여", "월급", "송금", "환전", "체크카드", "카드",
        "월급 받을", "월급 받는", "급여 받을", "급여 계좌",
        "bank", "account", "salary", "wage", "transfer", "ngân hàng",
        "बैंक", "rekening", "ဘဏ်", "ธนาคาร"
    ],
    "출입국": [
        "출입국", "비자", "사증", "체류", "연장", "외국인등록", "등록증", "재발급",
        "만료", "갱신", "기간", "신고",
        "visa", "immigration", "extend", "extension", "expire", "thị thực",
        "भिसा", "imigrasi", "ဗီဇာ", "วีซ่า"
    ],
}

def search_knowledge(query: str, forced_region: str = None):
    found_region = forced_region or next((r for r in REGION_KEYWORDS if r in query), None)
    found_topics = [t for t, kws in TOPIC_KEYWORDS.items() if any(k in query for k in kws)]
    context = {}
    if not found_topics:
        # 어떤 키워드와도 매칭되지 않으면, 가장 기본적인 생활 정보(지원센터·병원)를
        # 기본값으로 제공해 "관련 정보 없음" 대신 최소한의 안내를 보장
        found_topics = ["지원센터", "병원"]
    if "지원센터" in found_topics:
        items = kb["외국인지원센터"]
        if found_region:
            items = [i for i in items if i["지역"] == found_region]
        context["외국인지원센터"] = items
    if "병원" in found_topics:
        items = kb["병원정보"]
        if found_region:
            items = [i for i in items if i["지역"] in [found_region, "전국공통"]]
        context["병원정보"] = items
    if "은행" in found_topics:
        context["은행정보"] = kb["은행정보"]
    if "출입국" in found_topics:
        items = kb["출입국관서"]
        if found_region:
            items = [i for i in items if i["지역"] == found_region]
        context["출입국관서"] = items
    if found_region:
        시도맵 = {"안산":"경기도","화성":"경기도","평택":"경기도",
                  "아산":"충청남도","천안":"충청남도","김해":"경상남도"}
        시도 = 시도맵.get(found_region)
        if 시도:
            시도_stat = [i for i in kb["E9시도별_최신_2026_1Q"] if i["시도"] == 시도]
            if 시도_stat:
                context["지역_E9현황(2026_1Q)"] = 시도_stat
        context["E9_주요국적(전국기준_참고용)"] = kb["E9국적별인원_전국"][:4]
    return context, found_topics

# ────────────────────────────────────────────
# 7. 챗봇 답변 후 인라인 지도 생성
# ────────────────────────────────────────────
def make_inline_map(context: dict, center_lat: float, center_lng: float):
    """답변에 언급된 기관들만 지도에 표시"""
    m = folium.Map(location=[center_lat, center_lng], zoom_start=13, tiles="CartoDB positron")
    has_marker = False

    # 지원센터
    if "외국인지원센터" in context:
        for item in context["외국인지원센터"]:
            name = item.get("기관명", "")
            coords = SUPPORT_CENTER_COORDS.get(name)
            if coords:
                folium.Marker(
                    location=[coords["위도"], coords["경도"]],
                    popup=folium.Popup(
                        f"<b>🏢 {name}</b><br>📍 {item.get('주소','')}<br>📞 {item.get('전화번호','')}",
                        max_width=280
                    ),
                    tooltip=name,
                    icon=folium.Icon(color="green", icon="home", prefix="fa")
                ).add_to(m)
                has_marker = True

    # 병원
    if "병원정보" in context:
        for item in context["병원정보"]:
            name = item.get("기관명", "")
            coords = HOSPITAL_COORDS.get(name)
            if coords:
                folium.Marker(
                    location=[coords["위도"], coords["경도"]],
                    popup=folium.Popup(
                        f"<b>🏥 {name}</b><br>{item.get('분류','')}<br>📞 {item.get('참고','')}",
                        max_width=280
                    ),
                    tooltip=name,
                    icon=folium.Icon(color="red", icon="plus", prefix="fa")
                ).add_to(m)
                has_marker = True

    # 출입국관서
    if "출입국관서" in context:
        for item in context["출입국관서"]:
            name = item.get("기관명", "")
            coords = IMMIGRATION_COORDS.get(name)
            if coords:
                folium.Marker(
                    location=[coords["위도"], coords["경도"]],
                    popup=folium.Popup(
                        f"<b>🏛 {name}</b><br>📍 {item.get('주소','')}<br>📞 {item.get('전화번호','')}",
                        max_width=280
                    ),
                    tooltip=name,
                    icon=folium.Icon(color="blue", icon="building", prefix="fa")
                ).add_to(m)
                has_marker = True

    return m if has_marker else None

# ────────────────────────────────────────────
# 8. 전체 산단 지도 (탭2용)
# ────────────────────────────────────────────
def make_full_map(center_lat: float, center_lng: float, selected_region: str = None):
    m = folium.Map(location=[center_lat, center_lng], zoom_start=7, tiles="CartoDB positron")
    for s in SANDAN_COORDS:
        folium.CircleMarker(
            location=[s["위도"], s["경도"]],
            radius=7,
            color="blue", fill=True, fill_color="blue", fill_opacity=0.7,
            popup=folium.Popup(f"<b>🏭 {s['이름']}</b><br>{s['시도']}", max_width=200),
            tooltip=s["이름"]
        ).add_to(m)
    for name, coords in SUPPORT_CENTER_COORDS.items():
        folium.Marker(
            location=[coords["위도"], coords["경도"]],
            popup=folium.Popup(f"<b>🏢 {name}</b>", max_width=200),
            tooltip=name,
            icon=folium.Icon(color="green", icon="home", prefix="fa")
        ).add_to(m)
    legend_html = """
    <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
                background:white;padding:10px 15px;border-radius:8px;
                border:1px solid #ccc;font-size:13px;line-height:1.8;">
        <b>범례</b><br>🔵 외국인전용 산단<br>🟢 외국인 지원센터
    </div>"""
    m.get_root().html.add_child(folium.Element(legend_html))
    return m

# ────────────────────────────────────────────
# 9. 시스템 프롬프트
# ────────────────────────────────────────────
def get_system_prompt(lang_code: str, lang_label: str) -> str:
    base_ko = """당신은 '산단 정착 AI'입니다. 한국 산업단지에서 일하는 외국인 근로자를 돕는 정착 지원 챗봇입니다.

역할:
1. 제공된 공공데이터(지원센터·병원·은행·출입국관서 등)를 바탕으로 정확하고 친절하게 답변하세요.
2. 데이터에 없는 내용은 절대 추측하지 말고 "해당 기관에 직접 문의해주세요"라고 안내하세요.
3. 답변 끝에 E9 통계 기반 인사이트를 한 줄 덧붙이세요.
4. 전화번호·주소 등 실제 정보는 반드시 데이터 그대로 정확하게 전달하세요.
5. 외국인 근로자가 이해하기 쉬운 간단한 문장으로 답변하세요."""
    if lang_code == "ko":
        return base_ko
    lang_instructions = {
        "vi": "Please respond entirely in Vietnamese (Tiếng Việt). Keep sentences short and simple.",
        "ne": "Please respond entirely in Nepali (नेपाली). Keep sentences short and simple.",
        "id": "Please respond entirely in Indonesian (Bahasa Indonesia). Keep sentences short and simple.",
        "my": "Please respond entirely in Burmese (မြန်မာဘာသာ). Keep sentences short and simple.",
        "th": "Please respond entirely in Thai (ภาษาไทย). Keep sentences short and simple.",
        "en": "Please respond entirely in English. Keep sentences short and simple.",
    }
    instruction = lang_instructions.get(lang_code, "Please respond in English.")
    return f"""{base_ko}\n\nIMPORTANT: {instruction}\nThe user selected {lang_label}. All responses must be in {lang_label} only.\nKorean institution names and phone numbers may appear as-is."""

# ────────────────────────────────────────────
# 10. UI — 사이드바
# ────────────────────────────────────────────
with st.sidebar:
    st.header("🌐 언어 선택 / Language")
    selected_lang_label = st.selectbox(
        "언어를 선택하세요",
        options=[l["label"] for l in LANG_LIST],
        index=0,
        label_visibility="collapsed"
    )
    lang_info = next(l for l in LANG_LIST if l["label"] == selected_lang_label)
    st.divider()
    st.header("🏭 산업단지 선택")
    selected_sandan_name = st.selectbox(
        "근무 중인 산업단지를 선택하세요",
        options=[s["이름"] for s in SANDAN_LIST],
        index=0,
        label_visibility="collapsed"
    )
    sandan_info = next(s for s in SANDAN_LIST if s["이름"] == selected_sandan_name)
    st.caption(f"📍 {sandan_info['시도']} {sandan_info['지역']}")
    st.divider()
    st.header("💬 답변 가능 항목")
    st.markdown("""
    - 외국인 지원센터 위치·연락처
    - 병원·응급실 (산재 포함)
    - 은행 계좌 개설 안내
    - 출입국·체류 관련 안내
    """)
    st.divider()
    st.header("📍 서비스 지역")
    st.markdown("""
    - 경기: **안산·화성·평택**
    - 충남: **아산·천안**
    - 경남: **김해**
    """)
    st.divider()
    if not GEMINI_API_KEY:
        st.error("⚠️ API 키 미설정")
    else:
        st.success("✅ Gemini API 연결됨")
        st.caption("gemini-3-flash-preview")

# ────────────────────────────────────────────
# 11. UI — 메인
# ────────────────────────────────────────────
st.title("🏭 산단 정착 AI")
st.caption("외국인 근로자를 위한 산업단지 정착 지원 챗봇 | 2026 산업통상부 공공데이터 활용 공모전 데모")

tab1, tab2 = st.tabs(["💬 챗봇", "🗺️ 산단·지원센터 지도"])

# ── 탭2: 전체 지도 ──
with tab2:
    st.subheader("🗺️ 외국인전용 산업단지 & 지원센터 전국 현황")
    m_full = make_full_map(36.5, 127.8, sandan_info["지역"])
    st_folium(m_full, width=None, height=600, returned_objects=[])

# ── 탭1: 챗봇 ──
with tab1:
    st.markdown("**아래 예시를 눌러보세요**")
    col1, col2, col3 = st.columns(3)
    example_clicked = None
    with col1:
        if st.button("🏢 지원센터 찾기", use_container_width=True):
            example_clicked = "근처 외국인 지원센터 어디 있어요?"
    with col2:
        if st.button("🏥 산재 병원", use_container_width=True):
            example_clicked = "다쳤을 때 치료받을 수 있는 병원 어디예요?"
    with col3:
        if st.button("🏦 계좌 개설", use_container_width=True):
            example_clicked = "베트남 사람도 계좌 만들 수 있는 은행 알려주세요"
    st.divider()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "map_data" not in st.session_state:
        st.session_state.map_data = []  # 각 답변에 대응하는 지도 데이터 저장

    if st.button("🔄 대화 초기화"):
        st.session_state.messages = []
        st.session_state.map_data = []
        st.rerun()

    # 기존 대화 + 지도 표시
    # assistant 메시지가 몇 번째로 등장했는지 별도로 세서 map_data와 1:1 매칭
    assistant_turn = 0
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
        if msg["role"] == "assistant":
            if assistant_turn < len(st.session_state.map_data):
                map_info = st.session_state.map_data[assistant_turn]
                if map_info:
                    with st.expander("📍 관련 기관 위치 지도", expanded=True):
                        st_folium(map_info, width=None, height=380, returned_objects=[], key=f"map_{i}")
            assistant_turn += 1

    user_input = example_clicked or st.chat_input(
        PLACEHOLDER.get(selected_lang_label, "질문을 입력하세요...")
    )

    if user_input:
        if not GEMINI_API_KEY:
            st.error("API 키를 먼저 설정해주세요.")
            st.stop()

        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        selected_region = sandan_info["지역"]
        context, _ = search_knowledge(user_input, selected_region)
        context_str = json.dumps(context, ensure_ascii=False, indent=2)

        with st.chat_message("assistant"):
            with st.spinner("답변 생성 중..."):
                try:
                    system_prompt = get_system_prompt(lang_info["code"], selected_lang_label)
                    model = genai.GenerativeModel(
                        model_name="gemini-3-flash-preview",
                        system_instruction=system_prompt
                    )
                    prompt = f"""다음은 질문과 관련된 실제 공공데이터입니다:

{context_str}

사용자 질문: {user_input}
사용자 선택 산업단지: {selected_sandan_name} ({selected_region}, {sandan_info['시도']})

위 데이터를 바탕으로 {selected_lang_label}으로 정확하게 답변해주세요.
E9 통계 기반 인사이트를 마지막에 한 줄 추가하세요."""

                    response = model.generate_content(prompt)
                    answer = response.text
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                    # 인라인 지도 생성
                    inline_map = make_inline_map(
                        context,
                        sandan_info["위도"], sandan_info["경도"]
                    )
                    st.session_state.map_data.append(inline_map)

                    # 지도 바로 표시
                    if inline_map:
                        with st.expander("📍 관련 기관 위치 지도", expanded=True):
                            st_folium(inline_map, width=None, height=380,
                                      returned_objects=[], key=f"map_new_{len(st.session_state.messages)}")

                    with st.expander("📊 참고한 데이터 보기"):
                        st.json(context)

                except Exception as e:
                    err = str(e)
                    st.error(f"오류 발생: {err}")
                    st.session_state.map_data.append(None)
                    if "quota" in err.lower() or "429" in err:
                        st.info("💡 요청 한도 초과입니다. 잠시 후 다시 시도해주세요.")
                    elif "404" in err or "not found" in err.lower():
                        st.info("💡 모델명을 확인해주세요.")
                    else:
                        st.info("💡 오류가 지속되면 API 키를 다시 확인해주세요.")
