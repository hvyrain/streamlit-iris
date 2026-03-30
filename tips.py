import seaborn as sns
import streamlit as st
import sqlite3

@st.cache_data
def load_data():
    return sns.load_dataset('tips')

@st.cache_data
def save_to_db():
    tips = load_data()
    
    # SQLite 데이터베이스 연결
    conn = sqlite3.connect('sns.db')
    cursor = conn.cursor()
    
    # tips 테이블 생성 (기존 테이블 삭제 후 재생성)
    cursor.execute('''DROP TABLE IF EXISTS tips''')
    cursor.execute('''
        CREATE TABLE tips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_bill REAL,
            tip REAL,
            sex TEXT,
            smoker TEXT,
            day TEXT,
            time TEXT,
            size INTEGER
        )
    ''')
    
    # 데이터 삽입
    tips.to_sql('tips', conn, if_exists='replace', index=False)
    
    conn.commit()
    conn.close()
    
    return tips

# 데이터 로드 및 DB에 저장
tips = save_to_db()

st.title('Tips 데이터 분석')

st.header('Bill과 Tip의 관계')
st.scatter_chart(tips, x="total_bill", y="tip")

st.header('데이터 확인')
if st.checkbox('데이터프레임 보기'):
    st.dataframe(tips)

st.info('✓ 데이터가 sns.db 파일의 tips 테이블에 저장되었습니다.')
