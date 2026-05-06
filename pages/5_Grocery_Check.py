import streamlit as st
from utils import page_header, lookup_food_product, get_summary

page_header(
    "Grocery Check",
    "Look up a grocery item and check how a planned purchase would affect your budget."
)

df = st.session_state.expenses.copy()
total_spent, remaining, top_category = get_summary(df)

col1, col2, col3 = st.columns(3)
col1.metric("Remaining Balance", f"${remaining:,.2f}")
col2.metric("Total Spent", f"${total_spent:,.2f}")
col3.metric("Top Category", top_category)

st.divider()

with st.container(border=True):
    st.subheader("Product Lookup")

    barcode = st.text_input(
        "Enter product barcode",
        placeholder="Example: 737628064502",
        key="food_barcode_input"
    )

    st.caption("Use a real grocery product barcode. Example: 737628064502")

    planned_price = st.number_input(
        "Planned Purchase Price ($)",
        min_value=0.0,
        value=0.0,
        step=1.0,
        key="planned_product_price"
    )

    search_clicked = st.button(
        "Check Product",
        key="check_product_button"
    )

if search_clicked:
    if barcode.strip() == "":
        st.error("Please enter a barcode before searching.")
        st.stop()

    if not barcode.strip().isdigit():
        st.error("Barcode should only contain numbers.")
        st.stop()

    if planned_price <= 0:
        st.error("Please enter the planned purchase price.")
        st.stop()

    with st.spinner("Looking up product information..."):
        product, error = lookup_food_product(barcode.strip())

    if error:
        if "no results" in error.lower() or "returned no results" in error.lower():
            st.warning(error)
        else:
            st.error(error)
        st.stop()

    product_name = product.get("product_name", "Unknown product")
    brand = product.get("brands", "Unknown brand")
    category = product.get("categories", "No category listed")
    nutriscore = product.get("nutriscore_grade", "Not available")
    image_url = product.get("image_front_url", "")

    st.success("Product found.")

    left, right = st.columns([1, 1.2])

    with left:
        if image_url:
            st.image(image_url, caption=product_name, use_container_width=True)
        else:
            st.info("No product image available.")

    with right:
        st.subheader(product_name)
        st.write(f"**Brand:** {brand}")
        st.write(f"**Product Category:** {category}")
        st.write(f"**Nutri-Score:** {str(nutriscore).upper()}")

        remaining_after = remaining - planned_price
        percent_of_remaining = (planned_price / remaining * 100) if remaining > 0 else 0

        st.metric("Balance After Purchase", f"${remaining_after:,.2f}")
        st.progress(min(percent_of_remaining / 100, 1.0))
        st.caption(f"This planned purchase would use {percent_of_remaining:.1f}% of your remaining balance.")

        if remaining_after < 0:
            st.error("Buying this product would put you over your available balance.")
        elif top_category == "Groceries":
            st.warning(
                "Groceries are already your highest spending category. "
                "This product may still be worth buying, but the app flags it so you can decide intentionally."
            )
        else:
            st.info(
                "This product fits within your remaining balance. "
                "Consider whether it supports your grocery needs before buying."
            )