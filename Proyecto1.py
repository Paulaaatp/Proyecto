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