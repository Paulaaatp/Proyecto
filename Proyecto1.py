import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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

############   PREGUNTA 2 - EDUCACIÓN PADRES
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

# GRÁFICO DE BARRAS COMBINADO
niveles_comunes = sorted(
    list(
        set(df_padre["fami_educacionpadre"])
        .intersection(set(df_madre["fami_educacionmadre"]))))

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