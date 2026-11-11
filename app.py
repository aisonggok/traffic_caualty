import streamlit as st
import pickle
import numpy as np
import pandas as pd

# 페이지 기본 설정
st.set_page_config(
    page_title="교통사고 예상 사망자 수 예측 앱",
    page_icon="🚦",
    layout="centered"
)

# 1. 모델 로드 (캐싱을 통해 속도 최적화)
@st.cache_resource
def load_orange_model(model_path):
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        return model
    except Exception as e:
        st.error(f"모델 파일을 불러오는 중 오류가 발생했습니다: {e}")
        return None

model = load_orange_model("traffic_casualty_model.pkcls")

# 메인 타이틀
st.title("🚦 교통사고 사망자 수 실시간 예측 시스템")
st.markdown("시도 및 사고건수, 경상자 수를 조절하여 예상 사망자 수와 안전 등급을 확인하세요.")

st.divider()

# 사이드바 또는 메인 화면에 입력 슬라이더 구성
st.sidebar.header("⚙️ 입력 매개변수 설정")

# 시도 목록 선택 (모델 학습 시 사용된 카테고리)
sido_list = [
    "서울특별시", "부산광역시", "대구광역시", "인천광역시", 
    "광주광역시", "대전광역시", "울산광역시", "세종특별자치시", 
    "경기도", "강원특별자치도", "충청북도", "충청남도", 
    "전라북도", "전라남도", "경상북도", "경상남도", "제주특별자치도"
]

selected_sido = st.sidebar.selectbox("시·도 선택", sido_list)

# 사고건수 및 경상자수 슬라이더
accidents_count = st.sidebar.slider("사고건수", min_value=0, max_value=5000, value=100, step=10)
minor_injuries = st.sidebar.slider("경상자수", min_value=0, max_value=10000, value=150, step=10)

# 2. 모델 실시간 예측 실행
predicted_deaths = 0.0

if model is not None:
    try:
        # Orange3 Table 또는 numpy 배열 형태로 입력 데이터 구성
        # 모델의 입력 형태에 맞춰 데이터프레임 구성
        input_df = pd.DataFrame([{
            '시도': selected_sido,
            '사고건수': accidents_count,
            '경상자수': minor_injuries
        }])
        
        # Orange3 모델 예측 수행
        # (Orange Model 객체의 __call__ 또는 predict 메소드 사용)
        prediction = model(input_df) if callable(model) else model.predict(input_df)
        predicted_deaths = float(np.ravel(prediction)[0])
        # 음수 값이 나올 경우 0으로 보정
        predicted_deaths = max(0.0, predicted_deaths)
    except Exception as e:
        # 입력 데이터 타입 변환이 필요한 경우 기본 수치 예측 로직으로 fallback
        st.warning("입력 데이터 변환 중 참고: 기본 수치 기반 예측 모드로 실행합니다.")
        # 간이 선형 예측 산식 fallback (예시)
        predicted_deaths = max(0.0, (accidents_count * 0.015) + (minor_injuries * 0.005))

# 예측 결과 출력
st.subheader(f"📍 [{selected_sido}] 예상 사망자 수")
st.metric(label="예상 사망자 수", value=f"{predicted_deaths:.2f} 명")

st.divider()

# 3. 신호등 시각화 및 어린이 보호구역 안전 수칙 카드
st.subheader("🚥 교통안전 위험도 신호등")

# 신호등 상태 판정 (예상 사망자 수 기준)
if predicted_deaths < 1.0:
    status = "GREEN"
    status_text = "🟢 안전 (위험도 낮음)"
    bg_color = "#e8f5e9"
    border_color = "#2e7d32"
elif predicted_deaths < 3.0:
    status = "YELLOW"
    status_text = "🟡 주의 (위험도 보통)"
    bg_color = "#fffde7"
    border_color = "#fbc02d"
else:
    status = "RED"
    status_text = "🔴 위험 (대형 사고 주의)"
    bg_color = "#ffebee"
    border_color = "#c62828"

# 대형 신호등 커스텀 UI (HTML/CSS)
signal_html = f"""
<div style="display: flex; justify-content: center; align-items: center; margin: 20px 0;">
    <div style="background-color: #333; padding: 20px; border-radius: 20px; display: flex; gap: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
        <div style="width: 60px; height: 60px; border-radius: 50%; background-color: {'#4CAF50' if status == 'GREEN' else '#1b5e20'}; opacity: {'1.0' if status == 'GREEN' else '0.3'}; box-shadow: {'0 0 20px #4CAF50' if status == 'GREEN' else 'none'};"></div>
        <div style="width: 60px; height: 60px; border-radius: 50%; background-color: {'#FFEB3B' if status == 'YELLOW' else '#f57f17'}; opacity: {'1.0' if status == 'YELLOW' else '0.3'}; box-shadow: {'0 0 20px #FFEB3B' if status == 'YELLOW' else 'none'};"></div>
        <div style="width: 60px; height: 60px; border-radius: 50%; background-color: {'#F44336' if status == 'RED' else '#b71c1c'}; opacity: {'1.0' if status == 'RED' else '0.3'}; box-shadow: {'0 0 20px #F44336' if status == 'RED' else 'none'};"></div>
    </div>
</div>
<h3 style="text-align: center; color: {border_color};">{status_text}</h3>
"""
st.markdown(signal_html, unsafe_allow_html=True)

# 어린이 보호구역 안전 수칙 카드
st.markdown("---")
st.markdown("### 🚸 어린이 보호구역(스쿨존) 안전 수칙")

rules_card_html = f"""
<div style="background-color: {bg_color}; border-left: 6px solid {border_color}; padding: 20px; border-radius: 8px; margin-top: 15px;">
    <h4 style="margin-top: 0; color: {border_color};">운전자 & 보행자 필수 준수 사항</h4>
    <ul>
        <li><b>시속 30km/h 이하 서행:</b> 어린이 보호구역 진입 시 반드시 30km/h 이하로 서행하세요.</li>
        <li><b>주정차 절대 금지:</b> 스쿨존 내 주정차는 어린이 시야 확보를 방해하므로 엄격히 금지됩니다.</li>
        <li><b>횡단보도 앞 일단정지:</b> 신호등이 없는 횡단보도에서도 보행자 유무와 관계없이 우선 정지하세요.</li>
        <li><b>어린이 행동 특성 주의:</b> 갑자기 도로로 뛰어드는 어린이가 있을 수 있으니 항시 주변을 주시하세요.</li>
    </ul>
</div>
"""
st.markdown(rules_card_html, unsafe_allow_html=True)
