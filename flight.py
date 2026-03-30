import seaborn as sns
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# matplotlib에서 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

@st.cache_data
def load_data():
    flights = sns.load_dataset('flights')
    # 월 이름을 번호로 매핑
    month_mapping = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    flights['month_no'] = flights['month'].map(month_mapping)
    return flights

flights = load_data()

st.title('Flights 데이터 분석')

st.header('월별 항공사 승객 수 추이')
# 시계열 데이터로 변환
flights_sorted = flights.sort_values(['year', 'month']).reset_index(drop=True)
flights_sorted['date'] = flights_sorted['year'].astype(str) + '-' + flights_sorted['month'].astype(str)

# matplotlib으로 라인 차트와 추세선 표시
fig, ax = plt.subplots(figsize=(12, 5))

# 원본 데이터
x = np.arange(len(flights_sorted))
y = flights_sorted['passengers'].values
ax.plot(x, y, label='승객 수', linewidth=2)

# 추세선 계산 (1차 다항식)
coeffs = np.polyfit(x, y, 1)
trend = np.polyval(coeffs, x)
ax.plot(x, trend, 'r--', label='추세선', linewidth=2)

ax.set_xlabel('기간')
ax.set_ylabel('승객 수')
ax.legend()
ax.grid(True, alpha=0.3)
st.pyplot(fig)
plt.close(fig)

st.header('연도별 월별 승객 수')
# 월 번호를 인덱스로 사용하여 피벗 테이블 생성
pivot_data = flights.pivot_table(values='passengers', index='month_no', columns='year')
# 월 번호 순서대로 자동 정렬됨
st.bar_chart(pivot_data)

st.header('데이터 확인')
if st.checkbox('데이터프레임 보기'):
    st.dataframe(flights)

st.header('월별 승객수 분석 결과')

# 월별 평균 승객수
col1, col2, col3 = st.columns(3)
with col1:
    st.metric('전체 평균', f"{flights['passengers'].mean():.0f}")
with col2:
    st.metric('최고 승객수', f"{flights['passengers'].max()}")
with col3:
    st.metric('최저 승객수', f"{flights['passengers'].min()}")

# 월별 통계
st.subheader('월별 평균 승객수')
monthly_avg = flights.groupby('month_no')['passengers'].agg(['mean', 'min', 'max', 'std']).round(0)
monthly_avg.columns = ['평균', '최소', '최대', '표준편차']
st.dataframe(monthly_avg, use_container_width=True)

# 월별 최고/최저
monthly_stats = flights.groupby('month_no').agg({
    'passengers': ['mean', 'std'],
    'year': 'count'
}).round(0)
monthly_stats.columns = ['평균', '표준편차', '데이터 수']
st.subheader('월별 세부 통계')
st.dataframe(monthly_stats, use_container_width=True)

# 연도별 총 승객수
st.subheader('연도별 총 승객수')
yearly_total = flights.groupby('year')['passengers'].sum().reset_index()
yearly_total.columns = ['연도', '총 승객수']
st.bar_chart(yearly_total.set_index('연도'))

st.info('✓ Flights 데이터는 1949년부터 1960년까지의 국제 항공 승객 데이터입니다.')
