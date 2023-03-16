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
import json
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

st.title("Data")
final = st.container()

directory = 'pdf'
f = []


@st.cache_data
def fuzzy_search(search_key, text, strictness, show):
    res = []

    rezovle = False
    _text = text.split()

    for line in _text:
        similarity = fuzz.ratio(search_key, line)
        if similarity != None and similarity >= strictness:
            res.append(similarity)

            if show == 1:
                st.markdown("---")

                st.write(
                    f"Am gasit '{line}' care seamana cu termenul cautat: '{search_key}' cu {similarity}% similaritate")
                st.markdown("---")

            rezovle = True

    if show == 1:
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
    temp2 = findKey(key2, temp1[1]+temp1[2])
    res = temp1[2].replace(temp2[2], '').replace(temp2[1], '')

    return res


def updateMetadata(metadata, keys, text, i, show):

    stop = len(keys)
    for j in range(stop):
        if len(keys[j][0]) > 1:
            if show == 1:
                st.markdown("---")
                st.write(f"{j}.\n\n")
                st.write(
                    f"findField[{keys[j][0]}][{keys[j][1]}]: {findField(keys[j][0],keys[j][1],text)}")
                st.markdown("---")
            metadata[j][i] = findField(keys[j][0], keys[j][1], text)
        else:
            if keys[j] == "Zile":
                regex = re.compile('([0-9]*) zile')
                metadata[j][i] = regex.findall(text)[0]
            if keys[j] == "LDL":
                metadata[j][i] = getLDH(text, show)
            if keys[j] == "Hip":
                if fuzzy_search('hipertensiv', text, 95, show):
                    metadata[j][i] = "DA"
                else:
                    if fuzzy_search('hipertensiune', text, 80, show):
                        metadata[j][i] = "DA"
                    else:
                        metadata[j][i] = "NU"
            if keys[j] == "dislipidemic":
                if fuzzy_search('dislipidemic', text, 95, show):
                    metadata[j][i] = "DA"
                else:
                    if fuzzy_search('dislipidemic', text, 80, show):
                        metadata[j][i] = "DA"
                    else:
                        metadata[j][i] = "NU"

            if keys[j] == "diabet":
                if fuzzy_search('diabet', text, 95, show):
                    metadata[j][i] = "DA"
                else:
                    if fuzzy_search('diabet', text, 80, show):
                        metadata[j][i] = "DA"
                    else:
                        metadata[j][i] = "NU"
            if keys[j] == "insulina":
                if metadata[j-1][i] == "DA":
                    if fuzzy_search('insulina', text, 80, show):
                        metadata[j][i] = "Tratat cu Insulina"
                    else:
                        if fuzzy_search('dietetic', text, 80, show):
                            metadata[j][i] = "Tratat cu dieta"
                        else:
                            metadata[j][i] = "Nu scrie"
                else:
                    metadata[j][i] = "---"
            if keys[j] == "infarct":
                if fuzzy_search('infarct', text, 95, show):
                    metadata[j][i] = "DA"
                else:
                    if fuzzy_search('infarct', text, 80, show):
                        metadata[j][i] = "DA"
                    else:
                        metadata[j][i] = "NU"
            if keys[j] == "perioada":
                temp = findField("Perioada internarii: ", "(", text)
                a = len(temp)
                metadata[j][i] = temp.replace(
                    temp[a-7:], "", 1).replace(temp[10:16], "", 1)


def getLDH(text, show):
    try:
        hdl = findField("Colesterol HDL :", "mg", text)

        hdl = float(hdl)
        seric = findField("total :", "mg", text)
        seric = float(seric)

        trigliceride = findField("Trigliceride :", "mg", text)
        trigliceride = float(trigliceride)

        ldl = seric - hdl - trigliceride/5
        if show == 1:
            st.markdown("---")
            st.write(f"HDL:{hdl}")
            st.write(f"Colesterol Seric:{seric}")
            st.write(f"trigliceride:{float(trigliceride)}")
            st.write(f"LDL COLESTEROL: {round(ldl,2)}")
            st.markdown("---")
        return round(ldl, 2)
    except:
        return "---"


@st.cache_data
def executeProject(show):
    varsta = []
    for filename in os.listdir(directory):
        f.append(os.path.join(directory, filename))

    # st.write(f)
    metadata = np.empty([len(f), len(f)], dtype="<U250")
    zile = []
    keys = [["NUMELE ", "PRENUMELE"], ["PRENUMELE ", "VIRSTA"], ["VIRSTA ", "CNP"], ["Data tiparire: ", "Sectia"],
            "perioada", "Zile", ["Urgenta ", "NUMELE "], "Hip", "LDL", "dislipidemic", "diabet", "insulina", "infarct"]

    progress = st.progress(0)
    # try:
    for i in range(len(f)):

        pdfFile = open(f[i], "rb")
        viewer = PdfReader(pdfFile)
        text = ""

        if show == 1:
            
            st.header(f"\n\n{i}. INVESTIGATII {f[i]}")
            st.subheader("Acum cautam chestiile pe care le vrem in excel")

        for j in range(len(viewer.pages)):
            text += viewer.pages[j].extract_text()
        investigare = findField("INVESTIGATII PARACLINICE IN CURSUL INTERNARII","Indicatie de revenire pentru internare", text)
        investigare = investigare.replace(";",",").split(',')
        st.write(investigare)
        updateMetadata(metadata, keys, text, i, show)

        # varsta, , ldl, (colesterol hdl, colesterol seric total + trigliceride pentru formula ldh)
        # hipertensiune?, daca au antecedente infarct?, dislipidemic?diabet da sau nu si daca insulino necesitant sau antidiabetice orale sau igieno- dientetic

        # pentru ca findField returneaza dubios daca are un \n sau ceva , .strip() iti scoate doar stringul si sterge spatiile
        for h in range(len(metadata[6])):
            metadata[6][i] = metadata[6][i].strip()
            if metadata[6][i] == "":
                metadata[6][i] = "NU"
        varsta.append(metadata[6][i][:1])
        data = {

            "Nume": metadata[0],
            "Prenume": metadata[1],
            "Varsta": metadata[2],
            "Data Tiparire": metadata[3],
            "Perioada Internarii": metadata[4],
            "Numar zile": metadata[5],
            "Urgenta": metadata[6],
            "Hipertensiune": metadata[7],
            "LDL COLESTEROL": metadata[8],
            "Dislipidemic": metadata[9],
            "Diabet": metadata[10],
            "Insulina": metadata[11],
            "Antecedente infarct": metadata[12]

        }
        progress.progress(i/len(f), "Progress")

        if show == 1:
            st.markdown("---")
            st.write(f"Le adaugam in tabel:\n\n")
            st.write(metadata)
            st.success("Efectuat cu succes\n\n\n\n")
            st.markdown("---")

    df = pd.DataFrame(data)

    if 'table' not in st.session_state:
        st.session_state['table'] = metadata
    if 'varsta' not in st.session_state:
        st.session_state['varsta'] = varsta
    df.to_feather("excel/output.feather")

    with final:

        st.success("Efectuat cu Success")
    progress.progress(100, "Progress")
    st.markdown("---")
    st.write("Aici e tabelul transformat in excel:\n")
    st.write(df)

    if show == 1:
        st.success("Vezi ca la toate tabelasele de mai sus poti sa ordonezi in functie de fiecare coloana.\n FYI pentru orice inseamna data(de tiparire sau internare etc) nu ordoneaza corect, daca o sa ai nevoie imi zici, dar altfel ai fisierul excel si faci direct acolo")

    # except:
    #     Head.exception("eroare")
def extractInv(investigare, index, data, stop):
    ##
    result = []
    key_val = []
    # st.write(investigare)
    for i in range(len(investigare)-1):
        if len(investigare[i]) >= 1:
            temp = findKey(':', investigare[i])

            # st.write(words)
            before = temp[0]
            after = temp[2]
            if '/' in before:
                # st.write(f"DA ma intra aici ")
                words = investigare[i].split(" ")
                for word in words:

                    if len(word) > 1 and word[0].isupper():
                        key = word + '  /TODO'

                        vere = findKey(key, investigare[i])
                        before_value = findKey(":", vere[2])
                        value = before_value[2]
                        # st.write(key)
                        result.append(key)
                        break

            else:
                key = before
                value = after

                # st.write(before)
                # regex = re.compile('[a-zA-Z]')
                # key = regex.findall(before)
                result.append(key)
                # st.write(key)

            key_val.append((key, value))
    for i in range(len(key_val)):
        cheie = key_val[i][0]
        valoare = key_val[i][1]
        # st.write(len(data[cheie]))

        try:
            
            if len(data[cheie])-index < 1 and len(data[cheie]) != index:
                    for i in range(index-len(data[cheie])-1):

                        data[cheie].append("---")

            else:
                    data[cheie].append(valoare)
            with open('try.txt', 'w') as f:
                 f.write(json.dumps(data))
           
        except KeyError:
            data[cheie] = []
            data[cheie].append(valoare)
           
            with open('except.txt', 'w') as f:
                 f.write(json.dumps(data))
            
    for name in data.keys():
        if len(data[name])-stop < 0 :
            for i in range(stop-len(data[name])):

                data[name].append('---')
        elif len(data[name])-stop == 0 :
            pass
        elif len(data[name])-stop > 0 :
            # st.write("killme")
            pass
     
    
    # for name in data.keys():
    #     st.write(len(data[name]))
    
    
    return data


            

def extractText(show):
    varsta = []
    data={}
    data_temp = {}
    for filename in os.listdir(directory):
        f.append(os.path.join(directory, filename))

    # st.write(f)
    metadata = np.empty([len(f), len(f)], dtype="<U250")
    zile = []
    keys = [["NUMELE ", "PRENUMELE"], ["PRENUMELE ", "VIRSTA"], ["VIRSTA ", "CNP"], ["Data tiparire: ", "Sectia"],
            "perioada", "Zile", ["Urgenta ", "NUMELE "], "Hip", "LDL", "dislipidemic", "diabet", "insulina", "infarct"]
    

    progress = st.progress(0)
    # try:
    for i in range(len(f)):

        pdfFile = open(f[i], "rb")
        viewer = PdfReader(pdfFile)
        text = ""

        if show == 1:
            
            st.header(f"\n\n{i}. INVESTIGATII {f[i]}")
            st.subheader("Acum cautam chestiile pe care le vrem in excel")

        for j in range(len(viewer.pages)):
            text += viewer.pages[j].extract_text()
        investigare = findField("INVESTIGATII PARACLINICE IN CURSUL INTERNARII","Indicatie de revenire pentru internare", text)
        investigare = investigare.replace(";",",").split(',')
        # st.write(investigare)

        
        temp_data = extractInv(investigare, i, data_temp, len(f))
        data_temp.update(temp_data)


    df = pd.DataFrame(data)
    st.dataframe(df)
#----------------------------------------------------------------------------------------------------------------------------------
side = st.sidebar.selectbox(
    "Optiuni: ",
    options=["Afiseaza Consola","Nu afiseaza Consola"]

)

extractText(0)


