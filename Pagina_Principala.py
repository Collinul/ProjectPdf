import streamlit as st
import pandas as pd
import openpyxl
import plotly.express as px
st.set_page_config(page_title="HomePage", layout="wide",
                   page_icon=":sun_with_face:")

hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>

"""
st.markdown(hide_st_style, unsafe_allow_html=True)

df = pd.read_excel("excel/output.xlsx")
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
df_selection = df.query(
    "Urgenta == @urgenta & Dislipidemic == @dislipidemic & Diabet == @diabet"
)

#-----------MainPage------
st.title(":bar_chart: Pagina Principala")
st.markdown("##")

# top kpi's
procent_diabetici = round(((df_selection["Diabet"]=="DA").sum()*100)/len(df_selection["Diabet"]),2)
procent_hipertensiv = round(((df_selection["Hipertensiune"]=="DA").sum()*100)/len(df_selection["Hipertensiune"]),2)
procent_dislipidemic = round(((df_selection["Dislipidemic"]=="DA").sum()*100)/len(df_selection["Dislipidemic"]),2)
procent_infarct =round(((df_selection["Antecedente infarct"]=="DA").sum()*100)/len(df_selection["Antecedente infarct"]),2)
medie_internat = round(df_selection["Numar zile"].mean(),2)

column1, column2, column3, column4, column5 = st.columns(5)

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
with column5:
    st.subheader("Cat este un pacient internat in medie:")
    st.subheader(f"{medie_internat} Zile")

st.markdown("---")

st.table(df_selection)

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