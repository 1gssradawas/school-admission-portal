import streamlit as st
import pandas as pd
from datetime import date
import gspread

# --- CONFIGURATION ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1wXyzRVLhbU3k5nH0VNN45YHR6oUK4RNfICC9ht_lZ8g/edit?usp=sharing" # Paste your URL here
SCHOOLS = {
    "Radawa": "R123",
    "Guda premsingh": "G456",
    "Guda raghunath singh": "G789",
    "Bera boriya": "B012"
}
CLASSES = [f"Class {i}" for i in range(1, 13)]

st.set_page_config(page_title="Admission Portal", page_icon="🏫")

# --- DATABASE CONNECTION ---
def save_to_sheets(data):
    try:
        # For simplicity in this tutorial, we use gspread
        # Note: In production, use service account JSON for better security
        gc = gspread.public(SHEET_URL) 
        sh = gc.open_by_url(SHEET_URL)
        worksheet = sh.worksheet("MasterData")
        
        # Check for duplicates: Date + School + Class
        existing_data = pd.DataFrame(worksheet.get_all_records())
        if not existing_data.empty:
            duplicate = existing_data[
                (existing_data['Date'] == str(data[0])) & 
                (existing_data['School'] == data[1]) & 
                (existing_data['Class'] == data[2])
            ]
            if not duplicate.empty:
                return False, "Data for this class and date already exists!"
        
        worksheet.append_row(data)
        return True, "Success!"
    except Exception as e:
        return False, str(e)

# --- UI ---
st.title("🏫 School Admission Entry")
st.info("Date Range: 01-04-2026 to 15-05-2026")

selected_school = st.selectbox("Select School", ["Select..."] + list(SCHOOLS.keys()))
password = st.text_input("Enter School Access Code", type="password")

if selected_school != "Select..." and password == SCHOOLS[selected_school]:
    with st.form("admission_form"):
        adm_date = st.date_input("Admission Date", 
                                  min_value=date(2026, 4, 1), 
                                  max_value=date(2026, 5, 15))
        adm_class = st.selectbox("Class", CLASSES)
        b = st.number_input("Boys", min_value=0, step=1)
        g = st.number_input("Girls", min_value=0, step=1)
        
        submit = st.form_submit_button("Submit Data")
        
        if submit:
            row = [str(adm_date), selected_school, adm_class, b, g, b+g, str(pd.Timestamp.now())]
            success, msg = save_to_sheets(row)
            if success:
                st.success("Data saved successfully!")
            else:
                st.error(msg)
elif password != "" and password != SCHOOLS.get(selected_school):
    st.error("Incorrect Access Code for this school.")
