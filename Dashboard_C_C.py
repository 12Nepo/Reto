# Librerías
import pandas as pd 
import streamlit as st 
import plotly.express as px

# Configuración inicial de la página
st.set_page_config(
    page_title="Dashboard Calor y Control",
    page_icon="🔥",
    layout="wide")
# Título del Dasboard 
st.title("Dashboard Calor y Control 🔥")

# Datos a utilizar 
# Facturación 
# Cargar archivos a utilizar 
df = px.data.gapminder().query("country == 'Mexico'")
fac = pd.read_excel("Facturacion.xlsx", sheet_name="FACTURACION")
devo = pd.read_excel("Facturacion.xlsx", sheet_name="DEVOLUCIONES")
notas = pd.read_excel("Facturacion.xlsx", sheet_name="NOTAS DE CREDITO")
total_gastos = pd.read_csv("Gastos_concatenado.csv")
detalle = pd.read_csv("Detalle precios y productos fabricados 2022.csv")

# Procesamiento previo para KPI´s 
# Preprocesamiento Facturación 
# Agrupamos por fecha para obtener la cantidad total 
fac_group = fac[["FECHA_DOC", "CAN_TOT", "DES_TOT"]]
fac_group = fac_group.groupby("FECHA_DOC").sum()
fac_group = fac_group.reset_index()

# Preprocesamiento Devoluciones 
devo_group = devo[["FECHA_DOC", "CAN_TOT"]]
devo_group = devo_group.groupby("FECHA_DOC").sum()
devo_group = devo_group.reset_index()

# Procesamiento notas 
notas_group = notas[["FECHA_DOC", "CAN_TOT"]]
notas_group = notas_group.groupby("FECHA_DOC").sum()
notas_group = notas_group.reset_index()

# Procesamiento gráfica de pastel 
# Facturación 
fac_group_f = fac_group[["FECHA_DOC","CAN_TOT"]]
# Formato fechas 
fac_group_f["FECHA_DOC"] = pd.to_datetime(fac_group_f["FECHA_DOC"])
fac_group_f["Tipo"] = "Facturación"

# Descuentos 
fac_group_d = fac_group[["FECHA_DOC","DES_TOT"]]
fac_group_d["Tipo"] = "Descuento"
fac_group_d["CAN_TOT"] = fac_group_d["DES_TOT"]
fac_group_d = fac_group_d[["FECHA_DOC","CAN_TOT", "Tipo"]]
# Devoluciones 
devo_group_2 = devo_group[["FECHA_DOC","CAN_TOT"]]
devo_group_2["Tipo"] = "Devolucion"
# Notas 
notas_group_2 = notas_group[["FECHA_DOC","CAN_TOT"]]
notas_group_2["Tipo"] = "Notas"

# Unión de dataframes 
# Los concatenas verticalmente con axis=0
dfs = [fac_group_f, fac_group_d, devo_group_2, notas_group_2]
df_ingresos = pd.concat(dfs, axis=0)
df_ingresos["FECHA_DOC"] = pd.to_datetime(df_ingresos["FECHA_DOC"])

# Cálculo de ingresos 
# Facturación 
fac_group_f_1 = fac_group_f
fac_group_f_1.rename(columns={"CAN_TOT": "FACT"}, inplace=True)
fac_group_f_1 = fac_group_f_1[["FACT", "FECHA_DOC"]]

# Descuentos 
fac_group_d_1 = fac_group_d
fac_group_d_1.rename(columns={"CAN_TOT": "DES"}, inplace=True)
fac_group_d_1 = fac_group_d_1[["DES", "FECHA_DOC"]]

# Devoluciones 
devo_group_1 = devo_group.copy()
devo_group_1.rename(columns={"CAN_TOT": "DEVO"}, inplace=True)
devo_group_1 = devo_group_1[["DEVO", "FECHA_DOC"]]

# Notas  
notas_group_1 = notas_group
notas_group_1.rename(columns={"CAN_TOT": "NOTAS"}, inplace=True)
notas_group_1 = notas_group_1[["NOTAS", "FECHA_DOC"]]
# Agrupamos 
ingresos_merge = fac_group_f_1.merge(fac_group_d_1, on='FECHA_DOC', how='outer').merge(devo_group_1, on='FECHA_DOC', how='outer').merge(notas_group_1, on='FECHA_DOC', how='outer')
ingresos_full = ingresos_merge.groupby("FECHA_DOC").sum().reset_index()

# Calculemos los ingresos 
ingresos_full["Ingresos"] = ingresos_full["FACT"] - ingresos_full["DES"] - ingresos_full["DEVO"] + ingresos_full["NOTAS"]

# Calculos egresos 
# Detalle de precios 
detalle = detalle[["COSTO_TOTAL_CALCULADO", "FECHA_DOC"]]
# Cambiar tipos de datos
# Nos deshacemos del signo $
detalle['COSTO_TOTAL_CALCULADO'] = detalle['COSTO_TOTAL_CALCULADO'].replace({'\$': '', ',': ''}, regex=True)
detalle["COSTO_TOTAL_CALCULADO"] =detalle["COSTO_TOTAL_CALCULADO"].astype(float)
detalle_group = detalle.groupby("FECHA_DOC").sum().reset_index()

# Cambiar formato de fecha
total_gastos["FECHA"] = pd.to_datetime(total_gastos["FECHA"])
total_gastos.rename(columns={"FECHA": "FECHA_DOC"}, inplace=True)
# Convertimos los gastos a valores positivos 
total_gastos['IMPORTE'] = total_gastos['IMPORTE'].abs()
total_gastos = total_gastos[["FECHA_DOC", "IMPORTE"]]
gastos_group = total_gastos.groupby("FECHA_DOC").sum().reset_index()

# Unificar formato de fechas
total_gastos["FECHA_DOC"] = pd.to_datetime(total_gastos["FECHA_DOC"])
detalle["FECHA_DOC"] = pd.to_datetime(detalle["FECHA_DOC"], format="%d/%m/%Y %H:%M")




# Mostrar el widget de entrada de fecha
start_date = pd.to_datetime(st.date_input("Fecha de inicio:"))
end_date = pd.to_datetime(st.date_input("Fecha de fin:"))

# Validar que la fecha de inicio sea menor que la fecha de fin

if start_date < end_date:
    # Filtrar el dataframe por el rango de fechas
    mask = (fac_group["FECHA_DOC"] > start_date) & (fac_group["FECHA_DOC"] <= end_date)
    fac_group = fac_group.loc[mask]
    # Filtrar el segundo dataframe por el rango de fechas
    mask2 = (ingresos_full["FECHA_DOC"] > start_date) & (ingresos_full["FECHA_DOC"] <= end_date)
    ingresos_full = ingresos_full.loc[mask2]
    # Filtrar el tercer dataframe por el rango de fechas
    mask3 = (df_ingresos["FECHA_DOC"] > start_date) & (df_ingresos["FECHA_DOC"] <= end_date)
    df_ingresos = df_ingresos.loc[mask3]

    mask5 = (gastos_group["FECHA_DOC"] >= start_date) & (gastos_group["FECHA_DOC"] <= end_date)
    gastos_group = gastos_group[mask5]

    mask6 = (detalle_group["FECHA_DOC"] >= start_date) & (detalle_group["FECHA_DOC"] <= end_date)
    detalle_group = detalle_group[mask6]

else:
    # Mostrar un mensaje de error
    st.error("Error: La fecha de fin debe ser mayor que la fecha de inicio.")


# Obtenemos la suma de la columna "Ingresos"
total_ingresos = ingresos_full["Ingresos"].sum()


# Crear primera fila de KPI´s
# Definimos una función que formatea el número con comas

def format_number_with_commas(number):
    return "{:,.2f}".format(number)

# create three columns
kpi1, kpi2, kpi3 = st.columns(3)

kpi1.metric(
    label="Utilidad 💸",
    value=format_number_with_commas(total_ingresos - gastos_group['IMPORTE'].sum() + detalle_group["COSTO_TOTAL_CALCULADO"].sum()),
)


kpi2.metric(
    label="Ingresos 🤑",
    value= format_number_with_commas(total_ingresos)
)

kpi3.metric(
    label="Egresos 😥",
    value= format_number_with_commas(gastos_group['IMPORTE'].sum() + detalle_group["COSTO_TOTAL_CALCULADO"].sum())
)


# Gráficas
# Creamos 3 columnas 
fig_col1, fig_col2, fig_col3 = st.columns(3, gap="large")
#fig_col1, fig_col2, fig_col3 = st.columns([0.25, 0.5, 0.25])
with fig_col1:
    st.markdown("<h4 style='text-align: center'>Desglose de ingresos</h4>", unsafe_allow_html=True)
    fig = px.pie(df_ingresos, values='CAN_TOT', names='Tipo', color='Tipo', color_discrete_sequence=["#0e8a7e", "#006c6a", "#4ec8be", "#8efefe"],
              height=300, width=300)
    st.write(fig)
   
with fig_col2:
    st.markdown("<h4 style='text-align: center'>Ingresos</h4>", unsafe_allow_html=True)
    fig1 = px.line(ingresos_full, x="FECHA_DOC", y="Ingresos", hover_data=['FECHA_DOC', 'Ingresos'], height=300, width=300)
    fig1.update_xaxes(title_text="Fecha")
    fig1.update_yaxes(title_text="Ingresos totales")
    fig1.update_traces(line_color="#0e8a7e")
    st.write(fig1)

with fig_col3:
    st.markdown("<h4 style='text-align: center'>Utilidad</h4>", unsafe_allow_html=True)
    fig3 = px.line(fac_group, x="FECHA_DOC", y="CAN_TOT", hover_data=['FECHA_DOC', 'CAN_TOT'], height=300, width=300)
    fig3.update_traces(line_color="#0e8a7e")
    st.write(fig3)

# Creamos otro contenedor con 3 columnas
fig_col4, fig_col5, fig_col6 = st.columns(3, gap="large")
#fig_col4, fig_col5, fig_col6 = st.columns([0.25, 0.5, 0.25])
with fig_col4:
    st.markdown("<h4 style='text-align: center'>Egresos</h4>", unsafe_allow_html=True)
    fig4 = px.line(fac_group, x="FECHA_DOC", y="CAN_TOT", hover_data=['FECHA_DOC', 'CAN_TOT'], height=300, width=300)
    fig4.update_traces(line_color="#0e8a7e")
    st.write(fig4)
