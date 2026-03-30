import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 페이지 설정
st.set_page_config(page_title="Sales Data Merger", layout="wide")
st.title('🔗 매출 데이터 통합 결과')

@st.cache_data
def load_sales_data(file_input):
    try:
        return pd.read_excel(file_input, sheet_name=None)
    except Exception as e:
        st.error(f"파일 로드 중 오류 발생: {e}")
        return None

file_path = 'sales.xlsx'
all_sheets = None

# 1. 로컬 파일 확인 또는 업로드 안내
if os.path.exists(file_path):
    all_sheets = load_sales_data(file_path)
else:
    uploaded_file = st.sidebar.file_uploader("sales.xlsx 파일을 업로드해주세요", type=['xlsx'])
    if uploaded_file:
        all_sheets = load_sales_data(uploaded_file)
    else:
        st.warning(f"⚠️ '{file_path}' 파일을 찾을 수 없습니다. 왼쪽 사이드바에서 파일을 업로드하거나 파일 위치를 확인해주세요.")

fact_sheet_name = '예제01-매출내역'

if all_sheets and fact_sheet_name in all_sheets:
    merged_df = all_sheets[fact_sheet_name].copy()
    st.info(f"'{fact_sheet_name}' 테이블을 기준으로 병합을 시작합니다.")

    # 2. 나머지 시트(차원 테이블)들과 병합 수행
    for sheet_name, dim_df in all_sheets.items():
        if sheet_name == fact_sheet_name:
            continue
        
        # 공통 컬럼(Join Key) 찾기
        common_keys = list(set(merged_df.columns) & set(dim_df.columns))
        
        if common_keys:
            key = common_keys[0] # 첫 번째 공통 컬럼을 키로 사용
            
            # 데이터 타입 일치화 및 공백 제거 (조인 실패 방지)
            merged_df[key] = merged_df[key].astype(str).str.strip()
            dim_df_clean = dim_df.copy()
            dim_df_clean[key] = dim_df_clean[key].astype(str).str.strip()
            
            # Left Join 수행 (매출내역의 모든 행 유지)
            merged_df = pd.merge(merged_df, dim_df_clean, on=key, how='left', suffixes=('', f'_{sheet_name}'))
            st.write(f"✅ '{sheet_name}' 테이블이 '{key}' 컬럼을 통해 병합되었습니다.")

    # 3. 데이터 분석 섹션
    st.divider()
    
    # 상단 KPI 메트릭
    numeric_cols = merged_df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = merged_df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 판매 건수", f"{len(merged_df):,} 건")
    
    if '금액' in merged_df.columns:
        with col2:
            total_sales = merged_df['금액'].sum()
            st.metric("총 매출액", f"{total_sales:,.0f} 원")
        with col3:
            avg_sales = merged_df['금액'].mean()
            st.metric("평균 판매 단가", f"{avg_sales:,.0f} 원")

    # 분석 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📋 통합 데이터", "📊 요약 통계", "📈 카테고리 분석", "🧩 피벗 분석"])

    with tab1:
        st.subheader("통합 데이터프레임")
        st.dataframe(merged_df, use_container_width=True)
        st.success(f"총 {len(merged_df)}건의 데이터가 병합되었습니다.")

    with tab2:
        st.subheader("수치형 데이터 통계")
        st.dataframe(merged_df.describe(), use_container_width=True)
        
        if len(numeric_cols) >= 2:
            st.subheader("변수 간 상관관계")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(merged_df[numeric_cols].corr(), annot=True, cmap='coolwarm', ax=ax)
            st.pyplot(fig)
            plt.close(fig)

    with tab3:
        st.subheader("동적 카테고리 분석")
        if cat_cols and numeric_cols:
            c1, c2 = st.columns(2)
            with c1:
                group_key = st.selectbox("분석 기준(카테고리):", cat_cols, index=0)
            with c2:
                value_key = st.selectbox("분석 대상(수치):", numeric_cols, 
                                        index=numeric_cols.index('금액') if '금액' in numeric_cols else 0)
            
            # 그룹화 계산
            analysis_df = merged_df.groupby(group_key)[value_key].sum().sort_values(ascending=False).reset_index()
            
            col_chart, col_table = st.columns([2, 1])
            with col_chart:
                st.bar_chart(data=analysis_df, x=group_key, y=value_key)
            with col_table:
                st.write(f"{group_key}별 {value_key} 합계")
                st.dataframe(analysis_df, use_container_width=True)
        else:
            st.info("분석할 수 있는 카테고리 또는 수치 데이터가 부족합니다.")

    with tab4:
        st.subheader("데이터 피벗 테이블")
        if len(cat_cols) >= 2 and numeric_cols:
            row_key = st.selectbox("행(Row) 선택:", cat_cols, index=0)
            col_key = st.selectbox("열(Column) 선택:", cat_cols, index=1 if len(cat_cols) > 1 else 0)
            val_key = st.selectbox("값(Value) 선택:", numeric_cols, key='pivot_val')
            
            pivot_res = merged_df.pivot_table(index=row_key, columns=col_key, values=val_key, aggfunc='sum').fillna(0)
            st.dataframe(pivot_res, use_container_width=True)
        else:
            st.info("피벗 분석을 위해 최소 2개의 카테고리 컬럼이 필요합니다.")

elif all_sheets and fact_sheet_name not in all_sheets:
    st.error(f"❌ 파일 내에 '{fact_sheet_name}' 시트가 존재하지 않습니다. (시트명 확인 필요)")