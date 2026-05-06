import pandas as pd
import streamlit as st
import requests
from pathlib import Path

DATA_FILE = Path("expense.csv")


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE) if DATA_FILE.exists() else pd.DataFrame(
        columns=["amount", "category", "subcategory", "date", "notes"]
    )

    if "subcategory" not in df.columns:
        df["subcategory"] = ""

    if not df.empty:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["category"] = df["category"].fillna("Other")
        df["subcategory"] = df["subcategory"].fillna("")
        df["notes"] = df["notes"].fillna("")
        df = df.dropna(subset=["amount", "date"])

    return df


def save_data(df):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df.to_csv(DATA_FILE, index=False)


def initialize_state():
    if "expenses" not in st.session_state:
        st.session_state.expenses = load_data()
    if "starting_balance" not in st.session_state:
        st.session_state.starting_balance = 2000.0


def add_expense(amount, category, subcategory, date_value, notes):
    new_expense = pd.DataFrame([{
        "amount": amount,
        "category": category,
        "subcategory": subcategory,
        "date": pd.to_datetime(date_value),
        "notes": notes
    }])

    st.session_state.expenses = pd.concat(
        [st.session_state.expenses, new_expense],
        ignore_index=True
    )
    save_data(st.session_state.expenses)


def get_summary(df):
    total_spent = float(df["amount"].sum()) if not df.empty else 0.0
    remaining = st.session_state.starting_balance - total_spent
    top_category = "None" if df.empty else df.groupby("category")["amount"].sum().idxmax()
    return total_spent, remaining, top_category


def get_category_totals(df):
    if df.empty:
        return pd.DataFrame(columns=["category", "amount"])

    return (
        df.groupby("category", as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
    )


def format_dates(df):
    df = df.copy()
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    return df


def page_header(title, subtitle):
    st.markdown(f"<h1 class='page-title'>{title}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='page-subtitle'>{subtitle}</p>", unsafe_allow_html=True)


def insight_card(label, title, text):
    st.markdown(
        f"""
        <div class="accent-card">
            <div class="mini-label">{label}</div>
            <div class="big-insight">{title}</div>
            <p>{text}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


@st.cache_data(ttl=3600)
def lookup_food_product(barcode):
    # Cache for 1 hour to avoid repeated API calls and respect rate limits.
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    headers = {"User-Agent": "HoosOnBudget/1.0 (student-project)"}

    try:
        response = requests.get(url, headers=headers, timeout=8)

        if response.status_code == 401:
            return None, "API key is missing or invalid."
        if response.status_code == 404:
            return None, "No results found for your search."
        if response.status_code == 429:
            return None, "API limit reached. Please wait a minute and try again."
        if response.status_code >= 500:
            return None, "The service is temporarily unavailable. Please try again later."

        data = response.json()
        if not data or data.get("status") == 0:
            return None, "Your search returned no results. Try a different barcode."

        return data.get("product", {}), None

    except requests.exceptions.Timeout:
        return None, "Could not connect. Check your internet connection."
    except requests.exceptions.RequestException:
        return None, "Could not connect. Check your internet connection."
    except ValueError:
        return None, "Your search returned no results. Try broader terms."


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --uva-navy: #232D4B;
            --uva-orange: #E57200;
        }

        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #F6F8FC 0%, #FFFFFF 45%, #FFF7EF 100%);
        }

        .block-container {
            padding-top: 2.5rem;
            padding-bottom: 3rem;
            max-width: 1250px;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #232D4B 0%, #1F2741 100%);
        }

        section[data-testid="stSidebar"] * {
            color: white !important;
        }

        .page-title {
            font-size: 2.6rem;
            font-weight: 900;
            color: var(--uva-navy);
            line-height: 1.35;
            padding-top: 1rem;
            margin-bottom: 0.2rem;
        }

        .page-subtitle {
            font-size: 1.15rem;
            color: #4B5563;
            margin-bottom: 1.5rem;
        }

        .accent-card {
            background: linear-gradient(135deg, #FFF3E8 0%, #FFFFFF 65%);
            border-left: 8px solid var(--uva-orange);
            border-radius: 22px;
            padding: 1.5rem;
            box-shadow: 0 12px 30px rgba(35, 45, 75, 0.08);
        }

        .mini-label {
            text-transform: uppercase;
            color: var(--uva-orange);
            font-weight: 800;
            letter-spacing: 0.08em;
            font-size: 0.8rem;
        }

        .big-insight {
            font-size: 1.7rem;
            font-weight: 850;
            color: var(--uva-navy);
            margin: 0.4rem 0;
        }

        div[data-testid="stMetric"] {
            background: white;
            border: 1px solid #E5E7EB;
            border-top: 6px solid var(--uva-orange);
            border-radius: 20px;
            padding: 1.25rem;
            box-shadow: 0 12px 24px rgba(35, 45, 75, 0.08);
            min-height: 120px;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.9rem;
            color: var(--uva-navy);
            font-weight: 850;
            white-space: nowrap;
        }

        div[data-testid="stMetricLabel"] {
            font-size: 0.95rem;
            color: #374151;
            font-weight: 700;
            white-space: nowrap;
        }

        .stButton > button {
            background: linear-gradient(90deg, #E57200, #F39C12);
            color: white;
            border: none;
            border-radius: 14px;
            padding: 0.7rem 1.2rem;
            font-weight: 800;
        }

        .stButton > button:hover {
            background: #C65F00;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )