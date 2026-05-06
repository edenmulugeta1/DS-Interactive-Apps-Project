import streamlit as st
from utils import initialize_state, apply_global_styles

st.set_page_config(
    page_title="HoosOnBudget",
    page_icon="💸",
    layout="wide"
)

initialize_state()
apply_global_styles()

st.sidebar.markdown("## 💸 HoosOnBudget")
st.sidebar.caption("College Budgeting Assistant")
st.sidebar.divider()
st.sidebar.markdown(
    """
    **Quick goal:**  
    Track spending, understand patterns, and manage available funds.
    """
)

pages = [
    st.Page("pages/1_Dashboard.py", title="Dashboard", icon="🏠"),
    st.Page("pages/2_Add_Expense.py", title="Add Expense", icon="➕"),
    st.Page("pages/3_Spending_Analysis.py", title="Spending Analysis", icon="📊"),
    st.Page("pages/4_Budget_Planner.py", title="Budget Planner", icon="💰"),
    st.Page("pages/5_Grocery_Check.py", title="Grocery Check", icon="🛒"),
    st.Page("pages/6_Budget_Assistant.py", title="Budget Assistant", icon="🤖"),
]

pg = st.navigation(pages)
pg.run()