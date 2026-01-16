import streamlit as st
import pandas as pd
import plotly.express as px
import os
import signal
import time
import streamlit.components.v1 as components

# -----------------------------------------------------------------------------
# App Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="서울시 로컬 상권 분석",
    page_icon="🥕",
    layout="wide"
)

# -----------------------------------------------------------------------------
# Data Loading & Caching
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    """
    전처리된 CSV 데이터를 로드하고 기본 결측치를 처리
    """
    # 데이터 경로: src 폴더와 같은 레벨의 data 폴더 참조
    data_path = os.path.join("data", "seoul_market_final.csv")
    
    if not os.path.exists(data_path):
        return pd.DataFrame() # 빈 데이터프레임 반환
        
    df = pd.read_csv(data_path)
    df['SIGNGU_CD_NM'] = df['SIGNGU_CD_NM'].fillna("Unknown")
    return df

df = load_data()

# 데이터가 없는 경우 예외 처리 UI 표시
if df.empty:
    st.error("데이터 파일을 찾을 수 없습니다. 'src/collector.py'와 'src/preprocessor.py'를 먼저 실행해주세요.")
    st.stop()

# -----------------------------------------------------------------------------
# Sidebar: User Controls
# -----------------------------------------------------------------------------
st.sidebar.header("🔍 분석 조건 설정")

# 업종 리스트 추출 및 정렬
industry_list = sorted(df['SVC_INDUTY_CD_NM'].astype(str).unique().tolist())

# 초기 선택값 설정 (커피 업종 우선 선택)
default_idx = 0
for i, industry in enumerate(industry_list):
    if "커피" in industry:
        default_idx = i
        break

selected_industry = st.sidebar.selectbox(
    "분석 대상 업종",
    industry_list,
    index=default_idx
)

# 자치구 다중 선택 필터
all_districts = sorted(df['SIGNGU_CD_NM'].unique().tolist())
selected_districts = st.sidebar.multiselect(
    "자치구 필터 (미선택 시 전체)",
    all_districts,
    default=[]
)

# 사이드바 종료 버튼
st.sidebar.markdown("---") # 구분선
if st.sidebar.button("❌ 앱 종료 (Server Stop)"):
    # 1. 사용자에게 안내 메시지 표시
    st.sidebar.warning("서버가 안전하게 종료되었습니다. 이 탭을 닫으셔도 됩니다.")
    
    # 2. 메시지를 읽을 시간(1초)을 주고
    time.sleep(1)
    
    # 3. 파이썬 프로세스 종료 (터미널이 꺼짐)
    pid = os.getpid()
    os.kill(pid, signal.SIGTERM)

# -----------------------------------------------------------------------------
# Data Filtering Logic
# -----------------------------------------------------------------------------
filtered_df = df[df['SVC_INDUTY_CD_NM'] == selected_industry]

if selected_districts:
    filtered_df = filtered_df[filtered_df['SIGNGU_CD_NM'].isin(selected_districts)]

# -----------------------------------------------------------------------------
# Main Dashboard Layout
# -----------------------------------------------------------------------------
st.title(f"🥕 서울시 '{selected_industry}' 상권 현황")
st.markdown("Source: Seoul Open Data Plaza (Real-time API)")

# Key Performance Indicators (KPI)
col1, col2, col3 = st.columns(3)

# 컬럼명 매핑: STOR_CO(총점포수), OPBIZ_STOR_CO(개업점포수), CLSBIZ_STOR_CO(폐업점포수)
total_stores = filtered_df['STOR_CO'].sum()
total_open = filtered_df['OPBIZ_STOR_CO'].sum()
total_close = filtered_df['CLSBIZ_STOR_CO'].sum()

col1.metric("총 점포 수", f"{int(total_stores):,}개")
col2.metric("신규 개업", f"{int(total_open)}개", delta=int(total_open))
col3.metric("폐업", f"{int(total_close)}개", delta=-int(total_close), delta_color="inverse")

st.divider()

# -----------------------------------------------------------------------------
# Visualization
# -----------------------------------------------------------------------------
st.subheader("📊 자치구별 개업 vs 폐업 비교")

# 자치구별 집계
district_group = filtered_df.groupby('SIGNGU_CD_NM')[['OPBIZ_STOR_CO', 'CLSBIZ_STOR_CO']].sum().reset_index()

if district_group.empty:
    st.warning("조건에 해당하는 데이터가 없습니다.")
else:
    # 시각화를 위한 Unpivot (Melt)
    district_melted = district_group.melt(
        id_vars='SIGNGU_CD_NM', 
        value_vars=['OPBIZ_STOR_CO', 'CLSBIZ_STOR_CO'],
        var_name='Status', value_name='Count'
    )
    
    district_melted['Status'] = district_melted['Status'].replace({
        'OPBIZ_STOR_CO': 'Opened',
        'CLSBIZ_STOR_CO': 'Closed'
    })

    # Plotly Bar Chart
    fig = px.bar(
        district_melted, 
        x='SIGNGU_CD_NM', 
        y='Count', 
        color='Status',
        barmode='group',
        color_discrete_map={'Opened': '#5DADE2', 'Closed': '#EC7063'},
        title=f"{selected_industry} Regional Status"
    )
    
    st.plotly_chart(fig, width="stretch")

# -----------------------------------------------------------------------------
# Data Table
# -----------------------------------------------------------------------------
with st.expander("Raw Data View"):
    st.dataframe(filtered_df[['TRDAR_CD_NM', 'SIGNGU_CD_NM', 'STOR_CO', 'OPBIZ_STOR_CO', 'CLSBIZ_STOR_CO']])