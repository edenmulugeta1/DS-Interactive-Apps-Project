import streamlit as st
from utils import page_header, get_summary, format_dates, get_category_totals, insight_card

page_header(
    "Dashboard",
    "See your balance, spending, and biggest category at a glance."
)

df = st.session_state.expenses.copy()
total_spent, remaining, top_category = get_summary(df)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Starting Balance", f"${st.session_state.starting_balance:,.2f}")

with col2:
    st.metric("Total Spent", f"${total_spent:,.2f}")

with col3:
    st.metric("Remaining Balance", f"${remaining:,.2f}")

if remaining < 0:
    st.error("You are over your starting balance.")
elif st.session_state.starting_balance > 0 and remaining < st.session_state.starting_balance * 0.25:
    st.warning("You are close to using most of your available funds.")
else:
    st.success("You are within your budget.")

st.divider()

left, right = st.columns([1.2, 1])

with left:
    with st.container(border=True):
        st.subheader("Recent Expenses")
        if df.empty:
            st.warning("No expenses yet. Add an expense to begin tracking.")
        else:
            recent = df.sort_values("date", ascending=False).head(7)
            st.dataframe(format_dates(recent), use_container_width=True, hide_index=True)

with right:
    category_totals = get_category_totals(df)

    if category_totals.empty:
        insight_card(
            "Quick Insight",
            "No spending yet",
            "Add your first expense to generate budget insights."
        )
    else:
        highest = category_totals.iloc[0]
        insight_card(
            "Top Spending Category",
            str(top_category),
            f"You have spent the most on {highest['category']}: ${highest['amount']:,.2f}."
        )

    with st.container(border=True):
        st.subheader("Budget Snapshot")
        if st.session_state.starting_balance > 0:
            percent_used = min(total_spent / st.session_state.starting_balance, 1.0)
            st.progress(percent_used)
            st.caption(f"{percent_used * 100:.1f}% of available funds used.")
        else:
            st.info("Set a starting balance to see progress.")