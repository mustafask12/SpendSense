import sys
import os

# 1. This tells Python to look one folder UP and find 'Backend'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from add_update_ui import add_update_tab
from analytics_by_category import analytics_category_tab
from analytics_by_months import analytics_months_tab
from chatbot import financial_advisor_bot

# Page config — must be first Streamlit call
st.set_page_config(
    page_title="SpendSense",
    page_icon="💰",
    layout="wide"
)

st.title("💰 SpendSense — AI-Powered Finance Tracker")
tab1, tab2, tab3, tab4 = st.tabs(["Add/Update", "Analytics By Category", "Analytics By Months", "🤖 AI Advisor"])

with tab1:
    add_update_tab()
with tab2:
    analytics_category_tab()
with tab3:
    analytics_months_tab()
with tab4:
    financial_advisor_bot()

