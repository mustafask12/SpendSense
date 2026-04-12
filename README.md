# 💰 SpendSense — AI-Powered Personal Finance Tracker

> Track expenses with natural language. Powered by a hybrid AI engine — a local NLP model for instant offline predictions and Google Gemini LLM for intelligent cloud-based insights.

---

## 🧠 What Makes This Different

Most expense trackers just store numbers. **SpendSense** understands your spending in plain English.

- Type *"Got a vanilla cone at the park"* — the AI auto-categorizes it as **Food**
- Ask *"Compare my August vs September spending"* — the chatbot queries your database and answers in seconds
- Two AI engines in one app: a **fast offline ML model** and **Google Gemini LLM**

---

## ✨ Features

| Feature | Description |
|---|---|
| 📝 **Add / Update Expenses** | 5-row daily grid — load, edit and save expenses for any date |
| ✨ **Local AI Prediction** | TF-IDF + Naive Bayes model predicts category from notes instantly, no internet needed |
| 🤖 **Gemini AI Prediction** | Google Gemini LLM handles tricky or ambiguous expense notes via the cloud |
| 📊 **Analytics by Category** | Bar chart + table showing spending breakdown with percentages for any date range |
| 📅 **Analytics by Month** | Full year view of monthly spending with interactive bar chart |
| 💬 **AI Financial Advisor** | LangChain-powered chatbot — ask any question about your spending in plain English |
| 🗂️ **Rotating File Logger** | Production-grade logging with 5MB rotating files across the entire app |
| 🧪 **Pytest Test Suite** | Automated tests for database layer covering valid dates, invalid dates, and empty ranges |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           Streamlit Frontend (app.py)        │
│  Tab 1: Add/Update  │  Tab 2: Category       │
│  Tab 3: By Month    │  Tab 4: AI Advisor     │
└────────────────┬────────────────────────────┘
                 │  HTTP (requests)
                 ▼
┌─────────────────────────────────────────────┐
│         FastAPI Backend (server.py)          │
│                                             │
│  GET  /expenses/{date}                      │
│  POST /expenses/{date}                      │
│  GET  /predict-category/{notes}             │
│       ├─ use_gemini=false → ML_logic.py     │
│       └─ use_gemini=true  → Gemini LLM      │
│  POST /analytics/                           │
│  GET  /months/?year=                        │
│  GET  /years/                               │
└────────────────┬────────────────────────────┘
                 │
        ┌────────┴──────────┐
        ▼                   ▼
┌──────────────┐   ┌─────────────────────┐
│  MySQL DB    │   │   AI Engine Layer   │
│              │   │                     │
│  expenses    │   │ ✨ Local:           │
│  table       │   │  TF-IDF + Naive     │
│              │   │  Bayes Pipeline     │
│              │   │  (scikit-learn)     │
│              │   │                     │
└──────────────┘   │ 🤖 Cloud:           │
                   │  Gemini 2.5 Flash   │
                   │  Lite via LangChain │
                   └─────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit |
| **Backend** | FastAPI |
| **Database** | MySQL |
| **Local AI** | scikit-learn (TF-IDF Vectorizer + Multinomial Naive Bayes) |
| **Cloud AI** | Google Gemini 2.5 Flash Lite via `langchain-google-genai` |
| **SQL Chatbot** | LangChain `SQLDatabaseChain` |
| **Logging** | Python `RotatingFileHandler` (5MB × 3 files) |
| **Testing** | Pytest |
| **Environment** | python-dotenv |

---

## 📁 Project Structure

```
SpendSense/
│
├── Backend/
│   ├── server.py                # FastAPI app — all REST endpoints
│   ├── db_helper.py             # All MySQL operations (fetch, insert, delete)
│   ├── ML_logic.py              # TF-IDF + Naive Bayes training & prediction
│   ├── logging_setup.py         # Rotating file logger shared across all modules
│   └── category_model.pkl       # Trained ML model (auto-generated on first run)
│
├── Frontend/
│   ├── .streamlit/
│   │   └── config.toml          # Custom dark theme configuration
│   ├── app.py                   # Streamlit entry point — tab layout
│   ├── add_update_ui.py         # Tab 1: Expense entry grid with dual AI buttons
│   ├── analytics_by_category.py # Tab 2: Category breakdown chart + table
│   ├── analytics_by_months.py   # Tab 3: Monthly spending chart + table
│   └── chatbot.py               # Tab 4: Gemini AI financial advisor chatbot
│
├── tests/
│   ├── conftest.py              # Pytest path configuration
│   └── test_db_helper.py        # DB layer unit tests
│
├── database/
│   └── expense_manager.sql      # Database schema + sample data
│
├── .env                         # API keys (never commit this)
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/mustafask12/SpendSense.git
cd SpendSense
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up MySQL

**Option A — Use the included SQL file (recommended)**

A ready-made SQL file is included in the `database/` folder. Run this command to create and populate the database instantly:

```bash
mysql -u root -p < database/expense_manager.sql
```

**Option B — Create manually**

If you prefer to start with an empty database, make sure MySQL is running locally and run:

```sql
CREATE DATABASE expense_manager;

USE expense_manager;

CREATE TABLE expenses (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    expense_date DATE NOT NULL,
    amount       DECIMAL(10, 2) NOT NULL,
    category     VARCHAR(50) NOT NULL,
    notes        VARCHAR(255)
);
```

### 5. Configure your environment variables

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_google_gemini_api_key_here
```

Get your free API key from [Google AI Studio](https://aistudio.google.com/).

### 6. Start the FastAPI backend

Open **Terminal 1** and run:

```bash
cd Backend
uvicorn server:app --reload
```

Wait until you see:
```
INFO: Uvicorn running on http://127.0.0.1:8000
```

### 7. Start the Streamlit frontend

Open **Terminal 2** and run:

```bash
cd Frontend
streamlit run app.py
```

> ⚠️ **Both terminals must be running at the same time.** Terminal 1 runs the backend on port 8000, Terminal 2 runs the frontend on port 8501. If either stops, the app will break.

---

## 🎨 Theme

SpendSense uses a custom dark theme configured in `Frontend/.streamlit/config.toml`. It applies automatically when you run the app — no extra setup needed.

```toml
[theme]
primaryColor = "#00C896"
backgroundColor = "#0A0A0A"
secondaryBackgroundColor = "#141414"
textColor = "#F0F0F0"
font = "sans serif"
```

---

## 🤖 How the Dual AI Engine Works

When you type a note like *"Got a vanilla cone at the park"* and click an AI button:

```
User clicks ✨ Local
    │
    ▼
FastAPI → ML_logic.py
    ├── Loads category_model.pkl (TF-IDF + Naive Bayes pipeline)
    ├── Vectorizes the input text
    └── Returns predicted category → "Food"

User clicks 🤖 Gemini
    │
    ▼
FastAPI → Gemini 2.5 Flash Lite via LangChain
    ├── Receives structured prompt with 5 valid categories
    ├── Uses LLM reasoning to classify the note
    └── Returns predicted category → "Food"
```

The category dropdown on that row **automatically updates** and a toast notification shows `"AI Suggests: Food"`. You can accept it or override manually before saving.

---

## 💬 AI Financial Advisor — Example Queries

The chatbot translates plain English into SQL and answers from your real data:

```
"What was my highest expense in August 2024?"
"Compare my spending in August vs September."
"If 1 GBP = 105 INR, what is my total August spend in pounds?"
"Are there any duplicate entries with the same amount, category, and date?"
"If I keep spending like August, what will my yearly total look like?"
"Which category will I struggle with most on a £1,500/month UK budget?"
```

---

## 🧪 Running Tests

```bash
cd tests
pytest test_db_helper.py -v
```

Tests cover fetching expenses for a valid date, fetching for a date with no data, and fetching a summary for an empty date range.

---

## 📊 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/expenses/{date}` | Fetch all expenses for a given date |
| `POST` | `/expenses/{date}` | Replace all expenses for a given date |
| `GET` | `/predict-category/{notes}` | Predict category (add `?use_gemini=true` for Gemini) |
| `POST` | `/analytics/` | Get spending breakdown by category for a date range |
| `GET` | `/months/?year={year}` | Get monthly totals for a given year |
| `GET` | `/years/` | Get all years that have expense data |

Full interactive docs: `http://localhost:8000/docs`

---

## 📝 Logging

All modules write to `server.log` using a shared rotating logger (5MB per file, 3 backups):

```
2026-04-03 12:08:00 - server         - INFO - AI prediction requested for: pizza delivery (Mode: Gemini)
2026-04-03 12:08:32 - server         - INFO - Gemini response successful
2026-04-03 12:09:14 - gemini_chatbot - INFO - User Query: Compare August vs September spending
2026-04-03 12:10:16 - gemini_chatbot - INFO - Gemini response successful
```

---

## 🔮 Future Improvements

- [ ] Receipt image upload with OCR auto-fill
- [ ] Budget limits with alerts per category
- [ ] Export to CSV / PDF
- [ ] Multi-user authentication
- [ ] Deploy backend on Railway, frontend on Streamlit Cloud
