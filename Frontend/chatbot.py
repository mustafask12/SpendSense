import streamlit as st
import os
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from Backend.logging_setup import setup_logger  # Updated to use the bridge

# Use the professional logger
logger = setup_logger("gemini_chatbot")

# Custom prompt forces clean MySQL syntax — fixes STRFTIME and markdown SQL block errors
MYSQL_PROMPT = """You are a friendly MySQL expert and personal finance advisor. Given an input question, create a syntactically correct MySQL query to run, then provide a clear, helpful explanation of the results.

CRITICAL RULES:
1. Use ONLY plain SQL — never wrap in ```sql or any markdown code blocks
2. Use MONTH(column) and YEAR(column) for date filtering — NEVER use STRFTIME
3. Use DATE_FORMAT(column, '%Y-%m') if needed for grouping by month
4. Return only the raw SQL query with no explanation
5. ALWAYS write ONE single SQL query only — never write multiple queries separated by semicolons
6. If the question has multiple parts, combine them into ONE query using subqueries or CTEs
7. For "worst month" or "highest spending month" queries, ALWAYS use this simple pattern:
   SELECT YEAR(expense_date) as yr, MONTHNAME(expense_date) as month_name, SUM(amount) as total
   FROM expenses GROUP BY yr, MONTH(expense_date), month_name ORDER BY total DESC LIMIT 1
8. NEVER use ROW_NUMBER() or RANK() — use ORDER BY + LIMIT instead


Use the following format:
Question: the input question
SQLQuery: the SQL query to run (plain SQL only, no markdown)
SQLResult: the result of the SQL query
Answer: Provide a detailed, conversational answer that explains the result in context. Include relevant insights, comparisons, or suggestions where appropriate. Do not just repeat the raw number — explain what it means.

{table_info}

Question: {input}
"""
prompt = PromptTemplate(
    input_variables=["input", "table_info"],
    template=MYSQL_PROMPT
)

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

    # Load API key from .env only
    api_key = os.getenv("GEMINI_API_KEY")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display previous messages
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if api_key:
        try:
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", google_api_key=api_key)
            db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True, prompt=prompt)

            user_query = st.chat_input("Ex: What was my highest expense in August?")

            if user_query:
                # Build context-aware query from chat history
                if st.session_state.chat_history:
                    history_text = "\n".join([
                        f"{m['role'].upper()}: {m['content']}"
                        for m in st.session_state.chat_history[-6:]  # last 3 turns
                    ])
                    full_query = f"""Previous conversation context:
{history_text}

IMPORTANT: If the conversation started with a specific year or time period,
maintain that filter throughout ALL follow-up questions unless the user
explicitly asks to change the time period.

Current question (answer this using the context above): {user_query}"""
                else:
                    full_query = user_query

                logger.info(f"User Query: {user_query}")
                st.session_state.chat_history.append({"role": "user", "content": user_query})

                with st.chat_message("user"):
                    st.write(user_query)

                with st.chat_message("assistant"):
                    with st.spinner("Gemini is thinking..."):

                        # Retry logic — on SQL error, ask Gemini to self-correct
                        max_retries = 2
                        response = None
                        last_error = None

                        for attempt in range(max_retries):
                            try:
                                if attempt > 0 and last_error:
                                    retry_query = f"""{full_query}

NOTE: Your previous SQL attempt failed with this error: {last_error}
Please write a simpler, corrected MySQL query. Avoid referencing CTE columns that weren't explicitly selected."""
                                    response = db_chain.run(retry_query)
                                else:
                                    response = db_chain.run(full_query)
                                break

                            except Exception as e:
                                last_error = str(e)
                                logger.warning(f"Attempt {attempt + 1} failed: {e}")

                                # Stop immediately on quota error — retrying wastes requests
                                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                                    response = "⚠️ Gemini API quota exceeded. You have hit the free tier limit (20 requests/day). Please wait until 1:30 PM IST for quota to reset."
                                    break

                        if response is None:
                            response = "I encountered a database error after 2 attempts. Try rephrasing your question with simpler criteria."

                        st.write(response)
                        logger.info("Response delivered.")

                st.session_state.chat_history.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"AI Error: {e}")
            logger.error(f"Chatbot error: {e}")
    else:
        st.error("GEMINI_API_KEY not found. Please check your .env file.")
        logger.error("API Key not found in .env file")