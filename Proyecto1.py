import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

df = pd.read_csv("datos_cauca.csv")
df_original = df.copy()
df.columns = df.columns.str.lower().str.strip()

# Eliminar faltantes y duplicados
df = df.drop_duplicates()
df = df.dropna(subset=[
    "punt_ingles",
    "punt_matematicas",
    "punt_sociales_ciudadanas",
    "punt_c_naturales",
    "punt_lectura_critica"
])

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

print(desigualdad[desigualdad["cantidad"] == 1])

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

df_educ = df[
    (~df["fami_educacionpadre"].isin(categorias_excluir)) &
    (~df["fami_educacionmadre"].isin(categorias_excluir))].copy()

# PROMEDIO SEGÚN EDUCACIÓN PADRE
df_padre = (
    df_educ
    .groupby("fami_educacionpadre")["punt_global"]
    .agg(["count", "mean"])
    .reset_index()
    .rename(columns={
        "count": "n_estudiantes",
        "mean": "promedio_punt_global"
    }).sort_values("promedio_punt_global"))

df_padre["promedio_punt_global"] = df_padre["promedio_punt_global"].round(2)

print("\nPromedio según educación del padre")
print(df_padre)

# PROMEDIO SEGÚN EDUCACIÓN MADRE
df_madre = (
    df_educ
    .groupby("fami_educacionmadre")["punt_global"]
    .agg(["count", "mean"])
    .reset_index()
    .rename(columns={
        "count": "n_estudiantes",
        "mean": "promedio_punt_global"
    }).sort_values("promedio_punt_global"))

df_madre["promedio_punt_global"] = df_madre["promedio_punt_global"].round(2)

print("\nPromedio según educación de la madre")
print(df_madre)

# BRECHA ENTRE EXTREMOS
brecha_padre = df_padre["promedio_punt_global"].max() - df_padre["promedio_punt_global"].min()
brecha_madre = df_madre["promedio_punt_global"].max() - df_madre["promedio_punt_global"].min()

print("\nBrecha educación padre:", round(brecha_padre,2))
print("Brecha educación madre:", round(brecha_madre,2))

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

# GRÁFICO DE BARRAS COMBINADO
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
df_matriz = (
    df_educ
    .pivot_table(
        values="punt_global",
        index="fami_educacionpadre",
        columns="fami_educacionmadre",
        aggfunc="mean").round(2))

print("\nMatriz Padre x Madre (Promedios)")
print(df_matriz)
# HEATMAP PADRE × MADRE
plt.figure(figsize=(10,8))
plt.imshow(df_matriz, aspect='auto')
plt.colorbar(label="Puntaje Global Promedio")
plt.xticks(
    np.arange(len(df_matriz.columns)),
    df_matriz.columns,
    rotation=45,
    ha='right')
plt.yticks(
    np.arange(len(df_matriz.index)),
    df_matriz.index)
plt.title("Puntaje promedio según combinación educativa Padre × Madre")

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
df_p3["estrato"] = df_p3["estrato"].map({"Estrato 1":1,
                                         "Estrato 2":2,
                                         "Estrato 3":3,
                                         "Estrato 4":4,
                                         "Estrato 5":5,
                                         "Estrato 6":6})

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
#print(df_p3.head().to_string(index=False)) #imprimir sin el índice 

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

plt.figure()
plt.bar(resumen_estrato_grupo.index, resumen_estrato_grupo["Porcentaje"])
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
plt.bar(tabla_grupo.index, tabla_grupo["pct_bajo"])
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
plt.bar(tabla_stack.index, tabla_stack["No bajo"], label="No bajo")
plt.bar(tabla_stack.index, tabla_stack["Bajo"], bottom=tabla_stack["No bajo"], label="Bajo")
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
plt.bar(tabla_stack_zona.index, 
        tabla_stack_zona["No bajo"], 
        label="No bajo")
plt.bar(tabla_stack_zona.index, 
        tabla_stack_zona["Bajo"], 
        bottom=tabla_stack_zona["No bajo"], 
        label="Bajo")
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
tabla_comp_bajo.plot(marker="o")
plt.title("Proporción de nivel bajo por Estrato y Zona")
plt.ylabel("% en nivel bajo")
plt.xlabel("Grupo de estrato")
plt.show()

#Grafico de barras agrupadas
tabla_comp_bajo.plot(kind="bar")
plt.title("Proporción de nivel bajo por Estrato y Zona")
plt.ylabel("% en nivel bajo")
plt.xticks(rotation=30)
plt.show()

##Posesión de bienes
cols_bienes = ["carro", "internet", "pc", "lavadora"]
df_p3["indice_bienes"].value_counts()

pd.crosstab(df_p3["indice_bienes"], df["nivel_global"], normalize="index")
df.groupby("indice_bienes")["punt_global"].mean()
df["categoria_bienes"] = pd.cut(
    df_p3["indice_bienes"],
    bins=[-1,1,3,4],
    labels=["Bajo acceso", "Medio acceso", "Alto acceso"]
)
df_p3["categoria_bienes"] = pd.cut(
    df_p3["indice_bienes"],
    bins=[-1,1,3,4],
    labels=["Bajo acceso", "Medio acceso", "Alto acceso"]
)
pd.crosstab(df_p3["categoria_bienes"], df["nivel_global"], normalize="index")
