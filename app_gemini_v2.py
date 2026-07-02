"""
산단 정착 AI — 외국인 근로자 다국어 정착 지원 챗봇
2026 산업통상부 공공데이터 활용 아이디어 공모전

실행 방법:
1. pip install streamlit google-generativeai
2. 아래 GEMINI_API_KEY, KAKAO_JS_KEY 자리에 본인 키 입력
   - Gemini: AIza...로 시작 (aistudio.google.com)
   - 카카오맵 JavaScript 키: developers.kakao.com에서 발급
     (앱 생성 → 플랫폼 키 → JavaScript 키, 사이트 도메인에 배포 URL 등록 필요)
3. python -m streamlit run app_gemini_v2.py
"""

import streamlit as st
import json
import os
import streamlit.components.v1 as components
import google.generativeai as genai

# ────────────────────────────────────────────
# 0. API 키 설정
# ────────────────────────────────────────────
# 우선순위: 1) Streamlit secrets (Streamlit Cloud 배포용)
#           2) 환경변수 (로컬 개발용)
GEMINI_API_KEY = ""
KAKAO_JS_KEY = ""

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

try:
    KAKAO_JS_KEY = st.secrets["KAKAO_JS_KEY"]
except Exception:
    KAKAO_JS_KEY = os.environ.get("KAKAO_JS_KEY", "")

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
    "ko": "질문을 입력하세요 (예: 안산 지원센터 어디 있어요?)",
    "vi": "Nhập câu hỏi của bạn...",
    "ne": "आफ्नो प्रश्न टाइप गर्नुहोस्...",
    "id": "Ketik pertanyaan Anda...",
    "my": "သင့်မေးခွန်းကို ရိုက်ထည့်ပါ...",
    "th": "พิมพ์คำถามของคุณ...",
    "en": "Type your question here...",
}

# ────────────────────────────────────────────
# 5-1. UI 전체 다국어 텍스트
# ────────────────────────────────────────────
# 사이드바·제목·버튼 등 고정 UI 요소를 전부 여기서 관리.
# 언어 선택 시 챗봇 답변뿐 아니라 화면 전체가 같이 바뀌도록 함.
UI_TEXT = {
    "ko": {
        "lang_header": "🌐 언어 선택 / Language",
        "sandan_header": "🏭 산업단지 선택",
        "sandan_caption": "📍 {sido} {region}",
        "topics_header": "💬 답변 가능 항목",
        "topics_body": "- 외국인 지원센터 위치·연락처\n- 병원·응급실 (산재 포함)\n- 은행 계좌 개설 안내\n- 출입국·체류·비자 연장 안내\n- 산재 신고 절차 안내",
        "region_header": "📍 서비스 지역",
        "region_body": "- 경기: **안산·화성·평택**\n- 충남: **아산·천안**\n- 경남: **김해**",
        "api_missing": "⚠️ API 키 미설정",
        "api_ok": "✅ Gemini API 연결됨",
        "title": "🏭 산단 정착 AI",
        "subtitle": "외국인 근로자를 위한 산업단지 정착 지원 챗봇 | 2026 산업통상부 공공데이터 활용 공모전 데모",
        "tab_chat": "💬 챗봇",
        "tab_map": "🗺️ 산단·지원센터 지도",
        "map_subheader": "🗺️ 외국인전용 산업단지 & 지원센터 전국 현황",
        "examples_label": "**아래 예시를 눌러보세요**",
        "reset_button": "🔄 대화 초기화",
        "map_expander": "📍 관련 기관 위치 지도",
        "data_expander": "📊 참고한 데이터 보기",
        "api_key_needed": "API 키를 먼저 설정해주세요.",
        "spinner": "답변 생성 중...",
        "error_prefix": "오류 발생: ",
        "error_quota": "💡 요청 한도 초과입니다. 잠시 후 다시 시도해주세요.",
        "error_404": "💡 모델명을 확인해주세요.",
        "error_other": "💡 오류가 지속되면 API 키를 다시 확인해주세요.",
        "buttons": [
            {"icon": "🏢", "label": "지원센터 찾기", "query": "근처 외국인 지원센터 어디 있어요?"},
            {"icon": "🏥", "label": "산재 병원",     "query": "다쳤을 때 치료받을 수 있는 병원 어디예요?"},
            {"icon": "🏦", "label": "계좌 개설",     "query": "베트남 사람도 계좌 만들 수 있는 은행 알려주세요"},
            {"icon": "🛂", "label": "비자 연장",     "query": "체류기간 연장하려면 어디로 가야 해요?"},
            {"icon": "🚨", "label": "산재 신고",     "query": "일하다가 다쳤을 때 산재 신고는 어떻게 해요?"},
            {"icon": "📞", "label": "긴급 상담",     "query": "급하게 상담할 수 있는 곳 알려주세요"},
        ],
    },
    "vi": {
        "lang_header": "🌐 언어 선택 / Language",
        "sandan_header": "🏭 Chọn khu công nghiệp",
        "sandan_caption": "📍 {sido} {region}",
        "topics_header": "💬 Nội dung hỗ trợ",
        "topics_body": "- Vị trí·liên hệ trung tâm hỗ trợ người nước ngoài\n- Bệnh viện·cấp cứu (bao gồm tai nạn lao động)\n- Hướng dẫn mở tài khoản ngân hàng\n- Hướng dẫn xuất nhập cảnh·gia hạn visa\n- Hướng dẫn thủ tục báo cáo tai nạn lao động",
        "region_header": "📍 Khu vực dịch vụ",
        "region_body": "- Gyeonggi: **Ansan·Hwaseong·Pyeongtaek**\n- Chungnam: **Asan·Cheonan**\n- Gyeongnam: **Gimhae**",
        "api_missing": "⚠️ Chưa cài đặt API key",
        "api_ok": "✅ Đã kết nối Gemini API",
        "title": "🏭 AI Hỗ Trợ Định Cư Khu Công Nghiệp",
        "subtitle": "Chatbot hỗ trợ định cư cho người lao động nước ngoài | Cuộc thi sáng tạo dữ liệu công 2026",
        "tab_chat": "💬 Chatbot",
        "tab_map": "🗺️ Bản đồ khu công nghiệp·trung tâm hỗ trợ",
        "map_subheader": "🗺️ Hiện trạng khu công nghiệp & trung tâm hỗ trợ toàn quốc",
        "examples_label": "**Nhấn vào ví dụ bên dưới**",
        "reset_button": "🔄 Xóa hội thoại",
        "map_expander": "📍 Bản đồ vị trí cơ quan liên quan",
        "data_expander": "📊 Xem dữ liệu tham khảo",
        "api_key_needed": "Vui lòng cài đặt API key trước.",
        "spinner": "Đang tạo câu trả lời...",
        "error_prefix": "Đã xảy ra lỗi: ",
        "error_quota": "💡 Đã vượt quá giới hạn yêu cầu. Vui lòng thử lại sau.",
        "error_404": "💡 Vui lòng kiểm tra tên model.",
        "error_other": "💡 Nếu lỗi tiếp tục, vui lòng kiểm tra lại API key.",
        "buttons": [
            {"icon": "🏢", "label": "Tìm trung tâm hỗ trợ", "query": "Trung tâm hỗ trợ người nước ngoài gần đây ở đâu?"},
            {"icon": "🏥", "label": "Bệnh viện tai nạn LĐ",  "query": "Bệnh viện nào có thể điều trị khi tôi bị thương?"},
            {"icon": "🏦", "label": "Mở tài khoản",          "query": "Người Việt Nam có thể mở tài khoản ở ngân hàng nào?"},
            {"icon": "🛂", "label": "Gia hạn visa",          "query": "Tôi cần đến đâu để gia hạn thời gian lưu trú?"},
            {"icon": "🚨", "label": "Báo cáo tai nạn LĐ",    "query": "Làm thế nào để báo cáo tai nạn lao động khi bị thương lúc làm việc?"},
            {"icon": "📞", "label": "Tư vấn khẩn cấp",       "query": "Cho tôi biết nơi có thể tư vấn khẩn cấp"},
        ],
    },
    "ne": {
        "lang_header": "🌐 언어 선택 / Language",
        "sandan_header": "🏭 औद्योगिक क्षेत्र छनोट गर्नुहोस्",
        "sandan_caption": "📍 {sido} {region}",
        "topics_header": "💬 उपलब्ध सहयोग",
        "topics_body": "- विदेशी सहयोग केन्द्रको स्थान·सम्पर्क\n- अस्पताल·आकस्मिक उपचार (औद्योगिक दुर्घटना सहित)\n- बैंक खाता खोल्ने जानकारी\n- आप्रवासन·भिसा म्याद थप जानकारी\n- औद्योगिक दुर्घटना रिपोर्ट प्रक्रिया",
        "region_header": "📍 सेवा क्षेत्र",
        "region_body": "- ग्योन्गी: **अनसान·ह्वासेओन्ग·प्योङ्ताएक**\n- छुङ्नाम: **आसान·छेओनान**\n- ग्योङ्नाम: **गिम्हाए**",
        "api_missing": "⚠️ API कुञ्जी सेट गरिएको छैन",
        "api_ok": "✅ Gemini API जडान भयो",
        "title": "🏭 औद्योगिक क्षेत्र बसोबास सहयोग AI",
        "subtitle": "विदेशी कामदारका लागि औद्योगिक क्षेत्र बसोबास सहयोग च्याटबोट | 2026 सार्वजनिक डाटा प्रतियोगिता",
        "tab_chat": "💬 च्याटबोट",
        "tab_map": "🗺️ औद्योगिक क्षेत्र·सहयोग केन्द्र नक्सा",
        "map_subheader": "🗺️ राष्ट्रव्यापी औद्योगिक क्षेत्र र सहयोग केन्द्र अवस्था",
        "examples_label": "**तलका उदाहरणहरू थिच्नुहोस्**",
        "reset_button": "🔄 कुराकानी रिसेट गर्नुहोस्",
        "map_expander": "📍 सम्बन्धित संस्थाको स्थान नक्सा",
        "data_expander": "📊 सन्दर्भ डाटा हेर्नुहोस्",
        "api_key_needed": "कृपया पहिले API कुञ्जी सेट गर्नुहोस्।",
        "spinner": "जवाफ तयार गर्दै...",
        "error_prefix": "त्रुटि भयो: ",
        "error_quota": "💡 अनुरोध सीमा नाघ्यो। कृपया केहि बेरमा पुनः प्रयास गर्नुहोस्।",
        "error_404": "💡 कृपया मोडेलको नाम जाँच गर्नुहोस्।",
        "error_other": "💡 समस्या जारी रहे API कुञ्जी पुनः जाँच गर्नुहोस्।",
        "buttons": [
            {"icon": "🏢", "label": "सहयोग केन्द्र खोज्नुहोस्", "query": "नजिकैको विदेशी सहयोग केन्द्र कहाँ छ?"},
            {"icon": "🏥", "label": "औद्योगिक दुर्घटना अस्पताल", "query": "घाइते भएमा उपचार गर्न सकिने अस्पताल कहाँ छ?"},
            {"icon": "🏦", "label": "खाता खोल्ने",                "query": "भियतनामी नागरिकले पनि खाता खोल्न सक्ने बैंक बताउनुहोस्"},
            {"icon": "🛂", "label": "भिसा थप",                    "query": "बसोबास अवधि थप्न कहाँ जानुपर्छ?"},
            {"icon": "🚨", "label": "दुर्घटना रिपोर्ट",            "query": "काम गर्दा घाइते भएमा औद्योगिक दुर्घटना कसरी रिपोर्ट गर्ने?"},
            {"icon": "📞", "label": "आपतकालीन परामर्श",           "query": "छिटो परामर्श लिन सकिने ठाउँ बताउनुहोस्"},
        ],
    },
    "id": {
        "lang_header": "🌐 언어 선택 / Language",
        "sandan_header": "🏭 Pilih Kawasan Industri",
        "sandan_caption": "📍 {sido} {region}",
        "topics_header": "💬 Informasi yang Tersedia",
        "topics_body": "- Lokasi·kontak pusat dukungan warga asing\n- Rumah sakit·UGD (termasuk kecelakaan kerja)\n- Panduan pembukaan rekening bank\n- Panduan imigrasi·perpanjangan visa\n- Panduan prosedur pelaporan kecelakaan kerja",
        "region_header": "📍 Wilayah Layanan",
        "region_body": "- Gyeonggi: **Ansan·Hwaseong·Pyeongtaek**\n- Chungnam: **Asan·Cheonan**\n- Gyeongnam: **Gimhae**",
        "api_missing": "⚠️ API key belum diatur",
        "api_ok": "✅ Gemini API terhubung",
        "title": "🏭 AI Dukungan Pemukiman Kawasan Industri",
        "subtitle": "Chatbot dukungan pemukiman untuk pekerja asing | Kompetisi Pemanfaatan Data Publik 2026",
        "tab_chat": "💬 Chatbot",
        "tab_map": "🗺️ Peta Kawasan Industri·Pusat Dukungan",
        "map_subheader": "🗺️ Status Kawasan Industri & Pusat Dukungan Nasional",
        "examples_label": "**Klik contoh di bawah ini**",
        "reset_button": "🔄 Reset Percakapan",
        "map_expander": "📍 Peta Lokasi Lembaga Terkait",
        "data_expander": "📊 Lihat Data Referensi",
        "api_key_needed": "Silakan atur API key terlebih dahulu.",
        "spinner": "Membuat jawaban...",
        "error_prefix": "Terjadi kesalahan: ",
        "error_quota": "💡 Batas permintaan terlampaui. Silakan coba lagi nanti.",
        "error_404": "💡 Silakan periksa nama model.",
        "error_other": "💡 Jika error berlanjut, periksa kembali API key.",
        "buttons": [
            {"icon": "🏢", "label": "Cari Pusat Dukungan", "query": "Di mana pusat dukungan warga asing terdekat?"},
            {"icon": "🏥", "label": "RS Kecelakaan Kerja",  "query": "Rumah sakit mana yang bisa mengobati saat saya terluka?"},
            {"icon": "🏦", "label": "Buka Rekening",        "query": "Bank mana yang bisa membuka rekening untuk warga Vietnam?"},
            {"icon": "🛂", "label": "Perpanjang Visa",      "query": "Saya harus ke mana untuk memperpanjang masa tinggal?"},
            {"icon": "🚨", "label": "Lapor Kecelakaan",     "query": "Bagaimana cara melaporkan kecelakaan kerja saat terluka saat bekerja?"},
            {"icon": "📞", "label": "Konsultasi Darurat",   "query": "Beri tahu saya tempat konsultasi darurat"},
        ],
    },
    "my": {
        "lang_header": "🌐 언어 선택 / Language",
        "sandan_header": "🏭 စက်မှုဇုန် ရွေးချယ်ပါ",
        "sandan_caption": "📍 {sido} {region}",
        "topics_header": "💬 အကူအညီရနိုင်သော အကြောင်းအရာများ",
        "topics_body": "- နိုင်ငံခြားသား အကူအညီစင်တာ တည်နေရာ·ဆက်သွယ်ရန်\n- ဆေးရုံ·အရေးပေါ် (လုပ်ငန်းခွင်ထိခိုက်မှုပါ)\n- ဘဏ်အကောင့်ဖွင့်ခြင်း လမ်းညွှန်\n- လူဝင်မှုကြီးကြပ်ရေး·ဗီဇာသက်တမ်းတိုးခြင်း လမ်းညွှန်\n- လုပ်ငန်းခွင်ထိခိုက်မှု တိုင်ကြားရန် လုပ်ထုံးလုပ်နည်း",
        "region_header": "📍 ဝန်ဆောင်မှုဧရိယာ",
        "region_body": "- ဂျင်ဂီ: **အန်ဆန်·ဟွာဆွန်·ဖျောင်တိတ်**\n- ချွန်နမ်: **အာဆန်·ချွန်အန်**\n- ဂျောင်နမ်: **ဂျင်ဟေး**",
        "api_missing": "⚠️ API key သတ်မှတ်မထားပါ",
        "api_ok": "✅ Gemini API ချိတ်ဆက်ပြီး",
        "title": "🏭 စက်မှုဇုန် နေထိုင်မှု အကူအညီ AI",
        "subtitle": "နိုင်ငံခြားသား လုပ်သားများအတွက် စက်မှုဇုန် နေထိုင်မှု အကူအညီ Chatbot | 2026 အများသုံးဒေတာ ပြိုင်ပွဲ",
        "tab_chat": "💬 Chatbot",
        "tab_map": "🗺️ စက်မှုဇုန်·အကူအညီစင်တာ မြေပုံ",
        "map_subheader": "🗺️ တစ်နိုင်ငံလုံး စက်မှုဇုန်နှင့် အကူအညီစင်တာ အခြေအနေ",
        "examples_label": "**အောက်ပါ ဥပမာများကို နှိပ်ပါ**",
        "reset_button": "🔄 စကားဝိုင်း ပြန်စပါ",
        "map_expander": "📍 သက်ဆိုင်ရာ အဖွဲ့အစည်း တည်နေရာ မြေပုံ",
        "data_expander": "📊 ကိုးကားဒေတာ ကြည့်ရန်",
        "api_key_needed": "ကျေးဇူးပြု၍ API key ကို အရင်သတ်မှတ်ပါ။",
        "spinner": "အဖြေ ထုတ်လုပ်နေသည်...",
        "error_prefix": "အမှား ဖြစ်ပွားသည်: ",
        "error_quota": "💡 တောင်းဆိုမှု ကန့်သတ်ချက် ကျော်လွန်သည်။ နောက်မှ ထပ်စမ်းကြည့်ပါ။",
        "error_404": "💡 ကျေးဇူးပြု၍ model အမည်ကို စစ်ဆေးပါ။",
        "error_other": "💡 အမှားဆက်ဖြစ်ပါက API key ကို ပြန်စစ်ပါ။",
        "buttons": [
            {"icon": "🏢", "label": "အကူအညီစင်တာ ရှာရန်", "query": "အနီးဆုံး နိုင်ငံခြားသား အကူအညီစင်တာ ဘယ်မှာလဲ?"},
            {"icon": "🏥", "label": "လုပ်ငန်းခွင် ဆေးရုံ",    "query": "ထိခိုက်ဒဏ်ရာရရင် ကုသနိုင်တဲ့ ဆေးရုံ ဘယ်မှာလဲ?"},
            {"icon": "🏦", "label": "အကောင့်ဖွင့်ရန်",        "query": "ဗီယက်နမ်လူမျိုးလည်း အကောင့်ဖွင့်နိုင်တဲ့ ဘဏ်ပြောပြပါ"},
            {"icon": "🛂", "label": "ဗီဇာသက်တမ်းတိုးရန်",     "query": "နေထိုင်ခွင့် ကာလတိုးချင်ရင် ဘယ်ကိုသွားရမလဲ?"},
            {"icon": "🚨", "label": "လုပ်ငန်းခွင်ထိခိုက်မှု တိုင်ကြားရန်", "query": "အလုပ်လုပ်နေစဉ် ထိခိုက်ရင် ဘယ်လိုတိုင်ကြားရမလဲ?"},
            {"icon": "📞", "label": "အရေးပေါ် တိုင်ပင်ရန်",   "query": "အမြန် တိုင်ပင်နိုင်တဲ့ နေရာ ပြောပြပါ"},
        ],
    },
    "th": {
        "lang_header": "🌐 언어 선택 / Language",
        "sandan_header": "🏭 เลือกนิคมอุตสาหกรรม",
        "sandan_caption": "📍 {sido} {region}",
        "topics_header": "💬 หัวข้อที่สามารถตอบได้",
        "topics_body": "- ที่ตั้ง·ติดต่อศูนย์ช่วยเหลือชาวต่างชาติ\n- โรงพยาบาล·ห้องฉุกเฉิน (รวมอุบัติเหตุจากการทำงาน)\n- คำแนะนำการเปิดบัญชีธนาคาร\n- คำแนะนำตรวจคนเข้าเมือง·การต่อวีซ่า\n- ขั้นตอนการแจ้งอุบัติเหตุจากการทำงาน",
        "region_header": "📍 พื้นที่ให้บริการ",
        "region_body": "- คย็องกี: **อันซาน·ฮวาซอง·พยองแท็ก**\n- ชุงนาม: **อาซาน·ชอนอัน**\n- คย็องนาม: **กิมแฮ**",
        "api_missing": "⚠️ ยังไม่ได้ตั้งค่า API key",
        "api_ok": "✅ เชื่อมต่อ Gemini API แล้ว",
        "title": "🏭 AI สนับสนุนการตั้งถิ่นฐานในนิคมอุตสาหกรรม",
        "subtitle": "แชทบอทสนับสนุนการตั้งถิ่นฐานสำหรับแรงงานต่างชาติ | การประกวดใช้ข้อมูลสาธารณะ 2026",
        "tab_chat": "💬 แชทบอท",
        "tab_map": "🗺️ แผนที่นิคมอุตสาหกรรม·ศูนย์ช่วยเหลือ",
        "map_subheader": "🗺️ สถานะนิคมอุตสาหกรรมและศูนย์ช่วยเหลือทั่วประเทศ",
        "examples_label": "**กดตัวอย่างด้านล่าง**",
        "reset_button": "🔄 รีเซ็ตการสนทนา",
        "map_expander": "📍 แผนที่ตำแหน่งหน่วยงานที่เกี่ยวข้อง",
        "data_expander": "📊 ดูข้อมูลอ้างอิง",
        "api_key_needed": "กรุณาตั้งค่า API key ก่อน",
        "spinner": "กำลังสร้างคำตอบ...",
        "error_prefix": "เกิดข้อผิดพลาด: ",
        "error_quota": "💡 เกินขีดจำกัดคำขอ กรุณาลองใหม่ภายหลัง",
        "error_404": "💡 กรุณาตรวจสอบชื่อโมเดล",
        "error_other": "💡 หากข้อผิดพลาดยังคงอยู่ กรุณาตรวจสอบ API key อีกครั้ง",
        "buttons": [
            {"icon": "🏢", "label": "ค้นหาศูนย์ช่วยเหลือ", "query": "ศูนย์ช่วยเหลือชาวต่างชาติใกล้เคียงอยู่ที่ไหน?"},
            {"icon": "🏥", "label": "รพ.อุบัติเหตุงาน",     "query": "โรงพยาบาลไหนรักษาได้เมื่อฉันได้รับบาดเจ็บ?"},
            {"icon": "🏦", "label": "เปิดบัญชี",            "query": "คนเวียดนามเปิดบัญชีธนาคารไหนได้บ้าง?"},
            {"icon": "🛂", "label": "ต่อวีซ่า",              "query": "ต้องไปที่ไหนเพื่อขยายระยะเวลาพำนัก?"},
            {"icon": "🚨", "label": "แจ้งอุบัติเหตุงาน",     "query": "ถ้าได้รับบาดเจ็บขณะทำงานต้องแจ้งอุบัติเหตุอย่างไร?"},
            {"icon": "📞", "label": "ปรึกษาฉุกเฉิน",        "query": "บอกสถานที่ที่สามารถปรึกษาด่วนได้"},
        ],
    },
    "en": {
        "lang_header": "🌐 언어 선택 / Language",
        "sandan_header": "🏭 Select Industrial Complex",
        "sandan_caption": "📍 {sido} {region}",
        "topics_header": "💬 What I Can Help With",
        "topics_body": "- Foreign support center locations·contacts\n- Hospitals·emergency rooms (incl. work injuries)\n- Bank account opening guidance\n- Immigration·visa extension guidance\n- Work injury report procedure guidance",
        "region_header": "📍 Service Area",
        "region_body": "- Gyeonggi: **Ansan·Hwaseong·Pyeongtaek**\n- Chungnam: **Asan·Cheonan**\n- Gyeongnam: **Gimhae**",
        "api_missing": "⚠️ API key not set",
        "api_ok": "✅ Gemini API connected",
        "title": "🏭 Industrial Complex Settlement AI",
        "subtitle": "Settlement support chatbot for foreign workers | 2026 Public Data Utilization Contest",
        "tab_chat": "💬 Chatbot",
        "tab_map": "🗺️ Industrial Complex·Support Center Map",
        "map_subheader": "🗺️ Nationwide Industrial Complex & Support Center Status",
        "examples_label": "**Click an example below**",
        "reset_button": "🔄 Reset Conversation",
        "map_expander": "📍 Related Institution Location Map",
        "data_expander": "📊 View Reference Data",
        "api_key_needed": "Please set up the API key first.",
        "spinner": "Generating answer...",
        "error_prefix": "Error occurred: ",
        "error_quota": "💡 Request limit exceeded. Please try again later.",
        "error_404": "💡 Please check the model name.",
        "error_other": "💡 If the error persists, please check your API key.",
        "buttons": [
            {"icon": "🏢", "label": "Find Support Center", "query": "Where is the nearest foreign support center?"},
            {"icon": "🏥", "label": "Work Injury Hospital", "query": "Which hospital can treat me if I'm injured?"},
            {"icon": "🏦", "label": "Open Account",         "query": "Which banks let Vietnamese citizens open accounts?"},
            {"icon": "🛂", "label": "Extend Visa",          "query": "Where do I go to extend my stay period?"},
            {"icon": "🚨", "label": "Report Work Injury",   "query": "How do I report a work injury if I get hurt while working?"},
            {"icon": "📞", "label": "Emergency Consult",    "query": "Tell me where I can get urgent consultation"},
        ],
    },
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
# 7. 카카오맵 임베드 헬퍼
# ────────────────────────────────────────────
def _kakao_marker_js(lat, lng, title, content_html, marker_color="#2E75B6"):
    """카카오맵 마커 + 인포윈도우 하나를 생성하는 JS 조각을 반환"""
    safe_content = content_html.replace("`", "'").replace("\n", " ")
    return f"""
    (function() {{
        var pos = new kakao.maps.LatLng({lat}, {lng});
        var marker = new kakao.maps.Marker({{ position: pos, map: map }});
        var iw = new kakao.maps.InfoWindow({{
            content: `<div style="padding:8px 10px;font-size:13px;line-height:1.5;max-width:240px;">{safe_content}</div>`
        }});
        kakao.maps.event.addListener(marker, 'click', function() {{ iw.open(map, marker); }});
        bounds.extend(pos);
        markerCount++;
    }})();
    """

def render_kakao_map(markers_js: list, center_lat: float, center_lng: float, height: int = 420, level: int = 6):
    """카카오맵을 components.html로 렌더링. markers_js: _kakao_marker_js로 만든 JS 조각 리스트"""
    if not KAKAO_JS_KEY:
        st.warning("⚠️ 카카오맵 API 키(KAKAO_JS_KEY)가 설정되지 않아 지도를 표시할 수 없습니다. Secrets에 키를 추가해주세요.")
        return

    markers_block = "\n".join(markers_js)
    html = f"""
    <div id="map" style="width:100%;height:{height}px;border-radius:8px;"></div>
    <script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_JS_KEY}"></script>
    <script>
        var container = document.getElementById('map');
        var options = {{
            center: new kakao.maps.LatLng({center_lat}, {center_lng}),
            level: {level}
        }};
        var map = new kakao.maps.Map(container, options);
        map.addControl(new kakao.maps.ZoomControl(), kakao.maps.ControlPosition.RIGHT);
        var bounds = new kakao.maps.LatLngBounds();
        var markerCount = 0;

        {markers_block}

        if (markerCount > 0) {{
            map.setBounds(bounds);
        }}
    </script>
    """
    components.html(html, height=height + 10)

# ────────────────────────────────────────────
# 8. 챗봇 답변 후 인라인 지도 데이터 생성
# ────────────────────────────────────────────
def make_inline_map(context: dict, center_lat: float, center_lng: float):
    """답변에 언급된 기관들의 카카오맵 마커 JS 조각 리스트를 반환. 없으면 None"""
    markers = []

    if "외국인지원센터" in context:
        for item in context["외국인지원센터"]:
            name = item.get("기관명", "")
            coords = SUPPORT_CENTER_COORDS.get(name)
            if coords:
                content = f"<b>🏢 {name}</b><br>{item.get('주소','')}<br>{item.get('전화번호','')}"
                markers.append(_kakao_marker_js(coords["위도"], coords["경도"], name, content))

    if "병원정보" in context:
        for item in context["병원정보"]:
            name = item.get("기관명", "")
            coords = HOSPITAL_COORDS.get(name)
            if coords:
                content = f"<b>🏥 {name}</b><br>{item.get('분류','')}<br>{item.get('참고','')}"
                markers.append(_kakao_marker_js(coords["위도"], coords["경도"], name, content))

    if "출입국관서" in context:
        for item in context["출입국관서"]:
            name = item.get("기관명", "")
            coords = IMMIGRATION_COORDS.get(name)
            if coords:
                content = f"<b>🏛 {name}</b><br>{item.get('주소','')}<br>{item.get('전화번호','')}"
                markers.append(_kakao_marker_js(coords["위도"], coords["경도"], name, content))

    return markers if markers else None

# ────────────────────────────────────────────
# 9. 전체 산단 지도 (탭2용) — 카카오맵
# ────────────────────────────────────────────
def render_full_map(center_lat: float, center_lng: float, selected_region: str = None):
    if not KAKAO_JS_KEY:
        st.warning("⚠️ 카카오맵 API 키(KAKAO_JS_KEY)가 설정되지 않아 지도를 표시할 수 없습니다. Secrets에 키를 추가해주세요.")
        return

    markers_block_parts = []
    for s in SANDAN_COORDS:
        content = f"<b>🏭 {s['이름']}</b><br>{s['시도']}"
        markers_block_parts.append(_kakao_marker_js(s["위도"], s["경도"], s["이름"], content))
    for name, coords in SUPPORT_CENTER_COORDS.items():
        content = f"<b>🏢 {name}</b>"
        markers_block_parts.append(_kakao_marker_js(coords["위도"], coords["경도"], name, content))

    markers_block = "\n".join(markers_block_parts)
    height = 600
    html = f"""
    <div id="map2" style="width:100%;height:{height}px;border-radius:8px;"></div>
    <div style="position:relative;">
      <div style="position:absolute;bottom:14px;left:14px;z-index:10;background:white;
                  padding:10px 14px;border-radius:8px;border:1px solid #ddd;
                  font-size:13px;line-height:1.8;box-shadow:0 1px 4px rgba(0,0,0,0.15);">
        <b>범례</b><br>🔵 외국인전용 산단<br>🟢 외국인 지원센터
      </div>
    </div>
    <script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_JS_KEY}"></script>
    <script>
        var container = document.getElementById('map2');
        var options = {{
            center: new kakao.maps.LatLng({center_lat}, {center_lng}),
            level: 12
        }};
        var map = new kakao.maps.Map(container, options);
        map.addControl(new kakao.maps.ZoomControl(), kakao.maps.ControlPosition.RIGHT);
        var bounds = new kakao.maps.LatLngBounds();
        var markerCount = 0;

        {markers_block}
    </script>
    """
    components.html(html, height=height + 60)

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
    st.header(UI_TEXT["ko"]["lang_header"])
    selected_lang_label = st.selectbox(
        "언어를 선택하세요",
        options=[l["label"] for l in LANG_LIST],
        index=0,
        label_visibility="collapsed"
    )
    lang_info = next(l for l in LANG_LIST if l["label"] == selected_lang_label)
    T = UI_TEXT[lang_info["code"]]  # 선택된 언어의 전체 UI 텍스트 묶음

    st.divider()
    st.header(T["sandan_header"])
    selected_sandan_name = st.selectbox(
        "근무 중인 산업단지를 선택하세요",
        options=[s["이름"] for s in SANDAN_LIST],
        index=0,
        label_visibility="collapsed"
    )
    sandan_info = next(s for s in SANDAN_LIST if s["이름"] == selected_sandan_name)
    st.caption(T["sandan_caption"].format(sido=sandan_info["시도"], region=sandan_info["지역"]))
    st.divider()
    st.header(T["topics_header"])
    st.markdown(T["topics_body"])
    st.divider()
    st.header(T["region_header"])
    st.markdown(T["region_body"])
    st.divider()
    if not GEMINI_API_KEY:
        st.error(T["api_missing"])
    else:
        st.success(T["api_ok"])
        st.caption("gemini-3-flash-preview")

# ────────────────────────────────────────────
# 11. UI — 메인
# ────────────────────────────────────────────
st.title(T["title"])
st.caption(T["subtitle"])

tab1, tab2 = st.tabs([T["tab_chat"], T["tab_map"]])

# ── 탭2: 전체 지도 ──
with tab2:
    st.subheader(T["map_subheader"])
    render_full_map(36.5, 127.8, sandan_info["지역"])

# ── 탭1: 챗봇 ──
with tab1:
    st.markdown(T["examples_label"])
    button_cols = st.columns(3)
    example_clicked = None
    for idx, btn in enumerate(T["buttons"]):
        col = button_cols[idx % 3]
        with col:
            if st.button(f"{btn['icon']} {btn['label']}", use_container_width=True, key=f"ex_btn_{idx}"):
                example_clicked = btn["query"]
    st.divider()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "map_data" not in st.session_state:
        st.session_state.map_data = []  # 각 답변에 대응하는 지도 데이터 저장

    if st.button(T["reset_button"]):
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
                    with st.expander(T["map_expander"], expanded=True):
                        render_kakao_map(map_info["markers"], map_info["lat"], map_info["lng"])
            assistant_turn += 1

    user_input = example_clicked or st.chat_input(
        PLACEHOLDER.get(lang_info["code"], "질문을 입력하세요...")
    )

    if user_input:
        if not GEMINI_API_KEY:
            st.error(T["api_key_needed"])
            st.stop()

        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        selected_region = sandan_info["지역"]
        context, _ = search_knowledge(user_input, selected_region)
        context_str = json.dumps(context, ensure_ascii=False, indent=2)

        with st.chat_message("assistant"):
            with st.spinner(T["spinner"]):
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

                    # 인라인 지도용 마커 JS 생성
                    inline_markers = make_inline_map(
                        context,
                        sandan_info["위도"], sandan_info["경도"]
                    )
                    if inline_markers:
                        st.session_state.map_data.append({
                            "markers": inline_markers,
                            "lat": sandan_info["위도"],
                            "lng": sandan_info["경도"],
                        })
                    else:
                        st.session_state.map_data.append(None)

                    # 지도 바로 표시
                    if inline_markers:
                        with st.expander(T["map_expander"], expanded=True):
                            render_kakao_map(inline_markers, sandan_info["위도"], sandan_info["경도"])

                    with st.expander(T["data_expander"]):
                        st.json(context)

                except Exception as e:
                    err = str(e)
                    st.error(T["error_prefix"] + err)
                    st.session_state.map_data.append(None)
                    if "quota" in err.lower() or "429" in err:
                        st.info(T["error_quota"])
                    elif "404" in err or "not found" in err.lower():
                        st.info(T["error_404"])
                    else:
                        st.info(T["error_other"])
