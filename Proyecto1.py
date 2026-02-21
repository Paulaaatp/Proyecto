import pandas as pd
import matplotlib.pyplot as plt

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

########
