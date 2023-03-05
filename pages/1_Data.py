import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
import os
import numpy as np
import openpyxl
import re
from difflib import SequenceMatcher
from thefuzz import fuzz
from thefuzz import process
import time
import collections.abc
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
final = st.container()
st.markdown(hide_st_style, unsafe_allow_html=True)

st.header("Aici ma joc eu cu datele , nu baga in seama  ")
st.title("Data")
# File logic
# TODO: make it so you can put any number of pdfs as input serve the data to dataframe logic


directory = 'pdf'
f = []



@st.cache_data
def fuzzy_search(search_key, text, strictness):
    res=[]
    words=[]
    rezovle = False
    _text = text.split()
   
    for line in _text:   
        similarity = fuzz.ratio(search_key, line)
        if  similarity!=None and similarity >=strictness:
            res.append(similarity)
            words.append(text[i:j])

            st.write(f"Found '{line}' to be matching your search_key: {search_key} with {similarity}% similarity") 

            rezovle = True
       
       
    st.write(rezovle)
    return rezovle


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
    # st.write("temp1: ",temp1)
    temp2 = findKey(key2, temp1[1]+temp1[2])
    res = temp1[2].replace(temp2[2], '').replace(temp2[1], '')
    
    return res

def updateMetadata(metadata,keys,text,i):
    
    
    stop  = len(keys)
    for j in range(stop):
        if len(keys[j][0])>1:
            st.write(f"++++++++++++++++++++++++++{j}+++++++++++++++++++++++++++++++")
            st.write(f"findField[{keys[j][0]}][{keys[j][1]}]: {findField(keys[j][0],keys[j][1],text)}")
            metadata[j][i] = findField(keys[j][0],keys[j][1],text)
        else:
            if keys[j]=="Zile":
                regex = re.compile('([0-9]*) zile')
                st.write("nr Zile: ",regex.findall(text)[0])
                metadata[j][i] = regex.findall(text)[0]
            if keys[j] == "LDL":
                st.write("LDH : ",getLDH(text))
                metadata[j][i] = getLDH(text)
            if keys[j] =="Hip":
                if fuzzy_search('hipertensiv', text, 95):
                    metadata[j][i]= "DA"
                else:
                    if fuzzy_search('hipertensiune', text, 80):
                        metadata[j][i]= "DA" 
                    else:
                        metadata[j][i] ="NU"
            if keys[j]=="dislipidemic":
                if fuzzy_search('dislipidemic', text, 95):
                    metadata[j][i]= "DA"
                else:
                    if fuzzy_search('dislipidemic', text, 80):
                        metadata[j][i]= "DA" 
                    else:
                        metadata[j][i] ="NU"
            if keys[j]=="diabet":
                if fuzzy_search('diabet', text, 95):
                    metadata[j][i]= "DA"
                else:
                    if fuzzy_search('diabet', text, 80):
                        metadata[j][i]= "DA" 
                    else:
                        metadata[j][i] ="NU"
            if keys[j]=="infarct":
                if fuzzy_search('infarct', text, 95):
                    metadata[j][i]= "DA"
                else:
                    if fuzzy_search('infarct', text, 80):
                        metadata[j][i]= "DA" 
                    else:
                        metadata[j][i] ="NU"
            if keys[j] == "perioada":
                temp = findField("Perioada internarii: ","(",text)
                a = len(temp)
                metadata[j][i] = temp.replace(temp[a-7:],"",1).replace(temp[10:16],"",1)
           
        
   

def getLDH(text):
    hdl=findField("Colesterol HDL :","mg",text)
    
    st.write(f"Aici e hdl:{hdl}")
    hdl = float(hdl)
    seric=findField("total :","mg",text)
    seric = float(seric)
    st.write(f"Aici e seric:{seric}")

    trigliceride=findField("Trigliceride :","mg",text)
    trigliceride = float(trigliceride)
    st.write(f"aici e trigliceride:{float(trigliceride)}")

    ldl = seric - hdl - trigliceride/5
    st.write(f"LDL COLESTEROL: {ldl}")
    
    return ldl

 
for filename in os.listdir(directory):
    f.append(os.path.join(directory, filename))

st.write(f)
metadata = np.empty([50,50], dtype="<U250")
zile = []
keys=[["NUMELE ", "PRENUMELE"],["PRENUMELE ", "VIRSTA"],["VIRSTA ","CNP"],["Data tiparire: ", "Sectia"],"perioada","Zile",["Urgenta ", "NUMELE "],"Hip","LDL","dislipidemic","diabet","infarct"]
for i in range(len(f)):
    pdfFile = open(f[i], "rb")
    viewer = PdfReader(pdfFile)
    text = ""
    # pag2 = viewer.pages[2].extract_text()
    # pag2 = pag2.replace(" ","")
    # pag3 = viewer.pages[2].extract_text()

    # getLDH(pag2)
   
    
    for j in range (len(viewer.pages)):
       text+=viewer.pages[j].extract_text()
            
    # st.write("da: ",findField("Colesterol seric total :","mg",pag2))
    st.subheader(f"\n\n{i}. INVESTIGATII {f[i]}")
    # st.text(f"{text}")
    st.write("Acum cautam chestiile pe care le vrem in excel")

    # Keep in mind the j coordonates would eventually corespond to different patients
    #TODO function care automatizeaza
    updateMetadata(metadata,keys,text,i)
    
    st.write(f"Le adaugam in tabel:\n\n")
    st.write(metadata)
    #varsta, , ldl, (colesterol hdl, colesterol seric total + trigliceride pentru formula ldh)
    #hipertensiune?, daca au antecedente infarct?, dislipidemic?diabet da sau nu si daca insulino necesitant sau antidiabetice orale sau igieno- dientetic
    
    # pentru ca findField returneaza dubios daca are un \n sau ceva , .strip() iti scoate doar stringul si sterge spatiile
    for h in range(len(metadata[6])):
        metadata[6][i] = metadata[6][i].strip()
       
        
    data = {

        "Nume": metadata[0],
        "Prenume": metadata[1],
        "Varsta": metadata[2],
        "Data Tiparire": metadata[3],
        "Perioada_Internarii": metadata[4],
        "Numar zile": metadata[5],
        "Urgenta": metadata[6],
        "Hipertensiune": metadata[7],
        "LDL COLESTEROL": metadata[8],
        "Dislipidemic": metadata[9],
        "Diabet": metadata[10],
        "Antecedente infarct": metadata[11]
        
    }

    st.success("Efectuat cu succes\n\n\n\n")

st.write("Aici e tabelul transformat in excel:\n")
df = pd.DataFrame(data)

if 'table' not in st.session_state:
    st.session_state['table'] = metadata

with pd.ExcelWriter("excel/output.xlsx") as writer:
    df.to_excel(writer, sheet_name="Output", index=False)
st.write(df)
with final:
    st.success("Efectuat cu Success")
st.success("Vezi ca la toate tabelasele de mai sus poti sa ordonezi in functie de fiecare coloana.\n FYI pentru orice inseamna data(de tiparire sau internare etc) nu ordoneaza corect, daca o sa ai nevoie imi zici, dar altfel ai fisierul excel si faci direct acolo")