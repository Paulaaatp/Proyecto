import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("datos_cauca.csv")
print(df.head())
print(df.shape)

df = df.dropna(subset=[
    "punt_ingles",
    "punt_matematicas",
    "punt_sociales_ciudadanas",
    "punt_c_naturales",
    "punt_lectura_critica"
])

df["punt_global"] = df["punt_global"].fillna(
    (df[
        ["punt_ingles",
         "punt_matematicas",
         "punt_sociales_ciudadanas",
         "punt_c_naturales",
         "punt_lectura_critica"]
     ].sum(axis=1) / 13) * 5
)

print(df.shape) 
print(df.head())
df.columns
df["punt_global"] = pd.to_numeric(df["punt_global"], errors="coerce")


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
########
