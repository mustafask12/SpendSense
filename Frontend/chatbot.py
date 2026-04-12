import streamlit as st
import os
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_google_genai import ChatGoogleGenerativeAI
from Backend.logging_setup import setup_logger  # Updated to use the bridge

# Use the professional logger
logger = setup_logger("gemini_chatbot")


def financial_advisor_bot():
    st.subheader("🤖 Gemini AI Financial Advisor")
    st.write("Ask questions about your spending in natural language.")

    # Database connection
    db_uri = "mysql+pymysql://root:root@localhost/expense_manager"

    try:
        db = SQLDatabase.from_uri(db_uri)
    except Exception as e:
        st.error("Database Connection Failed. Ensure MySQL is running.")
        logger.error(f"DB Connection Error: {e}")
        return

    # --- API KEY LOGIC ---
    # Check .env first, then fallback to sidebar
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

    if api_key:
        try:
            # Change "gemini-2.0-flash" to "gemini-2.5-flash-lite"
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", google_api_key=api_key)
            db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)

            user_query = st.chat_input("Ex: What was my highest expense in August?")

            if user_query:
                logger.info(f"User Query: {user_query}")
                with st.chat_message("user"):
                    st.write(user_query)

                with st.chat_message("assistant"):
                    with st.spinner("Gemini is thinking..."):
                        response = db_chain.run(user_query)
                        st.write(response)
                        logger.info("Gemini response successful.")
        except Exception as e:
            st.error(f"AI Error: {e}")
            logger.error(f"Chatbot error: {e}")
    else:
        st.info("💡 Please enter your Gemini API Key in the sidebar or .env file.")