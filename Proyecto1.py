import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import dash_table
import statsmodels.api as sm

def cargar_y_preparar():    
    df = pd.read_csv("datos_cauca.csv")
    df.columns = df.columns.str.lower().str.strip()

    #Solo permitir los que tienen consentimiento
    df = df[df["estu_estadoinvestigacion"] == "PUBLICAR"]

    # Eliminar faltantes y duplicados
    df = df.drop_duplicates()
    df = df.dropna(subset=[
        "punt_ingles",
        "punt_matematicas",
        "punt_sociales_ciudadanas",
        "punt_c_naturales",
        "punt_lectura_critica"
    ])

    #Arrego estrato
    df["fami_estratovivienda"] = df["fami_estratovivienda"].str.extract(r"(\d)").astype(float)

    # Calcular puntaje de icfes
    df["punt_global"] = df["punt_global"].fillna(
        ((df[
            ["punt_matematicas",
            "punt_sociales_ciudadanas",
            "punt_c_naturales",
            "punt_lectura_critica"]
        ].sum(axis=1)*3 + df["punt_ingles"] )/ 13) * 5
    )


    cols_areas = [
        "punt_ingles",
        "punt_matematicas",
        "punt_sociales_ciudadanas",
        "punt_c_naturales",
        "punt_lectura_critica"
    ]

    # Validar rangos y tipo de datos
    for col in cols_areas:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df[(df[col] >= 0) & (df[col] <= 100)]

    df["punt_global"] = pd.to_numeric(df["punt_global"], errors="coerce")
    df = df[(df["punt_global"] >= 0) & (df["punt_global"] <= 500)]

    # Nueva variable de clasificación cualitativa por cuartiles
    df["nivel_global"] = pd.qcut(
        df["punt_global"],
        4,
        labels=["Bajo", "Medio", "Alto", "Muy Alto"],
        duplicates="drop"
    )

    # Nueva variable promedio por áreas
    df["promedio_areas"] = df[cols_areas].mean(axis=1)

    #######PREGUNTA 1
    desigualdad = df.groupby("estu_mcpio_reside")["punt_global"].agg(
        promedio="mean",
        desviacion="std",
        cantidad="count"
    ).reset_index()

    desigualdad = desigualdad.sort_values("desviacion", ascending=False)
    desigualdad["coef_variacion"] = (
            desigualdad["desviacion"] / desigualdad["promedio"]
        )
    #############
    #Posibles relaciones con el coeficiente de variación
    hetero_estrato = (
        df.groupby("estu_mcpio_reside")["fami_estratovivienda"]
        .std()
        .reset_index(name="desv_estrato")
    )
    desigualdad = desigualdad.merge(hetero_estrato,
                                    on="estu_mcpio_reside",
                                    how="left")

    prop_rural = (
        df.groupby("estu_mcpio_reside")
        .apply(lambda x: (x["cole_area_ubicacion"] == "RURAL").mean())
        .reset_index(name="prop_rural")
    )
    desigualdad = desigualdad.merge(prop_rural,
                                    on="estu_mcpio_reside",
                                    how="left")

    #############
    # 1. entender como se distribuye el puntaje global según el nivel educativo de los padres
    # Limpiar categorías no válidas
    categorias_excluir = ["No Aplica", "No sabe", "Ninguno"]

    df = df[
        (~df["fami_educacionpadre"].isin(categorias_excluir)) &
        (~df["fami_educacionmadre"].isin(categorias_excluir))].copy()

    # ORDEN EDUCATIVO PERSONALIZADO
    orden_educativo = [
        "Primaria incompleta",
        "Primaria completa",
        "Secundaria (Bachillerato) incompleta",
        "Secundaria (Bachillerato) completa",
        "Técnica o tecnológica incompleta",
        "Técnica o tecnológica completa",
        "Educación profesional incompleta",
        "Educación profesional completa",
        "Postgrado"]

    # 2Convertir variables en categóricas ordenadas
    df["fami_educacionpadre"] = pd.Categorical(
        df["fami_educacionpadre"],
        categories=orden_educativo,
        ordered=True)

    df["fami_educacionmadre"] = pd.Categorical(
        df["fami_educacionmadre"],
        categories=orden_educativo,
        ordered=True)
    #LIMPIEZA Y ORGANIZACION DE VARIABLES
    #Variable binaria - pertenencia al cuartil bajo
    df["es_bajo"] = (df["nivel_global"] == "Bajo").astype(int)

    #Crear df con las variables de interés
    df_p3 = df[["cole_area_ubicacion","estu_privado_libertad", "fami_cuartoshogar", 
                "fami_estratovivienda", "fami_personashogar", 
                "fami_tieneautomovil", "fami_tienecomputador", 
                "fami_tieneinternet", "fami_tienelavadora" ,"es_bajo"]]

    #Cambiar el nombre de los headers 
    df_p3.rename(columns={
        "cole_area_ubicacion": "zona",
        "estu_privado_libertad": "privado",
        "fami_cuartoshogar": "cuartos",
        "fami_estratovivienda": "estrato",
        "fami_personashogar": "personas",
        "fami_tieneautomovil": "carro",
        "fami_tienecomputador": "pc",
        "fami_tieneinternet": "internet",
        "fami_tienelavadora": "lavadora",
    }, inplace=True)

    # Convertir a número o a variables binarias 
        #Revisar los valores que entran a cada variable y cambiarlo si es necesario
    df_p3["privado"] = df_p3["privado"].map({"S": 1,"N": 0})
    df_p3["estrato"] = df_p3["estrato"].fillna(0) 
    df_p3["carro"] = df_p3["carro"].map({"Si": 1,"No": 0}) 
    df_p3["pc"] = df_p3["pc"].map({"Si": 1,"No": 0})
    df_p3["internet"] = df_p3["internet"].map({"Si": 1,"No": 0})
    df_p3["lavadora"] = df_p3["lavadora"].map({"Si": 1,"No": 0})

    #ANALISIS ESTADISTICO POR VARIABLE
    ###Estrato
    #Agrupar estratos en categorías más amplias
    df_p3["estrato_grupo"] = df_p3["estrato"].fillna(0)
    df_p3["estrato_grupo"] = df_p3["estrato_grupo"].map({
        0: "No reporta",
        1: "Estrato 1",
        2: "Estrato 2",
        3: "Estrato 3+",
        4: "Estrato 3+",
        5: "Estrato 3+",
        6: "Estrato 3+"})

    ###Zona     
    #Barras apiladas para mejor comprensión
    return df, df_p3, desigualdad, orden_educativo

def analisis_regresion(desigualdad):
    variables = ["promedio", "cantidad", "desv_estrato", "prop_rural"]
    resultados = []

    for var in variables:
        X = sm.add_constant(desigualdad[[var]])
        y = desigualdad["coef_variacion"] 
        modelo = sm.OLS(y, X).fit()

        resultados.append({
            "Variable": var,
            "R²": round(float(modelo.rsquared), 4),
            "p-value": round(float(modelo.pvalues[var]), 4),})
        
    mapeo = {
    "prop_rural": "Proporción rural",
    "desv_estrato": "Desviación del estrato",
    "cantidad": "Cantidad de estudiantes",
    "promedio": "Promedio del puntaje"}

    df_modelos = pd.DataFrame(resultados).sort_values("R²", ascending=False)
    df_modelos["Variable"] = df_modelos["Variable"].map(mapeo)

    tabla_modelos = dash_table.DataTable(
        data=df_modelos.to_dict("records"),
        columns=[{"name": c, "id": c} for c in df_modelos.columns],
        sort_action="native",
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center", "padding": "6px"})

    return tabla_modelos

def pregunta1(df, desigualdad):
    #Métrica
    tabla_modelos = analisis_regresion(desigualdad)
    
    #Calcular coeficiente de variación y usarlo en gráficas
    desigualdad = desigualdad.copy()
    desigualdad["coef_variacion"] = (
        desigualdad["desviacion"] / desigualdad["promedio"]
    )

    top_desigualdad = desigualdad.sort_values(
        "desviacion", ascending=False)
    top10 = top_desigualdad.head(10)
    top_coef = desigualdad.sort_values(
        "coef_variacion", ascending=False)

    top_desigualdad = desigualdad.sort_values(
        "coef_variacion", ascending=False)
    top10 = top_desigualdad.head(10)
    municipios_top = top10["estu_mcpio_reside"]
    
    #Boxplot
    df_top = df[df["estu_mcpio_reside"].isin(municipios_top)]

    fig_p1_1 = px.box(
        df_top,
        x="estu_mcpio_reside",
        y="punt_global",
        title="Distribución del puntaje en municipios con mayor coeficiente de variación",
         labels={
            "estu_mcpio_reside": "Municipio de residencia",
            "punt_global": "Puntaje global"})

    fig_p1_1.update_layout(
        xaxis_tickangle=45)

    #Grafico de barras
    top10 = top10.copy()

    colores = ["darkred"] + ["lightcoral"]*(len(top10)-1)
    top10["color"] = colores

    fig_p1_2 = px.bar(
        top10,
        x="estu_mcpio_reside",
        y="coef_variacion",
        title="Top 10 municipios con mayor coeficiente de variación",
        color="color",
        color_discrete_map="identity",
        labels={"estu_mcpio_reside": "Municipio de residencia", 
                "coef_variacion": "Coeficiente de variación"})

    fig_p1_2.update_layout(
        xaxis_tickangle=45)

    return fig_p1_1, fig_p1_2, tabla_modelos

def pregunta2(df, orden_educativo):
    # TABLA PADRE
    tabla_padre = df.groupby("fami_educacionpadre")["punt_global"].agg(
        n_estudiantes="count",media="mean",desviacion="std").reset_index().sort_values("fami_educacionpadre")

    tabla_padre["media"] = tabla_padre["media"].round(2)
    tabla_padre["desviacion"] = tabla_padre["desviacion"].round(2)

    # Visualización padre
    tabla_padre_dash = dash_table.DataTable(
        data=tabla_padre.to_dict("records"),
        columns=[{"name": c, "id": c} for c in tabla_padre.columns],
        page_size=10,
        sort_action="native",
        filter_action="native",
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center", "padding": "6px"},)

    # TABLA MADRE
    tabla_madre = df.groupby("fami_educacionmadre")["punt_global"].agg(n_estudiantes="count",media="mean",desviacion="std").reset_index().sort_values("fami_educacionmadre")
    tabla_madre["media"] = tabla_madre["media"].round(2)
    tabla_madre["desviacion"] = tabla_madre["desviacion"].round(2)

    # Visualización madre
    tabla_madre_dash = dash_table.DataTable(
        data=tabla_madre.to_dict("records"),
        columns=[{"name": c, "id": c} for c in tabla_madre.columns],
        page_size=10,
        sort_action="native",
        filter_action="native",
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center", "padding": "6px"})

    # GRÁFICO DE BARRAS COMBINADO
    df_padre = df.groupby("fami_educacionpadre")["punt_global"].mean().reset_index()
    df_padre = df_padre.rename(columns={"punt_global": "promedio_punt_global"})

    df_madre = df.groupby("fami_educacionmadre")["punt_global"].mean().reset_index()
    df_madre = df_madre.rename(columns={"punt_global": "promedio_punt_global"})

    niveles_comunes = [
        nivel for nivel in orden_educativo
        if nivel in df_padre["fami_educacionpadre"].values
        and nivel in df_madre["fami_educacionmadre"].values]

    padre_plot = df_padre[
        df_padre["fami_educacionpadre"].isin(niveles_comunes)
    ].set_index("fami_educacionpadre").loc[niveles_comunes].reset_index()

    madre_plot = df_madre[
        df_madre["fami_educacionmadre"].isin(niveles_comunes)
    ].set_index("fami_educacionmadre").loc[niveles_comunes].reset_index()

    fig_p2_3 = go.Figure()
    fig_p2_3.add_trace(go.Bar(
        x=niveles_comunes,
        y=padre_plot["promedio_punt_global"],
        name="Padre"))
    
    fig_p2_3.add_trace(go.Bar(
        x=niveles_comunes,
        y=madre_plot["promedio_punt_global"],
        name="Madre"))

    fig_p2_3.update_layout(
        barmode="group",
        title="Puntaje promedio según nivel educativo de los padres",
        xaxis_title="Nivel educativo",
        yaxis_title="Puntaje Global Promedio",
        xaxis_tickangle=45,
        legend_title_text="")

    # MATRIZ CRUZADA PADRE × MADRE
    df_matriz = (df.pivot_table(
            values="punt_global",
            index="fami_educacionpadre",
            columns="fami_educacionmadre",
            aggfunc="mean").round(2))

    df_matriz_conteo = df.pivot_table(values="punt_global",index="fami_educacionpadre",columns="fami_educacionmadre",aggfunc="count")
    
    # HEATMAP PADRE × MADRE
    df_matriz_ordenada = df_matriz.reindex(index=orden_educativo,columns=orden_educativo)
    df_conteo_ordenado = df_matriz_conteo.reindex(index=orden_educativo,columns=orden_educativo)

    # poner en blanco combinaciones con menos de 100 estudiantes
    df_matriz_filtrada = df_matriz_ordenada.where(df_conteo_ordenado >= 30)
    
    #Visualizar
    fig_p2_4 = px.imshow(
        df_matriz_filtrada,
        aspect="auto",
        title="Puntaje promedio según combinación educativa Padre × Madre (solo combinaciones con ≥ 30 estudiantes)",
        labels={"color": "Puntaje Global Promedio"})

    fig_p2_4.update_layout(
        xaxis_tickangle=45)

    return tabla_padre_dash, tabla_madre_dash, fig_p2_3, fig_p2_4

def pregunta3(df_p3):
    #Grafica: estrato, zona y nivel bajo
    df_p3 = df_p3.copy()
    tabla_comp = (
        pd.crosstab(
            [df_p3["estrato_grupo"], df_p3["zona"]],
            df_p3["es_bajo"],
            normalize="index") * 100).round(2)

    tabla_comp.columns = ["No bajo", "Bajo"]
    tabla_comp_bajo = tabla_comp["Bajo"].unstack()

    #Grafico de barras agrupadas
    df_plot1 = tabla_comp_bajo.reset_index().melt(
        id_vars="estrato_grupo",
        var_name="zona",
        value_name="pct_bajo")

    fig_p3_1 = px.bar(
        df_plot1,
        x="estrato_grupo",
        y="pct_bajo",
        color="zona",
        barmode="group",
        title="Proporción de nivel bajo por Estrato y Zona",
        labels={"estrato_grupo": "Estrato", "pct_bajo": "% en nivel bajo", "zona": "Zona"},
        color_discrete_sequence=["indigo", "deepskyblue"])
    fig_p3_1.update_layout(xaxis_tickangle=30)

    ###Posesión de bienes
    cols_bienes = ["carro", "internet", "pc", "lavadora"]
    df_p3["indice_bienes"] = df_p3[cols_bienes].sum(axis=1, min_count=1)#no muestra filas NaN
    df_p3["indice_bienes"].value_counts().sort_index()

    tabla_bienes =(pd.crosstab(df_p3["indice_bienes"], df_p3["es_bajo"], normalize="index")*100).sort_index()

    #Graficar
    etiquetas_bienes = {
        0: "Sin bienes",
        1: "1 bien",
        2: "2 bienes",
        3: "3 bienes",
        4: "4 bienes"}
    
    tabla_bienes = tabla_bienes.reindex([0, 1, 2, 3, 4])  # en caso de que falte algún nivel
    tabla_bienes.index = [etiquetas_bienes[i] for i in tabla_bienes.index]
    tabla_bienes = tabla_bienes.rename(columns={0: "No es bajo", 1: "Es bajo"})

    tabla_bienes_reset = tabla_bienes.reset_index().rename(columns={"index": "indice_bienes"})

    df_plot2 = tabla_bienes_reset.melt(
    id_vars="indice_bienes",
    var_name="nivel",
    value_name="porcentaje")

    fig_p3_2 = px.bar(
        df_plot2,
        x="indice_bienes",
        y="porcentaje",
        color="nivel",
        barmode="stack",
        title="Proporción de estudiantes en nivel bajo según bienes",
        labels={"indice_bienes": "Cantidad de bienes del hogar", "porcentaje": "Porcentaje (%)", "nivel": ""},
        color_discrete_map={"No es bajo": "thistle", "Es bajo": "indigo"})
    
    fig_p3_2.update_layout(xaxis_tickangle=0)

    #SINTESIS 
    #Tabla comparativa de brechas
    brecha_estrato = (df_p3.groupby("estrato_grupo")["es_bajo"].mean().mul(100))
    brecha_estrato_val = brecha_estrato.max() - brecha_estrato.min()
    
    brecha_zona = (df_p3.groupby("zona")["es_bajo"].mean().mul(100))
    brecha_zona_val = brecha_zona.max() - brecha_zona.min()

    brecha_bienes = (df_p3.groupby("indice_bienes")["es_bajo"].mean().mul(100))
    brecha_bienes_val = brecha_bienes.max() - brecha_bienes.min()

    resumen_brechas = pd.DataFrame({
        "Dimensión": ["Estrato", "Zona", "Bienes"],
        "Brecha (pp)": [
            brecha_estrato_val,
            brecha_zona_val,
            brecha_bienes_val]})
    
    resumen_brechas = resumen_brechas.sort_values(by="Brecha (pp)", ascending=False)

    fig_p3_3 = px.bar(
        resumen_brechas,
        x="Dimensión",
        y="Brecha (pp)",
        title="Comparación de intensidad de desigualdad",
        labels={"Dimensión": "", "Brecha (pp)": "Brecha en puntos porcentuales"},
        color_discrete_sequence=["indigo"])
    
    fig_p3_3.update_layout(xaxis_tickangle=0)

    return fig_p3_1, fig_p3_2, fig_p3_3