import streamlit as st
import pandas as pd
import plotly.express as px
from utils import page_header, format_dates, get_category_totals

page_header(
    "Spending Analysis",
    "Filter your expenses and use charts to understand where your money goes."
)

df = st.session_state.expenses.copy()

if df.empty:
    st.warning("No expense data available yet. Add expenses first.")
    st.stop()

df["date"] = pd.to_datetime(df["date"])
category_options = sorted(df["category"].dropna().unique())


def reset_analysis_filters():
    st.session_state.analysis_category_filter = category_options
    st.session_state.analysis_time_view = "All Data"
    st.session_state.show_analysis_table = True
    st.session_state.show_advanced_filters = False
    st.session_state.minimum_expense_filter = 0.0
    st.toast("Filters cleared!")


with st.container(border=True):
    st.subheader("Filters")

    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])

    with filter_col1:
        selected_categories = st.multiselect(
            "Categories",
            options=category_options,
            default=category_options,
            key="analysis_category_filter"
        )

    with filter_col2:
        time_view = st.radio(
            "Time View",
            ["All Data", "This Week", "This Month"],
            key="analysis_time_view"
        )

    with filter_col3:
        show_table = st.toggle(
            "Show Table",
            value=True,
            key="show_analysis_table"
        )

    show_advanced = st.toggle(
        "Show Advanced Filters",
        value=False,
        key="show_advanced_filters"
    )

    if show_advanced:
        st.caption("Advanced filters help users narrow spending patterns more precisely.")

        adv1, adv2 = st.columns(2)

        with adv1:
            min_amount = st.number_input(
                "Minimum Expense Amount ($)",
                min_value=0.0,
                value=0.0,
                step=5.0,
                key="minimum_expense_filter"
            )

        with adv2:
            compare_category = st.selectbox(
                "Compare Against Category",
                options=category_options,
                key="compare_category_filter"
            )
    else:
        min_amount = 0.0
        compare_category = None

    st.button(
        "Reset Filters",
        key="reset_filters_button",
        on_click=reset_analysis_filters
    )

if not selected_categories:
    st.warning("Please select at least one category.")
    st.stop()

filtered_df = df[df["category"].isin(selected_categories)]
filtered_df = filtered_df[filtered_df["amount"] >= min_amount]

today = pd.Timestamp.today().normalize()

if time_view == "This Week":
    start_week = today - pd.Timedelta(days=7)
    filtered_df = filtered_df[filtered_df["date"] >= start_week]

elif time_view == "This Month":
    filtered_df = filtered_df[
        (filtered_df["date"].dt.month == today.month) &
        (filtered_df["date"].dt.year == today.year)
    ]

if filtered_df.empty:
    st.warning("No expenses match your current filters.")
    st.stop()

if show_advanced and compare_category not in selected_categories:
    st.info("Your comparison category is not part of the selected filters.")

category_totals = get_category_totals(filtered_df)

st.success(f"Loaded {len(filtered_df)} matching expense records.")

st.divider()

chart_col1, chart_col2 = st.columns([1.15, 1])

with chart_col1:
    with st.container(border=True):
        st.subheader("Spending by Category")

        with st.spinner("Building category chart..."):
            fig_bar = px.bar(
                category_totals,
                x="category",
                y="amount",
                color="category",
                text="amount",
                labels={"category": "Category", "amount": "Amount Spent ($)"},
                title="Total Spending by Category",
                color_discrete_sequence=[
                    "#232D4B",
                    "#E57200",
                    "#007BAC",
                    "#F9DCBF",
                    "#6B7280",
                    "#A8C4E5"
                ]
            )
            fig_bar.update_traces(texttemplate="$%{text:.2f}", textposition="outside")
            fig_bar.update_layout(showlegend=False, yaxis_title="Amount Spent ($)", xaxis_title="")
            st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
    with st.container(border=True):
        st.subheader("Spending Distribution")

        fig_pie = px.pie(
            category_totals,
            names="category",
            values="amount",
            title="Share of Spending by Category",
            hole=0.45,
            color_discrete_sequence=[
                "#232D4B",
                "#E57200",
                "#007BAC",
                "#F9DCBF",
                "#6B7280",
                "#A8C4E5"
            ]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

monthly = (
    filtered_df.assign(month=filtered_df["date"].dt.to_period("M").astype(str))
    .groupby("month", as_index=False)["amount"]
    .sum()
)

with st.container(border=True):
    st.subheader("Spending Over Time")

    fig_line = px.line(
        monthly,
        x="month",
        y="amount",
        markers=True,
        title="Monthly Spending Trend",
        labels={"month": "Month", "amount": "Amount Spent ($)"}
    )
    fig_line.update_traces(line_color="#E57200", marker_color="#232D4B", line_width=4)
    st.plotly_chart(fig_line, use_container_width=True)

if show_table:
    with st.container(border=True):
        st.subheader("Filtered Expense Data")
        st.dataframe(
            format_dates(filtered_df.sort_values("date", ascending=False)),
            use_container_width=True,
            hide_index=True
        )