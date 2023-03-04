import streamlit as st
import pandas as pd
import openpyxl
st.set_page_config(page_title="HomePage", layout="wide",
                   page_icon=":sun_with_face:")
st.title("Pagina Principala :smile:")
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>

"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# st.header("Home Page")
# st.sidebar.success("Select page")
table = pd.read_excel("excel/output.xlsx")
st.subheader(f"Momentan doar asta avem in excel:\n")
st.write(table)
if 'table' in st.session_state:
    table = st.session_state["table"]
    st.write(table)

