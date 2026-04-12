import streamlit as st
from datetime import datetime
import requests

API_URL = "http://localhost:8000"


def add_update_tab():
    # 1. Date Selection
    selected_date = st.date_input("Enter Date", datetime(2024, 8, 1), label_visibility="collapsed")

    # 2. Fetch existing data from MySQL via Backend
    response = requests.get(f"{API_URL}/expenses/{selected_date}")
    if response.status_code == 200:
        existing_expenses = response.json()
    else:
        st.error("Failed to retrieve expenses")
        existing_expenses = []

    categories = ["Rent", "Food", "Shopping", "Entertainment", "Other"]

    # 3. Main Expense Form
    with st.form(key=f"expense_form_{selected_date}"):

        # --- Header Row ---
        h_col1, h_col2, h_col3, h_col4 = st.columns([2, 2, 3, 3])
        with h_col1:
            st.subheader("Amount")
        with h_col2:
            st.subheader("Category")
        with h_col3:
            st.subheader("Notes")
        with h_col4:
            st.subheader("AI Predict")

        expenses = []

        # --- 5-Row Expense Grid ---
        for i in range(5):
            # Load values from DB or use defaults
            if i < len(existing_expenses):
                db_amount   = float(existing_expenses[i]["amount"])
                db_category = existing_expenses[i]["category"]
                db_notes    = existing_expenses[i]["notes"]
            else:
                db_amount   = 0.0
                db_category = "Other"
                db_notes    = ""

            col1, col2, col3, col4 = st.columns([2, 2, 3, 3])

            with col1:
                amount_input = st.number_input(
                    label="Amount", min_value=0.0, step=1.0, value=db_amount,
                    key=f"amount_{selected_date}_{i}", label_visibility="collapsed"
                )

            with col3:
                notes_input = st.text_input(
                    label="Notes", value=db_notes,
                    key=f"notes_{selected_date}_{i}", label_visibility="collapsed"
                )

            # --- TWO AI BUTTONS with short labels ---
            with col4:
                btn_local_col, btn_gemini_col = st.columns(2)

                with btn_local_col:
                    # ✨ Local NLP button — fast, offline
                    local_clicked = st.form_submit_button(
                        "✨ Local",
                        key=f"l_btn_{i}",
                        use_container_width=True,
                        help="Fast offline prediction using local NLP model"
                    )
                    if local_clicked:
                        if notes_input:
                            try:
                                res = requests.get(
                                    f"{API_URL}/predict-category/{notes_input}?use_gemini=false"
                                )
                                if res.status_code == 200:
                                    prediction = res.json()["suggested_category"]
                                    st.session_state[f"ai_res_{i}"]    = prediction
                                    st.session_state[f"ai_toast_{i}"]  = f"✨ AI Suggests: {prediction}"
                                    st.rerun()
                            except Exception:
                                st.error("Server Down — is server.py running?")
                        else:
                            st.warning("Enter a note first!")

                with btn_gemini_col:
                    # 🤖 Gemini button — cloud AI
                    gemini_clicked = st.form_submit_button(
                        "🤖 Gemini",
                        key=f"g_btn_{i}",
                        use_container_width=True,
                        help="Cloud prediction using Google Gemini LLM"
                    )
                    if gemini_clicked:
                        if notes_input:
                            try:
                                with st.spinner("Gemini thinking..."):
                                    res = requests.get(
                                        f"{API_URL}/predict-category/{notes_input}?use_gemini=true"
                                    )
                                    if res.status_code == 200:
                                        prediction = res.json()["suggested_category"]
                                        st.session_state[f"ai_res_{i}"]   = prediction
                                        # ← restored from your old code
                                        st.session_state[f"ai_toast_{i}"] = f"🤖 AI Suggests: {prediction}"
                                        st.rerun()
                            except Exception:
                                st.error("Server Down — is server.py running?")
                        else:
                            st.warning("Enter a note first!")

            # Show toast AFTER rerun — outside the form submit blocks
            toast_key = f"ai_toast_{i}"
            if toast_key in st.session_state:
                st.toast(st.session_state[toast_key])
                del st.session_state[toast_key]   # show once only, then clear

            # Determine which category to show (AI prediction takes priority over DB value)
            current_display_cat = st.session_state.get(f"ai_res_{i}", db_category)

            with col2:
                # Dynamic key forces dropdown to update instantly when AI predicts
                category_input = st.selectbox(
                    label="Category",
                    options=categories,
                    index=categories.index(current_display_cat) if current_display_cat in categories else 0,
                    key=f"cat_select_{selected_date}_{i}_{current_display_cat}",
                    label_visibility="collapsed"
                )

            expenses.append({
                "amount":   amount_input,
                "category": category_input,
                "notes":    notes_input
            })

        # --- Submit All Changes ---
        submit_all = st.form_submit_button("Submit All Changes")
        if submit_all:
            filtered_expenses = [e for e in expenses if e["amount"] > 0]
            save_res = requests.post(f"{API_URL}/expenses/{selected_date}", json=filtered_expenses)

            if save_res.status_code == 200:
                st.success("Database updated successfully!")
                # Clear all AI memory after saving
                for k in list(st.session_state.keys()):
                    if k.startswith("ai_res_") or k.startswith("ai_toast_"):
                        del st.session_state[k]
                st.rerun()
            else:
                st.error("Failed to update database.")