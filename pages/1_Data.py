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

st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("Data")
final = st.container()

directory = 'pdf'
f = []

# TODO: Mare atentie, analizele au elemente duplicate si trebuie setat sa ia varianta cea mai actualizata a respectivului. sugerez 1 dictionar pentru un rand si functia migratedictionary ca sa isi faca append unde e cazul


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
            if keys[j] == "CNP":
                ##
                metadata[j][i] = findField("CNP ", "CASA", text)
                st.write(f"CNP: {metadata[j][i]}")

                cnp = metadata[j][i]
            if keys[j] == "Nastere":
                ##
                an = cnp[1]+cnp[2]
                luna = cnp[3] + cnp[4]
                zi = cnp[5] + cnp[6]
                metadata[j][i] = zi + '/' + luna + '/' + an
            if keys[j] == "Sex":
                ##
                if int(cnp[0]) % 2 == 0:
                    metadata[j][i] = "F"
                else:
                    metadata[j][i] = "M"

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


def unique(list1):

    # initialize a null list
    unique_list = []

    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)

    return unique_list

    key_val = []
    keys = []

    # loop to find terms and extract key and value
    for i in range(len(investigare) - 1):
        if len(investigare[i]) >= 1:
            temp = findKey(':', investigare[i])

            before = temp[0]
            after = temp[2]
            if '/' in before:
                words = investigare[i].split(" ")
                for word in words:

                    if len(word) > 1 and word[0].isupper():
                        key = word + '  /TODO'

                        vere = findKey(key, investigare[i])
                        before_value = findKey(":", vere[2])
                        value = before_value[2]
                        break

            else:
                key = before.replace(' ', '')
                value = after

            key_val.append((key, value))
            keys.append(key)

    for i in range(len(keys)):
        found_key = False
        for j in range(len(metadataInv)):
            if fuzzy_search(keys[i], metadataInv[j][0], 80, 0):
                metadataInv[j][0] = keys[i]
                found_key = True
                break

        if not found_key:
            new_row = np.array([keys[i]] + ["" for _ in range(index)])
            metadataInv = np.vstack((metadataInv, new_row))

    for i in range(len(key_val)):
        found_key = False
        for j in range(len(metadataInv)):
            if fuzzy_search(key_val[i][0], metadataInv[j][0], 80, 0):
                metadataInv[j][index + 1] = key_val[i][1]
                found_key = True
                break

        if not found_key:
            new_row = np.array([key_val[i][0]] +
                               ["" for _ in range(index)] + [key_val[i][1]])
            metadataInv = np.vstack((metadataInv, new_row))

    st.write(metadataInv)
    if index == stop - 1:

        st.write(metadataInv)


def extractInv(investigare, index, stop, data_fin, metadataInv):
    key_val = []
    keys = []
    # st.write(metadataInv)
    # loop for finding terms and extracting keys and values
    for i in range(len(investigare) - 1):
        if len(investigare[i]) >= 1:
            temp = findKey(':', investigare[i])
            before = temp[0]
            after = temp[2]

            if '/' in before:
                words = investigare[i].split(" ")
                for word in words:
                    if len(word) > 1 and word[0].isupper():
                        key = word + '  /TODO'
                        vere = findKey(key, investigare[i])
                        before_value = findKey(":", vere[2])
                        value = before_value[2]
                        break
            else:
                key = before.replace(' ', '')
                value = after

            key_val.append((key, value))
            keys.append(key)
    # st.write(f"key len:  {len(keys)}")
    for i in range(len(keys)):

        aTemp = list(metadataInv[:, 0])
        try:
            place = aTemp.index(keys[i])
        except ValueError:
            closest_key = None
            highest_similarity = 0

            for existing_key in aTemp:
                similarity = fuzz.ratio(keys[i], existing_key)
                if similarity >= 80 and similarity > highest_similarity:
                    highest_similarity = similarity
                    closest_key = existing_key

            row_added = False
            if highest_similarity > 60:
                keys[i] = closest_key
            else:
                for j in range(len(aTemp)):
                    if metadataInv[j][0] == "":
                        metadataInv[j][0] = keys[i]
                        # st.write(f"keys[i]= {keys[i]}")
                        row_added = True
                        break

                if not row_added:
                    new_row = np.array(
                        [keys[i]] + ["" for _ in range(metadataInv.shape[1] - 1)], dtype="<U250").reshape(1, -1)
                    metadataInv = np.vstack((metadataInv, new_row))

    for i in range(len(key_val)):
        aTemp = list(metadataInv[:, 0])
        try:
            place = aTemp.index(key_val[i][0])
            metadataInv[place][index + 1] = key_val[i][1]
        except ValueError:
            # for j in range(len(aTemp)):
            #     if metadataInv[j][0] == "":
            #         metadataInv[j][0] = key_val[i][0]
            #         metadataInv[j][index + 1] = key_val[i][1]
            #         st.write(key_val[i][0])
            #         st.write(key_val[i][1])
            #     j = len(aTemp)
            pass

    # st.write(metadataInv)
    # if index == stop - 1:
    #     st.write(metadataInv)
    return metadataInv


def extractInv_2(investigare, index, stop, data_fin):

    key_val = []
    # st.write(investigare)
    caca = {}

  # loop pentru gasit termeni si iti scoate key  si  valoare
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
                        break

            else:
                key = before
                value = after

            key_val.append((key, value))

    st.write(f"key_val len:  {len(key_val)}")

    # loop care baga key si valoarea in data
    for i in range(len(key_val)):
        cheie = key_val[i][0]
        valoare = key_val[i][1]
        # st.write(len(data[cheie]))

        caca[cheie] = valoare

        if cheie not in data_fin.keys():
            data_fin[cheie] = []

        if len(data_fin[cheie]) < index:
            for i in range(len(data_fin[cheie]), index):
                if len(data_fin[cheie]) == index:
                    break
                data_fin[cheie].append("gigi")
            data_fin[cheie].append(caca[cheie])
        elif len(data_fin[cheie]) > index:
            for i in range(index, len(data_fin[cheie])):
                data_fin[cheie].pop()

        else:
            pass
    st.write(len(data_fin.keys()))
    # gigel = st.container()
    # st.write(caca)

    # for name in caca.keys():
    #     data_fin[name].append(caca[name])

    # st.write(data_fin)
    # corecteaza lungimea arrayurilor
    for name in data_fin.keys():
        if len(data_fin[name]) < stop:

            while len(data_fin[name]) != stop:

                data_fin[name].append(i)

        elif len(data_fin[name]) == stop:
            pass
        elif len(data_fin[name]) > stop:
            while len(data_fin[name]) != stop:
                data_fin[name].pop()

    # for name in caca.keys():
    #     st.write(len(caca[name]))

    # if index == stop-1:
    #     # dc = pd.DataFrame(data_fin)
    #     gigel.write(data_fin)
    return data_fin


def mergeDictionary(dict_1, dict_2):

    for key, value in dict_1.items():
        if key in dict_1 and key in dict_2:
            dict_1[key].append(dict_2[key])
    return dict_1

# @st.cache_data


def executeProject(show):
    varsta = []
    data_temp = {}
    f = []
    data_fin = {}
    for filename in os.listdir(directory):
        f.append(os.path.join(directory, filename))

    # st.write(f)
    metadata = np.empty([len(f), len(f)], dtype="<U250")
    metadataInv = np.zeros([len(f)+60, len(f)+1], dtype="<U250")
    extractData = np.empty([len(f), len(f)], dtype="<U250")
    zile = []
    keys = [["NUMELE ", "PRENUMELE"], ["PRENUMELE ", "VIRSTA"], ["VIRSTA ", "CNP"], "CNP", "Nastere", ["Data tiparire: ", "Sectia"],
            "Sex", "perioada", "Zile", ["Urgenta ", "NUMELE "], "Hip", "LDL", "dislipidemic", "diabet", "insulina", "infarct"]

    keys_inv = []
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
        investigare = findField("INVESTIGATII PARACLINICE IN CURSUL INTERNARII",
                                "Indicatie de revenire pentru internare", text)
        investigare = investigare.replace(";", ",").split(',')

        # st.write(investigare)
        updateMetadata(metadata, keys, text, i, show)

        # varsta, , ldl, (colesterol hdl, colesterol seric total + trigliceride pentru formula ldh)
        # hipertensiune?, daca au antecedente infarct?, dislipidemic?diabet da sau nu si daca insulino necesitant sau antidiabetice orale sau igieno- dientetic

        # pentru ca findField returneaza dubios daca are un \n sau ceva , .strip() iti scoate doar stringul si sterge spatiile
        for h in range(len(metadata[9])):
            metadata[9][i] = metadata[9][i].strip()
            if metadata[9][i] == "":
                metadata[9][i] = "NU"
        varsta.append(metadata[2][i][:1])
        data = {

            "Nume": metadata[0],
            "Prenume": metadata[1],
            "Varsta": metadata[2],
            "CNP": metadata[3],
            "Data Nastere": metadata[4],
            "Data Tiparire": metadata[5],
            "Sex": metadata[6],
            "Perioada Internarii": metadata[7],
            "Durata Internarii": metadata[8],
            "Urgenta": metadata[9],
            "Hipertensiune": metadata[10],
            "LDL COLESTEROL": metadata[11],
            "Dislipidemic": metadata[12],
            "Diabet": metadata[13],
            "Insulina": metadata[14],
            "Antecedente infarct": metadata[15]

        }
        progress.progress(i/len(f), f"Progress {i}/{len(f)}")

        temp_data = extractInv(
            investigare, i, len(f), data_temp, metadataInv)

        if show == 1:
            st.markdown("---")
            st.write(f"Le adaugam in tabel:\n\n")
            st.write(metadata)
            st.success("Efectuat cu succes\n\n\n\n")
            st.markdown("---")
    # st.write(data_temp)
    dc = pd.DataFrame(temp_data)

    dc_t = dc.transpose(copy=True)

    dc_t.columns = dc_t.iloc[0]

    dc_t = dc_t[1:]
    dc_t = dc_t.reset_index(drop=True)
    st.dataframe(dc_t)

    # for name in data.keys():

    #     st.write(len(data[name]))

    df = pd.DataFrame(data)
    st.write(df)
    df3 = pd.merge(df, dc_t, sort=False, left_index=True, right_index=True)
    # df = df.merge(dc_t, how='outer', sort=False, left_index=True, right_index=True)
    # df.join(dc_t)
    st.write(df3)

    if 'table' not in st.session_state:
        st.session_state['table'] = metadata
    if 'varsta' not in st.session_state:
        st.session_state['varsta'] = varsta
    df3.to_feather("excel/output.feather")

    with final:

        st.success("Efectuat cu Success")
        # st.dataframe(dc)

    progress.progress(100, "Progress")
    st.markdown("---")
    st.write("Aici e tabelul transformat in excel:\n")
    st.write(df)

    if show == 1:
        st.success("Vezi ca la toate tabelasele de mai sus poti sa ordonezi in functie de fiecare coloana.\n FYI pentru orice inseamna data(de tiparire sau internare etc) nu ordoneaza corect, daca o sa ai nevoie imi zici, dar altfel ai fisierul excel si faci direct acolo")

    # except:
    #     Head.exception("eroare")


side = st.sidebar.selectbox(
    "Optiuni: ",
    options=["Nu afiseaza Consola", "Afiseaza Consola"]

)


if side == "Afiseaza Consola":
    executeProject(1)

elif side == "Nu afiseaza Consola":
    executeProject(0)
    st.markdown("---")
    st.write("Consola nu e afisata")
    st.markdown("---")

# ideee algoritm gasit chestii din investigatii


'''
keys = ["clor", "colesterol", "acid uric seric"]

investigatii = "..."  textul cu investigatii

investigatii.replace(";",",").split(",")

investigatii == ["Sediment automat - Hematii:ABSENTE","Eritrocite (BLD):NEGATIV mg/dL",...]

for i in range (len(keys)):

    if keys[i] in investigatii: # dar facut cu fuzzy search pentru ca pot exista typo-uri
        valoare = findField(":","unitati de masura") # aflam valoarea pentru keyul respectiv





data:{
            keys[i]: valoare

        }        






'''
