import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd


#site config
st.set_page_config(page_title="Extract", layout="wide",  page_icon=":sun_with_face:")
st.header("Aici ma joc eu cu datele , nu baga in seama  ")
st.title("Data")
#File logic
#TODO: make it so you can put any number of pdfs as input serve the data to dataframe logic



path = "pdf/AFTINIE GRIGORITA.pdf"
pdfFile=open(path,"rb")



viewer = PdfReader(pdfFile)
text = viewer.pages[0].extract_text()
# st.write(f"Asta e text:{text}")
textArray = text.capitalize().split('\n')

#functions
@st.cache_data
def findKey(keyword,text):
    res=[]
    mystring = text
   
    before_keyword, keyword, after_keyword = mystring.partition(keyword)
    # st.write(f"before_keyword: {before_keyword}\n, keyword: {keyword}\n, after_keyword: {after_keyword}\n")
    res.append(before_keyword)
    res.append(keyword)
    res.append(after_keyword)
    return res

#dataframe logic
temp1 = findKey('Perioada internarii: ', text)
temp2 = findKey('Medic: ', text)
perioada=temp1[2].replace(temp2[2],'').replace(temp2[1],'')
st.write(f"Perioada: {perioada}")

nume=[]
prenume=[]
dataTiparire=[]
chomp = text.split()
# print("chomp:\n",chomp)

@st.cache_data
def writeWord(array,i) :
    return array[i]


for i in range (len(textArray)-1):
    st.write(f"chomp[{i}]: {writeWord(chomp,i)}")
    if(str(chomp[i]) == "NUMELE"):  
        nume.append(chomp[i+1])
    if(str(chomp[i])  == "PRENUMELE"):
        prenume.append(chomp[i+1])
    if("tiparire" in chomp[i]):
        dataTiparire.append(chomp[i+1])
     

data = {
    "Data Tiparire":dataTiparire,
    "Nume":nume,
    "Prenume": prenume,
    "Perioada Internarii": perioada
}
df = pd.DataFrame(data)

with pd.ExcelWriter("excel/output.xlsx") as writer:
    df.to_excel(writer, sheet_name="Output", index=False)
st.write(df)