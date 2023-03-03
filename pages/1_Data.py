import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
import os
import numpy as np
import openpyxl
# site config
st.set_page_config(page_title="Extract", layout="wide",
                   page_icon=":sun_with_face:")
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>

"""
st.markdown(hide_st_style, unsafe_allow_html=True)

st.header("Aici ma joc eu cu datele , nu baga in seama  ")
st.title("Data")
# File logic
# TODO: make it so you can put any number of pdfs as input serve the data to dataframe logic


directory = 'pdf'
f = []


def findKey(keyword, text):
    res = []
    mystring = text

    before_keyword, keyword, after_keyword = mystring.partition(keyword)
    # st.write(f"before_keyword: {before_keyword}\n, keyword: {keyword}\n, after_keyword: {after_keyword}\n")
    res.append(before_keyword)
    res.append(keyword)
    res.append(after_keyword)
    return res


def findField(key1, key2, text):
    temp1 = findKey(key1, text)
    temp2 = findKey(key2, text)
    res = temp1[2].replace(temp2[2], '').replace(temp2[1], '')
    st.write(f"{key1}: {res}")
    return res

 
for filename in os.listdir(directory):
    f.append(os.path.join(directory, filename))

st.write(f)
metadata = np.empty([len(f),len(f)], dtype="<U200")
for i in range(len(f)):
    pdfFile = open(f[i], "rb")
    viewer = PdfReader(pdfFile)
    text = viewer.pages[0].extract_text()

   

    st.subheader(f"\n\n{i}. Doar prima pagina din {f[i]}:\n\n\n{text}\n\n\n\n Acum cautam chestiile pe care le vrem in excel")

    # Keep in mind the j coordonates would eventually corespond to different patients
    metadata[0][i] = findField("NUMELE ", "PRENUMELE", text)  # nume
    metadata[1][i] = findField("PRENUMELE ", "VIRSTA", text)  # prenume

    metadata[2][i] = findField(
        "Data tiparire: ", "Sectia", text)  # dataTiparire

    metadata[3][i] = findField("Perioada internarii: ",
                               "Medic:", text)  # perioada

    metadata[4][i] = findField("Urgenta ", "NUMELE ", text)
    st.write(f"Le adaugam in tabel:\n\n")
    st.write(metadata)
    data = {

        "Nume": metadata[0],
        "Prenume": metadata[1],
        "Data Tiparire": metadata[2],
        "Perioada Internarii": metadata[3],
        "Urgenta": metadata[4]
    }

    st.success("Efectuat cu succes\n\n\n\n")

st.write("Aici e tabelul transformat in excel:\n")
df = pd.DataFrame(data)

with pd.ExcelWriter("excel/output.xlsx") as writer:
    df.to_excel(writer, sheet_name="Output", index=False)
st.write(df)
st.success("Vezi ca la toate tabelasele de mai sus poti sa ordonezi in functie de fiecare coloana.\n FYI pentru orice inseamna data(de tiparire sau internare etc) nu ordoneaza corect, daca o sa ai nevoie imi zici, dar altfel ai fisierul excel si faci direct acolo")