import streamlit as st
import pandas as pd
import openpyxl
st.set_page_config(page_title="HomePage", layout="wide",  page_icon=":sun_with_face:")
st.title("Pagina Principala :smile:")
# st.header("Home Page")
# st.sidebar.success("Select page")
table = pd.read_excel("excel/output.xlsx")
st.subheader(f"Momentan doar asta avem in excel:\n")
st.write(table)