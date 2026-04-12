from fastapi import FastAPI, HTTPException
from datetime import date
import db_helper
from typing import List
from pydantic import BaseModel
from logging_setup import setup_logger
from ML_logic import predict_category # Importing ML function
import os
# from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI

# --- THIS LINE IS TO LOAD .env FILE ---
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Setup logger
logger = setup_logger("server")

# --- INITIALIZE GEMINI API KEY ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.error("API Key not found!")
    raise ValueError("GEMINI_API_KEY is missing in .env file")

# This Line for the Chatbot to work
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", google_api_key=api_key)

app = FastAPI()
class Expense(BaseModel):
    amount: float
    category: str
    notes: str

class DateRange(BaseModel):
    start_date: date
    end_date: date


@app.get("/expenses/{expense_date}", response_model=List[Expense])
def get_expenses(expense_date: date):
    expenses = db_helper.fetch_expenses_for_date(expense_date)
    if expenses is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expenses from the database")

    return expenses

@app.post("/expenses/{expense_date}")
def add_or_update_expense(expense_date: date, expenses:List[Expense]):
    db_helper.delete_expenses_for_date(expense_date)
    for expense in expenses:
        db_helper.insert_expense(expense_date, expense.amount, expense.category, expense.notes)
    return {"message": "Expenses updated successfully"}


@app.get("/predict-category/{notes}")
def get_ai_category(notes: str, use_gemini: bool = False):
    """
            AI CAPSTONE FEATURE: Hybrid NLP approach.
            - Local: Fast & Free (ml_logic.py)
            - Gemini: Smart Cloud AI (for tricky notes)
    """

    logger.info(f"AI prediction requested for: {notes} (Mode: {'Gemini' if use_gemini else 'Local'})")

    try:
        if use_gemini:

            prompt = f"""
            Categorize this expense note into exactly ONE category:

            Rent
            Food
            Shopping
            Entertainment
            Other

            Note: {notes}

            Return only the category name.
            """

            response = llm.invoke(prompt)

            category = response.content.strip().replace(".", "")

        else:
            category = predict_category(notes)

        return {"suggested_category": category}

    except Exception as e:
        logger.error(f"AI Model Error for '{notes}': {e}")
        raise HTTPException(status_code=500, detail=f"AI Model failed: {str(e)}")


@app.post("/analytics/")
def get_analytics(date_range: DateRange):
    data = db_helper.fetch_expense_summary(date_range.start_date, date_range.end_date)
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expense summary from the database")

    Total=sum([row['Total'] for row in data])

    breakdown ={}
    for row in data:
        percentage = (row['Total']/Total)*100 if Total !=0 else 0
        breakdown[row['category']] = {
            'total': row['Total'],
            'percentage': percentage
        }
    return breakdown


@app.get("/months/")
def get_expenses_by_months(year: int):
    data = db_helper.fetch_expense_summary_by_months(year)
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expense summary from the database")

    return data


@app.get("/years/")
def get_availabe_years():
    data = db_helper.fetch_available_years()
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expense summary from the database")

    return data