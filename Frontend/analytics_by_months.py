import streamlit as st
import pandas as pd
import requests

API_URL = "http://localhost:8000"
def analytics_months_tab():
    response = requests.get(f"{API_URL}/years/")
    years_data = response.json()

    years = [row['year'] for row in years_data]
    year = st.selectbox("Select Year", years)

    response = requests.get(f"{API_URL}/months/", params={"year": year})
    data = response.json()

    df = pd.DataFrame(data)

    if not df.empty:
        df = df.rename(columns={
            "month_no": "Month Number",
            "month_name": "Month Name"
        })

        df_sorted = df.sort_values(by="Month Number", ascending=False)
        df_sorted.set_index("Month Number", inplace=True)

        st.title("Expense Breakdown by Months")
        st.bar_chart(data=df_sorted.set_index("Month Name")["Total"].astype(float), width='stretch',height='content')
        df_sorted["Total"] = df_sorted["Total"].map("{:.2f}".format)
        df_sorted.index.name = None #removes "month_no" title


        st.table(df_sorted.sort_index())


