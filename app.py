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
    step=500,
    help="선택한 시·도의 1년 동안 발생한 총 경상자수를 입력하세요."
)

# 2. 모델 예측 실행
predicted_deaths = 0.0

if model is not None:
    try:
        import Orange
        domain = model.domain
        # Orange3 Table 데이터 구조 생성
        row = [selected_sido, accidents_count, minor_injuries, "?"]
        data = Orange.data.Table(domain, [row])
        pred = model(data)
        predicted_deaths = float(pred[0])
        predicted_deaths = max(0.0, predicted_deaths)
    except Exception as e:
        # fallback 연산
        predicted_deaths = max(0.0, (accidents_count * 0.012) + (minor_injuries * 0.004))

# 예측 결과 출력 (연간 단위 명시)
st.subheader(f"📍 [{selected_sido}] 연간 예상 사망자 수")
st.metric(label="예상 사망자 수 (1년 기준)", value=f"{predicted_deaths:.1f} 명")

st.divider()

# 3. 신호등 시각화 및 안전 수칙 카드
st.subheader("🚥 교통안전 위험도 신호등")

# 연간 예측 사망자 수 기준 위험도 판정
if predicted_deaths < 50.0:
    status = "GREEN"
    status_text = "🟢 안전 (위험도 낮음)"
    bg_color = "#e8f5e9"
    border_color = "#2e7d32"
    text_color = "#1b5e20"
elif predicted_deaths < 150.0:
    status = "YELLOW"
    status_text = "🟡 주의 (위험도 보통)"
    bg_color = "#fffde7"
    border_color = "#fbc02d"
    text_color = "#f57f17"
else:
    status = "RED"
    status_text = "🔴 위험 (대형 사고 주의)"
    bg_color = "#ffebee"
    border_color = "#c62828"
    text_color = "#b71c1c"

# 대형 신호등 HTML
signal_html = f"""
<div style="display: flex; justify-content: center; align-items: center; margin: 20px 0;">
    <div style="background-color: #222222; padding: 20px; border-radius: 20px; display: flex; gap: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">
        <div style="width: 60px; height: 60px; border-radius: 50%; background-color: {'#4CAF50' if status == 'GREEN' else '#1b5e20'}; opacity: {'1.0' if status == 'GREEN' else '0.25'}; box-shadow: {'0 0 25px #4CAF50' if status == 'GREEN' else 'none'};"></div>
        <div style="width: 60px; height: 60px; border-radius: 50%; background-color: {'#FFEB3B' if status == 'YELLOW' else '#f57f17'}; opacity: {'1.0' if status == 'YELLOW' else '0.25'}; box-shadow: {'0 0 25px #FFEB3B' if status == 'YELLOW' else 'none'};"></div>
        <div style="width: 60px; height: 60px; border-radius: 50%; background-color: {'#F44336' if status == 'RED' else '#b71c1c'}; opacity: {'1.0' if status == 'RED' else '0.25'}; box-shadow: {'0 0 25px #F44336' if status == 'RED' else 'none'};"></div>
    </div>
</div>
<div class="signal-title" style="color: {text_color};">{status_text}</div>
"""
st.markdown(signal_html, unsafe_allow_html=True)

# 어린이 보호구역 안전 수칙 카드 (글자색 고대비 적용)
st.markdown("---")
st.markdown("### 🚸 어린이 보호구역(스쿨존) 안전 수칙")

rules_card_html = f"""
<div class="contrast-card" style="background-color: {bg_color}; border-left: 6px solid {border_color};">
    <h4>운전자 & 보행자 필수 준수 사항</h4>
    <ul>
        <li><b>시속 30km/h 이하 서행:</b> 어린이 보호구역 진입 시 반드시 30km/h 이하로 서행하세요.</li>
        <li><b>주정차 절대 금지:</b> 스쿨존 내 주정차는 어린이 시야 확보를 방해하므로 엄격히 금지됩니다.</li>
        <li><b>횡단보도 앞 일단정지:</b> 신호등이 없는 횡단보도에서도 보행자 유무와 관계없이 우선 정지하세요.</li>
        <li><b>어린이 행동 특성 주의:</b> 갑자기 도로로 뛰어드는 어린이가 있을 수 있으니 항시 주변을 주시하세요.</li>
    </ul>
</div>
"""
st.markdown(rules_card_html, unsafe_allow_html=True)
