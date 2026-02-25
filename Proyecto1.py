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