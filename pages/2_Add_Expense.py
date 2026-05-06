import streamlit as st
from datetime import date
from utils import page_header, add_expense, format_dates, get_summary

page_header(
    "Add Expense",
    "Quickly log a purchase and keep your spending record updated."
)

df = st.session_state.expenses.copy()
total_spent, remaining, top_category = get_summary(df)

m1, m2, m3 = st.columns(3)
m1.metric("Current Spent", f"${total_spent:,.2f}")
m2.metric("Remaining", f"${remaining:,.2f}")
m3.metric("Top Category", top_category)

st.divider()

subcategory_map = {
    "Food": ["Dining Out", "Coffee", "Snacks", "Takeout"],
    "Groceries": ["Produce", "Pantry", "Frozen", "Household"],
    "Transport": ["Uber/Lyft", "Bus", "Metro", "Gas"],
    "Entertainment": ["Movies", "Events", "Subscriptions"],
    "School": ["Books", "Supplies", "Printing"],
    "Personal": ["Clothing", "Skincare", "Laundry"],
    "Other": ["Other"]
}

categories = list(subcategory_map.keys())


def category_changed():
    st.session_state.expense_subcategory = subcategory_map[st.session_state.expense_category][0]
    st.session_state.custom_category = ""
    st.toast("Category changed. Subcategory options updated.")


form_col, table_col = st.columns([0.95, 1.3])

with form_col:
    with st.container(border=True):
        st.subheader("New Expense")
        st.caption("Add only the purchase details you need. Custom categories are supported.")

        selected_category = st.selectbox(
            "Category",
            categories,
            key="expense_category",  # key lets the on_change callback reset dependent subcategory choices
            on_change=category_changed
        )

        subcategory_options = subcategory_map[selected_category]

        selected_subcategory = st.selectbox(
            "Subcategory",
            subcategory_options,
            key="expense_subcategory"  # key stores the dependent dropdown value across reruns
        )

        custom_category = ""
        if selected_category == "Other":
            custom_category = st.text_input(
                "Custom Category",
                placeholder="Example: Coffee, Books, Subscriptions",
                key="custom_category"
            )

        with st.form("expense_form", clear_on_submit=True):
            amount = st.number_input(
                "Expense Amount ($)",
                min_value=0.0,
                step=1.0,
                key="expense_amount"  # key keeps the amount input stable inside the form
            )

            expense_date = st.date_input(
                "Date",
                value=date.today(),
                key="expense_date"
            )

            notes = st.text_input(
                "Notes",
                placeholder="Example: lunch, Uber, snacks",
                key="expense_notes"
            )

            submitted = st.form_submit_button("Add Expense")

        if submitted:
            if amount <= 0:
                st.error("Please enter an amount greater than $0.")
                st.stop()

            if selected_category == "Other" and custom_category.strip() == "":
                st.error("Please enter a custom category or choose one from the list.")
                st.stop()

            final_category = (
                custom_category.strip().title()
                if selected_category == "Other"
                else selected_category
            )

            add_expense(amount, final_category, selected_subcategory, expense_date, notes)
            st.success("Expense added successfully. Your dashboard and charts are now updated.")
            st.toast("Expense added!")

with table_col:
    with st.container(border=True):
        st.subheader("Expense Log")
        st.caption("Most recent purchases appear first.")

        if st.session_state.expenses.empty:
            st.warning("No expenses have been added yet.")
        else:
            st.dataframe(
                format_dates(st.session_state.expenses.sort_values("date", ascending=False)),
                use_container_width=True,
                hide_index=True
            )