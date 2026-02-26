import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

df = pd.read_csv("datos_cauca.csv")
df_original = df.copy()
df.columns = df.columns.str.lower().str.strip()

total = len(df)
print("Total datos iniciales sin modificación:", total)

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

# Reporte de impacto
print("Tamaño final:",df.shape) 
print("Encabezado DataFrame:",df.head())
print("Registros iniciales:", df_original.shape[0])
print("Tomas con datos faltantes:", df_original.isna().sum())
print("Registros finales:", df.shape[0])
print("Porcentaje eliminado:", 
      round((1 - df.shape[0]/df_original.shape[0]) * 100, 2), "%")
print("Duplicados:", df_original.duplicated().sum())


#######PREGUNTA 1
print("Número de municipios:", df["estu_mcpio_reside"].nunique())
desigualdad = df.groupby("estu_mcpio_reside")["punt_global"].agg(
    promedio="mean",
    desviacion="std",
    cantidad="count"
).reset_index()

desigualdad = desigualdad.sort_values("desviacion", ascending=False)

print(desigualdad)


plt.figure()
plt.bar(desigualdad["estu_mcpio_reside"], desigualdad["desviacion"])
plt.xticks(rotation=90)
plt.title("Desigualdad interna por municipio - Cauca")
plt.xlabel("Municipio")
plt.ylabel("Desviación estándar del puntaje global")
plt.show()


plt.figure()
df.boxplot(column="punt_global", by="estu_mcpio_reside")
plt.xticks(rotation=45)
plt.title("Dispersión del puntaje global - Cauca")
plt.suptitle("")
plt.show()

#Calcular coeficiente de variación y usarlo en gráficas

desigualdad["coef_variacion"] = (
    desigualdad["desviacion"] / desigualdad["promedio"]
)

top_desigualdad = desigualdad.sort_values(
    "desviacion", ascending=False)
top10 = top_desigualdad.head(10)
print(top10)
top_coef = desigualdad.sort_values(
    "coef_variacion", ascending=False)
top10_coef = top_coef.head(10)
print(top10_coef)

top_desigualdad = desigualdad.sort_values(
    "coef_variacion", ascending=False)
top10 = top_desigualdad.head(10)
municipios_top = top10["estu_mcpio_reside"]

plt.figure()
df[df["estu_mcpio_reside"].isin(municipios_top)] \
    .boxplot(column="punt_global", by="estu_mcpio_reside")
plt.xticks(rotation=45)
plt.suptitle("")
plt.title("Distribución del puntaje en municipios con mayor coeficiente de variación de dispersión")
plt.show()

colores = ["darkred"] + ["lightcoral"]*(len(top10)-1)

plt.figure()
plt.bar(top10["estu_mcpio_reside"],
        top10["coef_variacion"],
        color=colores)

plt.xticks(rotation=45)
plt.xlabel("Municipio")
plt.ylabel("Coeficiente de variación")
plt.title("Top 10 municipios con mayor desigualdad interna")
plt.show()


plt.figure()
plt.scatter(desigualdad["promedio"],
            desigualdad["coef_variacion"])
plt.xlabel("Promedio municipal")
plt.ylabel("Coeficiente de variación")
plt.title("Relación entre desempeño promedio y desigualdad interna")
plt.show()

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

import statsmodels.api as sm

variables = ["promedio", "cantidad", "desv_estrato", "prop_rural"]

for var in variables:
    X = sm.add_constant(desigualdad[[var]])
    y = desigualdad["coef_variacion"]
    
    modelo = sm.OLS(y, X).fit()
    
    print(f"\nModelo: coef_variacion ~ {var}")
    print("R²:", round(modelo.rsquared, 4))
    print("p-value:", round(modelo.pvalues[var], 4))


################### FIN PREGUNTA 1


######## PREGUNTA 2 - EDUCACIÓN PADRES
# 1. entender como se distribuye el puntaje global según el nivel educativo de los padres
print("Estadísticas descriptivas del puntaje global:")
print(df["punt_global"].describe())

print("\nAsimetría:", round(df["punt_global"].skew(), 2))
print("Curtosis:", round(df["punt_global"].kurt(), 2))

#Histograma del puntaje global
plt.figure(figsize=(8,5))
plt.hist(df["punt_global"], bins=30)
plt.title("Distribución del Puntaje Global")
plt.xlabel("Puntaje Global")
plt.ylabel("Frecuencia")
plt.show()

# diagrama de violín
plt.figure(figsize=(6,4))
sns.violinplot(x=df["punt_global"])
plt.title("Diagrama de violín del Puntaje Global")
plt.show()

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

# TABLA PADRE
tabla_padre = df.groupby("fami_educacionpadre")["punt_global"].agg(
    n_estudiantes="count",media="mean",desviacion="std").reset_index().sort_values("fami_educacionpadre")

tabla_padre["media"] = tabla_padre["media"].round(2)
tabla_padre["desviacion"] = tabla_padre["desviacion"].round(2)

# Visualización padre
fig, ax = plt.subplots(figsize=(10, 4))
ax.axis("off")
tabla = ax.table(cellText=tabla_padre.values,colLabels=tabla_padre.columns,cellLoc="center",loc="center")

tabla.auto_set_font_size(False)
tabla.set_fontsize(10)
tabla.auto_set_column_width(col=list(range(len(tabla_padre.columns))))

plt.title("Desempeño según nivel educativo del padre", pad=20)
plt.tight_layout()
plt.show()

# 4TABLA MADRE
tabla_madre = df.groupby("fami_educacionmadre")["punt_global"].agg(n_estudiantes="count",media="mean",desviacion="std").reset_index().sort_values("fami_educacionmadre")
tabla_madre["media"] = tabla_madre["media"].round(2)
tabla_madre["desviacion"] = tabla_madre["desviacion"].round(2)

# Visualización madre
fig, ax = plt.subplots(figsize=(10, 4))
ax.axis("off")

tabla = ax.table(cellText=tabla_madre.values,colLabels=tabla_madre.columns,cellLoc="center",loc="center")

tabla.auto_set_font_size(False)
tabla.set_fontsize(10)
tabla.auto_set_column_width(col=list(range(len(tabla_madre.columns))))

plt.title("Desempeño según nivel educativo de la madre", pad=20)
plt.tight_layout()
plt.show()

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
].set_index("fami_educacionpadre").loc[niveles_comunes]

madre_plot = df_madre[
    df_madre["fami_educacionmadre"].isin(niveles_comunes)
].set_index("fami_educacionmadre").loc[niveles_comunes]

x = np.arange(len(niveles_comunes))
width = 0.35

plt.figure(figsize=(12,6))

plt.bar(x - width/2, padre_plot["promedio_punt_global"],
        width, label="Padre", color="blue")

plt.bar(x + width/2, madre_plot["promedio_punt_global"],
        width, label="Madre", color="orange")

plt.xticks(x, niveles_comunes, rotation=45, ha='right')
plt.ylabel("Puntaje Global Promedio")
plt.title("Puntaje promedio según nivel educativo de los padres")
plt.legend()
plt.tight_layout()
plt.show()

# MATRIZ CRUZADA PADRE × MADRE
df_matriz = (df.pivot_table(
        values="punt_global",
        index="fami_educacionpadre",
        columns="fami_educacionmadre",
        aggfunc="mean").round(2))

print("\nMatriz Padre x Madre (Promedios)")
print(df_matriz)

df_matriz_conteo = df.pivot_table(values="punt_global",index="fami_educacionpadre",columns="fami_educacionmadre",aggfunc="count")
# HEATMAP PADRE × MADRE
df_matriz_ordenada = df_matriz.reindex(index=orden_educativo,columns=orden_educativo)
df_conteo_ordenado = df_matriz_conteo.reindex(index=orden_educativo,columns=orden_educativo)

# poner en blanco combinaciones con menos de 100 estudiantes
df_matriz_filtrada = df_matriz_ordenada.where(df_conteo_ordenado >= 30)
plt.figure(figsize=(10,8))

im = plt.imshow(df_matriz_filtrada, aspect='auto')
plt.colorbar(im, label="Puntaje Global Promedio")
plt.xticks(np.arange(len(df_matriz_filtrada.columns)),df_matriz_filtrada.columns,rotation=45,ha='right')

plt.yticks(np.arange(len(df_matriz_filtrada.index)),df_matriz_filtrada.index)

plt.title("Puntaje promedio según combinación educativa Padre × Madre\n""(solo combinaciones con ≥ 30 estudiantes)")

plt.tight_layout()
plt.show()

########### PREGUNTA 3 - PERFIL SOCIODEMOGRAFICO
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
df["cole_area_ubicacion"].unique()#se deja así 

df["estu_privado_libertad"].unique()
df_p3["privado"] = df_p3["privado"].map({"S": 1,"N": 0})
df["estu_privado_libertad"].shape
total =df_p3["privado"].sum() #nadie es privado de su libertad

df["fami_cuartoshogar"].unique() #variables dificiles

df["fami_estratovivienda"].unique()
df_p3["estrato"] = df_p3["estrato"].fillna(0) 

df["fami_personashogar"].unique() #variables dificiles

df["fami_tieneautomovil"].unique()
df_p3["carro"] = df_p3["carro"].map({"Si": 1,"No": 0}) 

df["fami_tienecomputador"].unique()
df_p3["pc"] = df_p3["pc"].map({"Si": 1,"No": 0})

df["fami_tieneinternet"].unique()
df_p3["internet"] = df_p3["internet"].map({"Si": 1,"No": 0})

df["fami_tienelavadora"].unique()
df_p3["lavadora"] = df_p3["lavadora"].map({"Si": 1,"No": 0})

#Visualización   
pd.set_option("display.max_columns", None) #visualizar todas las columnas        
print(df_p3.head().to_string(index=False)) #imprimir sin el índice 

#ANALISIS ESTADISTICO POR VARIABLE
###Estrato
#Frecuencias y porcentajes
freq_estrato = df_p3["estrato"].value_counts(dropna=False).sort_index()
pct_estrato = df_p3["estrato"].value_counts(normalize=True, dropna=False).sort_index()

resumen_estrato = (pd.DataFrame({"N": freq_estrato, "Porcentaje": (pct_estrato*100).round(2)}))
print(resumen_estrato) # Hay una gran concentración en estratos bajos y muchos NaN.

# ~Revisar si los NaN son aleatorios para evaluar si se pueden eliminar.
# Proporción de nivel bajo en quienes NO reportan estrato
prop_nan = df_p3[df_p3["estrato"].isna()]["es_bajo"].mean() #%muy alto, no son aleatorios.
# Proporción de nivel bajo en quienes sí reportan estrato
prop_no_nan = df_p3[~df_p3["estrato"].isna()]["es_bajo"].mean()
print(prop_nan, prop_no_nan) 

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

freq_estrato_grupo = df_p3["estrato_grupo"].value_counts(dropna=False).sort_index()
pct_estrato_grupo = df_p3["estrato_grupo"].value_counts(normalize=True, dropna=False).sort_index()

resumen_estrato_grupo = (pd.DataFrame({"N": freq_estrato_grupo, "Porcentaje": (pct_estrato_grupo*100).round(2)}))

#Graficar
orden = ["Estrato 1", "Estrato 2", "Estrato 3+", "No reporta"] #asegurar orden
resumen_estrato_grupo = resumen_estrato_grupo.reindex(orden)
print(resumen_estrato_grupo)

plt.figure()
plt.bar(resumen_estrato_grupo.index, resumen_estrato_grupo["Porcentaje"],color="indigo")
plt.title("Distribución de estudiantes por grupo de estrato")
plt.xlabel("Grupo de estrato")
plt.ylabel("Porcentaje (%)")
plt.xticks(rotation=30)
plt.show()

#Hacer comparación con estratos y nivel bajo
tabla_grupo = (
    df_p3.groupby("estrato_grupo")
         .agg(
             N=("es_bajo","size"),
             prop_bajo=("es_bajo","mean")
         )
         .assign(pct_bajo=lambda x: (x["prop_bajo"]*100).round(2))
         .sort_values("pct_bajo", ascending=False))

#Graficar
plt.figure()
plt.bar(tabla_grupo.index, tabla_grupo["pct_bajo"], color="darkturquoise")
plt.title("Proporción de nivel bajo por grupo de estrato")
plt.xlabel("Grupo de estrato")
plt.ylabel("% en nivel bajo")
plt.xticks(rotation=30)
plt.show()

#Barras apiladas para mejor comprensión
tabla_stack = (pd.crosstab(df_p3["estrato_grupo"], 
                df_p3["es_bajo"], 
                normalize="index"))

tabla_stack = (tabla_stack * 100).round(2)

#Graficar 
tabla_stack.columns = ["No bajo", "Bajo"]
tabla_stack = tabla_stack.reindex(["Estrato 1", "Estrato 2", "Estrato 3+", "No reporta"])

plt.figure()
plt.bar(tabla_stack.index, tabla_stack["No bajo"], label="No bajo", color="thistle")
plt.bar(tabla_stack.index, tabla_stack["Bajo"], bottom=tabla_stack["No bajo"], label="Bajo", color="indigo")
plt.title("Composición de nivel global por grupo de estrato")
plt.xlabel("Grupo de estrato")
plt.ylabel("Porcentaje (%)")
plt.xticks(rotation=30)
plt.legend()
plt.show()

###Zona 
#Frecuencias y porcentajes
freq_zona = df_p3["zona"].value_counts()
pct_zona = df_p3["zona"].value_counts(normalize=True).mul(100).round(2)
resumen_zona = pd.DataFrame({"N": freq_zona,"Porcentaje": pct_zona}) 

#Comparación zona y nivel bajo
tabla_zona_bajo = (
    df_p3.groupby("zona")
         .agg(
             N=("es_bajo","size"),
             prop_bajo=("es_bajo","mean")
         )
         .assign(pct_bajo=lambda x: (x["prop_bajo"]*100).round(2)))

#Barras apiladas para mejor comprensión
tabla_stack_zona = (
    pd.crosstab(
        df_p3["zona"],
        df_p3["es_bajo"],
        normalize="index") * 100).round(2)

tabla_stack_zona.columns = ["No bajo", "Bajo"]

#Graficar 
plt.figure()
plt.bar(tabla_stack_zona.index, tabla_stack_zona["No bajo"], label="No bajo", color="thistle")
plt.bar(tabla_stack_zona.index, tabla_stack_zona["Bajo"], bottom=tabla_stack_zona["No bajo"], label="Bajo", color="indigo")
plt.title("Composición del nivel global por zona")
plt.xlabel("Zona")
plt.ylabel("Porcentaje (%)")
plt.legend()
plt.show()

#Grafica: estrato, zona y nivel bajo
tabla_comp = (
    pd.crosstab(
        [df_p3["estrato_grupo"], df_p3["zona"]],
        df_p3["es_bajo"],
        normalize="index") * 100).round(2)

tabla_comp.columns = ["No bajo", "Bajo"]
tabla_comp_bajo = tabla_comp["Bajo"].unstack()

#Alernativas 
#Grafico de lineas 
tabla_comp_bajo.plot(marker="o", color=["indigo", "deepskyblue"])
plt.title("Proporción de nivel bajo por Estrato y Zona")
plt.ylabel("% en nivel bajo")
plt.xlabel("Grupo de estrato")
plt.show()

#Grafico de barras agrupadas
tabla_comp_bajo.plot(kind="bar", color=["indigo", "deepskyblue"])
plt.title("Proporción de nivel bajo por Estrato y Zona")
plt.ylabel("% en nivel bajo")
plt.xticks(rotation=30)
plt.show()

###Posesión de bienes
cols_bienes = ["carro", "internet", "pc", "lavadora"]
df_p3[cols_bienes].isna().all(axis=1).sum() #estudiantes que no reportan nada
df_p3["indice_bienes"] = df_p3[cols_bienes].sum(axis=1, min_count=1)#no muestra filas NaN
df_p3["indice_bienes"].value_counts().sort_index()

tabla_bienes =pd.crosstab(df_p3["indice_bienes"], df_p3["es_bajo"], normalize="index")*100

#Graficar
tabla_bienes.plot(kind="bar", stacked=True, color=["thistle", "indigo"])

tabla_bienes.index = [
    "Sin bienes",
    "1 bien",
    "2 bienes",
    "3 bienes",
    "4 bienes"]

plt.ylabel("Porcentaje (%)")
plt.xlabel("Cantidad de bienes del hogar")
plt.title("Proporción de estudiantes en nivel bajo según bienes")
plt.legend(["No es bajo", "Es bajo"])
plt.show()

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

resumen_brechas.set_index("Dimensión").plot(kind="bar",color="indigo")

resumen_brechas = resumen_brechas.sort_values(by="Brecha (pp)",ascending=False)

plt.ylabel("Brecha en puntos porcentuales")
plt.title("Comparación de intensidad de desigualdad")
plt.xticks(rotation=0)
plt.show()