import pandas as pd

df = pd.read_csv("datos_cauca.csv")

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