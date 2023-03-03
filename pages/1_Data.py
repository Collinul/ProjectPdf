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
    temp2 = findKey(key2, temp1[1]+temp1[2])
    res = temp1[2].replace(temp2[2], '').replace(temp2[1], '')
    
    return res

def updateMetadata(metadata,keys,text,i):
    for j in range(len(keys)):
        metadata[j][i] = findField(keys[j][0],keys[j][1],text)
        
    metadata[len(keys)][i] = getLDH(text)

def getLDH(text):
    hdl=findField("Colesterol HDL :","mg",text)
    hdl = float(hdl)
    st.write(f"Aici e hdl:{float(hdl)}")

    seric=findField("Colesterol seric total :","mg",text)
    st.write(f"Aici e seric:{seric}")
    seric = float(seric)
    st.write(f"Aici e seric:{seric}")

    trigliceride=findField("Trigliceride :","mg",text)
    trigliceride = float(trigliceride)
    # st.write(f"aici e trigliceride:{float(trigliceride)}")

    ldl = seric - hdl - trigliceride/5
    st.write(f"LDL COLESTEROL: {ldl}")
    
    return ldl

 
for filename in os.listdir(directory):
    f.append(os.path.join(directory, filename))

st.write(f)
metadata = np.empty([50,50], dtype="<U200")

keys=[["NUMELE ", "PRENUMELE"],["PRENUMELE ", "VIRSTA"],["VIRSTA ","CNP"],["Data tiparire: ", "Sectia"],["Perioada internarii: ","Medic:"],["Urgenta ", "NUMELE "]]
for i in range(len(f)):
    pdfFile = open(f[i], "rb")
    viewer = PdfReader(pdfFile)
    text = ""
    pag2 = viewer.pages[1].extract_text()
    # pag2 = pag2.replace(" ","")
    # pag3 = viewer.pages[2].extract_text()

    # getLDH(pag2)
   
    # st.write(findField("Clor seric","Colesterol",pag2))
    for j in range (len(viewer.pages)):
       text+=viewer.pages[j].extract_text()
            


    st.subheader(f"\n\n{i}. INVESTIGATII {f[i]}:\n\n\n{text}\n\n\n\n Acum cautam chestiile pe care le vrem in excel")

    # Keep in mind the j coordonates would eventually corespond to different patients
    #TODO function care automatizeaza
    updateMetadata(metadata,keys,text,i)
    st.write(f"Metadata 6 !!! {metadata[6]}")
    st.write(f"Le adaugam in tabel:\n\n")
    st.write(metadata)
    #varsta, , ldl, (colesterol hdl, colesterol seric total + trigliceride pentru formula ldh)
    #hipertensiune?, daca au antecedente infarct?, dislipidemic?diabet da sau nu si daca insulino necesitant sau antidiabetice orale sau igieno- dientetic
    data = {

        "Nume": metadata[0],
        "Prenume": metadata[1],
        "Varsta": metadata[2],
        "Data Tiparire": metadata[3],
        "Perioada Internarii": metadata[4],
        "Urgenta": metadata[5],
        "LDL COLESTEROL": metadata[6]
    }

    st.success("Efectuat cu succes\n\n\n\n")

st.write("Aici e tabelul transformat in excel:\n")
df = pd.DataFrame(data)

with pd.ExcelWriter("excel/output.xlsx") as writer:
    df.to_excel(writer, sheet_name="Output", index=False)
st.write(df)
st.success("Vezi ca la toate tabelasele de mai sus poti sa ordonezi in functie de fiecare coloana.\n FYI pentru orice inseamna data(de tiparire sau internare etc) nu ordoneaza corect, daca o sa ai nevoie imi zici, dar altfel ai fisierul excel si faci direct acolo")