import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import os

# Training data based on your real-world usage
TRAINING_DATA = [
    # --- RENT EXAMPLES (Needs to be strong!) ---
    ("monthly house rent", "Rent"),
    ("paying monthly rent", "Rent"),
    ("room rent payment", "Rent"),
    ("flat rent for april", "Rent"),
    ("studio rent money", "Rent"),
    ("house rent to landlord", "Rent"),
    ("paying my room rent", "Rent"),
    ("studio apartment rent", "Rent"),

    # --- FOOD EXAMPLES ---
    ("dinner at nandos", "Food"),
    ("groceries at lidl", "Food"),
    ("Ate chicken at restaurant", "Food"),
    ("pizza delivery", "Food"),
    ("Ate a ice cream", "Food"),
    ("Coffee at Starbucks", "Food"),
    ("Lunch with friends", "Food"),
    ("Breakfast at cafe", "Food"),

    # --- SHOPPING EXAMPLES ---
    ("new shoes from zara", "Shopping"),
    ("bought a pen", "Shopping"),
    ("clothes from h&m", "Shopping"),
    ("bought coconut and hair oil", "Shopping"),
    ("bought a mercedez car", "Shopping"),

    # --- OTHER ---
    ("bus fare to london", "Other"),
    ("train ticket", "Other"),
    ("netflix subscription", "Entertainment"),
    ("cinema tickets", "Entertainment")
]

MODEL_PATH = "category_model.pkl"


def train_model():
    X = [text for text, cat in TRAINING_DATA]
    y = [cat for text, cat in TRAINING_DATA]

    # Industry standard ML Pipeline
    model = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', MultinomialNB()),
    ])

    model.fit(X, y)
    joblib.dump(model, MODEL_PATH)
    return model


def predict_category(text):
    if not os.path.exists(MODEL_PATH):
        train_model()
    model = joblib.load(MODEL_PATH)
    return model.predict([text])[0]