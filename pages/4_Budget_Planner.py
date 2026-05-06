import streamlit as st
from utils import page_header, get_summary, get_category_totals

page_header(
    "Budget Planner",
    "Set your available funds and monitor how much you have left."
)

df = st.session_state.expenses.copy()
total_spent, remaining, top_category = get_summary(df)

mode = st.radio(
    "Budget Mode",
    ["Simple Budget", "Category Limit"],
    horizontal=True,
    key="budget_mode"
)

input_col, insight_col = st.columns([0.95, 1.3])

with input_col:
    with st.container(border=True):
        st.subheader("Set Available Funds")

        new_balance = st.number_input(
            "Starting Balance ($)",
            min_value=0.0,
            value=float(st.session_state.starting_balance),
            step=25.0,
            key="budget_starting_balance"
        )

        savings_goal = st.slider(
            "Target amount to keep unspent ($)",
            min_value=0,
            max_value=int(max(new_balance, 1)),
            value=min(100, int(max(new_balance, 1))),
            step=10,
            key="savings_goal_slider"
        )

        if mode == "Category Limit":
            category_totals = get_category_totals(df)
            category_options = sorted(df["category"].dropna().unique()) if not df.empty else ["Groceries"]

            limit_category = st.selectbox(
                "Category to Limit",
                options=category_options,
                key="budget_limit_category"
            )

            category_limit = st.number_input(
                "Category Limit ($)",
                min_value=0.0,
                value=100.0,
                step=10.0,
                key="category_limit_amount"
            )

        if st.button("Update Budget", key="update_budget_button"):
            if new_balance <= 0:
                st.error("Starting balance must be greater than $0.")
                st.stop()

            st.session_state.starting_balance = new_balance
            st.success("Budget updated successfully.")
            st.toast("Budget updated!")
            total_spent, remaining, top_category = get_summary(df)

with insight_col:
    with st.container(border=True):
        st.subheader("Budget Status")

        col1, col2, col3 = st.columns([1.2, 1, 1.2])
        col1.metric("Balance", f"${st.session_state.starting_balance:,.2f}")
        col2.metric("Spent", f"${total_spent:,.2f}")
        col3.metric("Left", f"${remaining:,.2f}")

        if remaining < 0:
            st.error("You have spent more than your starting balance.")
        elif remaining < savings_goal:
            st.warning("You are below your target unspent amount.")
        else:
            st.success("You are still above your target unspent amount.")

        if mode == "Category Limit" and not df.empty:
            spent_in_category = float(df[df["category"] == limit_category]["amount"].sum())

            st.divider()
            st.subheader(f"{limit_category} Limit")

            progress = min(spent_in_category / category_limit, 1.0) if category_limit > 0 else 0
            st.progress(progress)

            if spent_in_category > category_limit:
                st.warning(f"You are over your {limit_category} limit.")
            else:
                st.info(f"You have spent ${spent_in_category:,.2f} of your ${category_limit:,.2f} {limit_category} limit.")

st.divider()

with st.container(border=True):
    st.subheader("Budget Progress")

    if st.session_state.starting_balance > 0:
        progress_value = min(total_spent / st.session_state.starting_balance, 1.0)
        st.progress(progress_value)
        st.caption(f"You have used {progress_value * 100:.1f}% of your starting balance.")
    else:
        st.info("Enter a starting balance to see progress.")

category_totals = get_category_totals(df)

with st.expander("Category Tip"):
    if category_totals.empty:
        st.write("Add expenses to receive a category-based budget tip.")
    else:
        highest = category_totals.iloc[0]
        st.write(
            f"Your highest category is **{highest['category']}** at "
            f"${highest['amount']:,.2f}. Consider setting a smaller limit for this category first."
        )