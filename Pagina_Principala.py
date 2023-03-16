import streamlit as st
import pandas as pd
import openpyxl
import plotly.express as px
import time

from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
st.set_page_config(page_title="HomePage", layout="wide",
                   page_icon=":sun_with_face:")

hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>

"""
def getVarsta(df):

    temp_varsta = df["Varsta"].values.tolist()
    
    varsta=[]
    for i in range (len(temp_varsta)):
        varsta.append(int(temp_varsta[i][:2]))
    return varsta


st.markdown(hide_st_style, unsafe_allow_html=True)
   
df = pd.read_feather("excel/output.feather")
st.dataframe(df)

urgenta = st.sidebar.multiselect(
    "Urgenta:",
    options = df["Urgenta"].unique(),
    default = df["Urgenta"].unique()
)
dislipidemic = st.sidebar.multiselect(
    "Dislipidemic:",
    options = df["Dislipidemic"].unique(),
    default = df["Dislipidemic"].unique()
)
diabet = st.sidebar.multiselect(
    "Diabet:",
    options = df["Diabet"].unique(),
    default = df["Diabet"].unique(),
)
insulina = st.sidebar.multiselect(
    "Insulina:",
    options = df["Insulina"].unique(),
    default = df["Insulina"].unique(),
)
st.sidebar.markdown("---")
h=[]



df_selection = df.query(
    "Urgenta == @urgenta & Dislipidemic == @dislipidemic & Diabet == @diabet & Insulina == @insulina"
)
varsta = getVarsta(df_selection)

age_min = st.sidebar.text_input(
    "Limita inferioara a varstei:",
    value= int(min(varsta))
)
age_max = st.sidebar.text_input(
    "Limita superioara a varstei:",
    value = int(max(varsta))
)
a_m = int(age_min)
a_M = int(age_max)

df_selection["Slider"] = varsta
df_selection  = df_selection.query("Slider <= @a_M & Slider >= @a_m")

# if 'index' in df_selection.columns:
#     df_selection.drop('index', axis =1)
#-----------MainPage------
st.title(":bar_chart: Pagina Principala")
st.markdown("##")
st.markdown("---")


# top kpi's
procent_diabetici = round(((df_selection["Diabet"]=="DA").sum()*100)/len(df_selection["Diabet"]),2)
procent_hipertensiv = round(((df_selection["Hipertensiune"]=="DA").sum()*100)/len(df_selection["Hipertensiune"]),2)
procent_dislipidemic = round(((df_selection["Dislipidemic"]=="DA").sum()*100)/len(df_selection["Dislipidemic"]),2)
procent_infarct =round(((df_selection["Antecedente infarct"]=="DA").sum()*100)/len(df_selection["Antecedente infarct"]),2)

column1, column2, column3, column4 = st.columns(4)

with column1:
    st.subheader("Cati Diabetici din Total pacienti prezentati:")
    st.subheader(f"{procent_diabetici}%")
with column2:
    st.subheader("Cati Hipertensivi din Total pacienti prezentati:")
    st.subheader(f"{procent_hipertensiv}%")
with column3:
    st.subheader("Cati Dislipidemici din Total pacienti prezentati:")
    st.subheader(f"{procent_dislipidemic}%")
with column4:
    st.subheader("Cati au Antecedente de Infarct din Total pacienti prezentati:")
    st.subheader(f"{procent_infarct}%")


st.markdown("---")
df_selection = df_selection.drop("Slider",axis=1 ).reset_index().set_index("index")
st.table(df_selection)
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output)
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    # format1 = workbook.add_format({'num_format': '0.00'}) 
    # worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data
df_xslx = to_excel(df_selection)
def downloadTable():
    with pd.ExcelWriter("excel/filteredTable.xlsx") as writer:
            df_selection.to_excel(writer, sheet_name="Output", index=False, data= "excel/filteredTable.xlsx")

st.download_button(label = "Download Table",file_name="Pacienti.xlsx", data=df_xslx)
st.markdown("---")
data_Hipertensiune = (df_selection["Hipertensiune"]=="DA").sum()
data_Diabet = (df_selection["Diabet"]=="DA").sum()
data_Dislipidemic = (df_selection["Dislipidemic"]=="DA").sum()
data_Infarct= (df_selection["Antecedente infarct"]=="DA").sum()
data_Urgenta = (df_selection["Urgenta"]=="DA").sum()
total = [data_Urgenta,data_Hipertensiune,data_Diabet,data_Infarct,data_Dislipidemic]


data_nume = ["Urgenta","Hipertensiune","Diabet","Dislipidemic","Antecedente infarct"]
data_all = {
    "Total":total,
    "Nume":data_nume
}
df_all = pd.DataFrame(data_all)


fig_procente = px.bar(
    df_all,
    x="Nume",
    y="Total",
    orientation="v",
    range_y= (0,len(df_selection.index))

)
st.plotly_chart(fig_procente)