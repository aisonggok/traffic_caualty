import streamlit as st
import pickle
import numpy as np

# 페이지 기본 설정
st.set_page_config(
    page_title="교통사고 연간 예상 사망자 수 예측 앱",
    page_icon="🚦",
    layout="centered"
)

# 다크모드/라이트모드 모두 대응 가능한 고대비 글자색 CSS
st.markdown("""
    <style>
    .contrast-card {
        padding: 20px;
        border-radius: 12px;
        margin-top: 15px;
        color: #111111 !important; /* 가독성을 위한 명확한 검은색 글자 */
    }
    .contrast-card h4 {
        color: #000000 !important;
        margin-top: 0;
        font-weight: 700;
    }
    .contrast-card li {
        color: #111111 !important;
        font-size: 15px;
        line-height: 1.6;
    }
    .signal-title {
        text-align: center;
        font-weight: 800;
        font-size: 22px;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 1. Orange3 모델 로드 (캐싱 적용)
@st.cache_resource
def load_orange_model(model_path):
    try:
        import Orange  # Orange3 pickle 언피클링을 위한 모듈 로드
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        st.error(f"모델 파일 로드 실패: {e}")
        return None

model = load_orange_model("traffic_casualty_model.pkcls")

# 메인 타이틀 및 연간 기준 안내
st.title("🚦 교통사고 연간 사망자 수 실시간 예측 시스템")
st.caption("💡 본 모델은 **연간(1년) 누적 통계 데이터** 기반으로 학습되었습니다.")
st.write("시·도 선택 및 **연간 사고건수**, **연간 경상자수**를 조절하여 예상 사망자 수와 안전 등급을 확인하세요.")

st.divider()

# 사이드바 입력 매개변수 설정 (연간 기준에 적합한 범위 설정)
st.sidebar.header("⚙️ 연간 데이터 설정")

sido_list = [
    "서울특별시", "부산광역시", "대구광역시", "인천광역시", 
    "광주광역시", "대전광역시", "울산광역시", "세종특별자치시", 
    "경기도", "강원특별자치도", "충청북도", "충청남도", 
    "전라북도", "전라남도", "경상북도", "경상남도", "제주특별자치도"
]

selected_sido = st.sidebar.selectbox("시·도 선택", sido_list)

# 연간 통계 수치에 맞게 최댓값 및 기본값 조정
accidents_count = st.sidebar.slider(
    "연간 사고건수", 
    min_value=0, 
    max_value=50000, 
    value=10000, 
    step=100,
    help="선택한 시·도의 1년 동안 발생한 총 사고건수를 입력하세요."
)

minor_injuries = st.sidebar.slider(
    "연간 경상자수", 
    min_value=0, 
    max_value=100000, 
    value=15000,
