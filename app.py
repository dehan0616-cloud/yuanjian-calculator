import streamlit as st
import math
import pandas as pd

# 網頁設定：寬版模式
st.set_page_config(page_title="遠見沐景 | 專業財務試算", layout="wide")

# --- 1. 全域字體與樣式放大 ---
st.markdown("""
    <style>
    html, body, [class*="View"] { font-size: 22px !important; }
    h1 { font-size: 50px !important; font-weight: 800 !important; color: #1E3A8A; }
    h2 { font-size: 38px !important; font-weight: 700 !important; }
    h3 { font-size: 30px !important; }
    [data-testid="stMetricLabel"] { font-size: 24px !important; }
    [data-testid="stMetricValue"] { font-size: 48px !important; font-weight: 700 !important; }
    .stNumberInput input, .stSelectbox div, .stButton button { font-size: 22px !important; }
    .stDataFrame td, .stDataFrame th { font-size: 24px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏢 遠見沐景 | 專屬購屋財務報告")
st.markdown("---")

# --- 2. 側邊欄：輸入區 ---
with st.sidebar:
    st.header("📋 參數輸入")
    
    # 戶別選擇 (已移除「連動代收款」文字)
    unit_type = st.selectbox("🏠 選擇戶別", ["A1", "A2", "A3", "A5", "B1", "B2", "B3"])
    
    total_price = st.number_input("房屋總價 (萬元)", min_value=100, value=1524, step=1)
    
    deposit = 10 
    st.write(f"💰 訂金：固定 **{deposit} 萬**")
    signing = st.number_input("✍️ 簽約金 (萬元)", min_value=0, value=40, step=1)
    
    st.divider()
    
    st.header("🏦 房貸設定")
    loan_years = st.number_input("貸款年限 (年)", min_value=10, max_value=40, value=30)
    interest_rate = st.number_input("房貸利率 (%)", min_value=1.0, max_value=6.0, value=2.18, step=0.01)

# --- 3. 代收款判斷邏輯 ---
escrow_map = {"A1": 25, "A2": 25, "B1": 25, "B2": 25, "A3": 23, "A5": 23, "B3": 27}
escrow_fee = escrow_map[unit_type]

# --- 4. 貸款成數快速選擇 ---
st.subheader("🎯 點擊切換貸款成數")
ratio_map = {
    "3成": 0.3, "4成": 0.4, "5成": 0.5, "6成": 0.6, 
    "7成": 0.7, "7.5成": 0.75, "8成": 0.8, "8.5成": 0.85, "9成": 0.9
}
selected_label = st.radio("選擇成數：", options=list(ratio_map.keys()), index=6, horizontal=True, label_visibility="collapsed")
loan_ratio = ratio_map[selected_label]

# --- 5. 核心計算邏輯 (含進位/捨去) ---
# 貸款金額：無條件捨去
loan_amt = math.floor(total_price * loan_ratio)
# 自備款總額：總價 - 貸款
down_payment = total_price - loan_amt

# 拆款：扣除訂簽後，用印與完稅平分
remaining_down = down_payment - deposit - signing
seal_payment = math.ceil(remaining_down / 2)
tax_payment = math.floor(remaining_down / 2)

# 月繳計算
loan_yuan = loan_amt * 10000
monthly_rate = (interest_rate / 100) / 12
months = loan_years * 12
if monthly_rate > 0:
    monthly_pay = loan_yuan * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
else:
    monthly_pay = loan_yuan / months

# --- 6. 結果展示區 ---
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f'''
        <div style="font-size: 24px; color: #31333F;">🏠 房屋總價</div>
        <div style="font-size: 48px; font-weight: 800; color: #E53935;">{total_price:,} 萬</div>
    ''', unsafe_allow_html=True)
with col2:
    st.metric("💼 自備款總額", f"{down_payment:,} 萬", f"{selected_label}")
with col3:
    st.metric("🏦 銀行貸款", f"{loan_amt:,} 萬")
with col4:
    st.metric("📅 預估月繳", f"{int(monthly_pay):,} 元", f"{loan_years}年 / {interest_rate}%")
with col5:
    st.metric("🧾 代收款", f"{escrow_fee} 萬", f"{unit_type} 戶別")

st.markdown("<br>", unsafe_allow_html=True)

# 下方明細表格
col_left, spacer, col_right = st.columns([1, 0.1, 1])

with col_left:
    st.subheader("📝 資金分配明細")
    
    # 修改項目：1.合計改為5.貸款 2.移除特殊背景與顏色
    custom_table = f"""
    <table style="width: 100%; font-size: 24px; border-collapse: collapse; text-align: left; background-color: white;">
        <tr style="border-bottom: 2px solid #ddd;">
            <th style="padding: 12px; color: #555;">付款階段</th>
            <th style="padding: 12px; text-align: right; color: #555;">金額 (萬元)</th>
        </tr>
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 12px;">1. 訂金</td>
            <td style="padding: 12px; text-align: right;">{deposit}</td>
        </tr>
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 12px;">2. 簽約金</td>
            <td style="padding: 12px; text-align: right;">{signing}</td>
        </tr>
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 12px;">3. 用印款</td>
            <td style="padding: 12px; text-align: right;">{seal_payment}</td>
        </tr>
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 12px;">4. 完稅款</td>
            <td style="padding: 12px; text-align: right;">{tax_payment}</td>
        </tr>
        <tr style="border-bottom: 2px solid #ddd; font-weight: bold;">
            <td style="padding: 12px;">5. 貸款</td>
            <td style="padding: 12px; text-align: right; font-size: 28px;">{loan_amt}</td>
        </tr>
    </table>
    """
    st.markdown(custom_table, unsafe_allow_html=True)

with col_right:
    st.subheader("🏦 銀行貸款資訊")
    loan_data = {
        "資訊項目": ["貸款成數", "貸款總額", "還款年限", "房貸利率", "每月負擔"],
        "內容": [selected_label, f"{loan_amt} 萬元", f"{loan_years} 年", f"{interest_rate} %", f"約 {int(monthly_pay):,} 元"]
    }
    st.table(pd.DataFrame(loan_data))

st.markdown("---")
st.caption("※ 本試算結果僅供參考，實際核貸成數與利率依銀行最終審核結果為準。")