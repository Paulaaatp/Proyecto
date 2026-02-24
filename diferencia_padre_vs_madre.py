import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ruta = "C:/Users/paula/OneDrive/Desktop/Andes/8 semestre/Analitica/Proyectos/Proyecto 1 - ICFES/datos_cauca.csv"
df = pd.read_csv(ruta)
# ======================================================
# LIMPIEZA DE DATOS
categorias_excluir = ["No Aplica", "No sabe", "Ninguno"]

df_clean = df[
    (~df["fami_educacionpadre"].isin(categorias_excluir)) &
    (~df["fami_educacionmadre"].isin(categorias_excluir)) &
    (df["punt_global"].notna())].copy()


# ======================================================
# PROMEDIO SEGÚN EDUCACIÓN DEL PADRE
df_padre = (
    df_clean
    .groupby("fami_educacionpadre")["punt_global"]
    .agg(["count", "mean"])
    .reset_index()
    .rename(columns={
        "count": "n_estudiantes",
        "mean": "promedio_punt_global"
    }).sort_values("promedio_punt_global"))

df_padre["promedio_punt_global"] = df_padre["promedio_punt_global"].round(2)

# ======================================================
# PROMEDIO SEGÚN EDUCACIÓN DE LA MADRE
df_madre = (
    df_clean
    .groupby("fami_educacionmadre")["punt_global"]
    .agg(["count", "mean"])
    .reset_index()
    .rename(columns={
        "count": "n_estudiantes",
        "mean": "promedio_punt_global"
    }).sort_values("promedio_punt_global"))

df_madre["promedio_punt_global"] = df_madre["promedio_punt_global"].round(2)
# ======================================================
# PENDIENTE DE CRECIMIENTO (BRECHA ENTRE EXTREMOS)
brecha_padre = df_padre["promedio_punt_global"].max() - df_padre["promedio_punt_global"].min()
brecha_madre = df_madre["promedio_punt_global"].max() - df_madre["promedio_punt_global"].min()

df_brechas = pd.DataFrame({
    "Variable": ["Educación Padre", "Educación Madre"],
    "Brecha_promedio": [round(brecha_padre, 2), round(brecha_madre, 2)]})

# ======================================================
# MATRIZ CRUZADA PADRE × MADRE (PROMEDIO)
df_matriz = (
    df_clean
    .pivot_table(
        values="punt_global",
        index="fami_educacionpadre",
        columns="fami_educacionmadre",
        aggfunc="mean").round(2))

# ======================================================
# HEATMAP PADRE × MADRE
# ======================================================

plt.figure(figsize=(10,8))

plt.imshow(df_matriz, aspect='auto')

plt.colorbar(label="Puntaje Global Promedio")

plt.xticks(
    np.arange(len(df_matriz.columns)),
    df_matriz.columns,
    rotation=45,
    ha='right'
)

plt.yticks(
    np.arange(len(df_matriz.index)),
    df_matriz.index
)

plt.title("Puntaje promedio según combinación educativa Padre × Madre")

plt.tight_layout()
plt.show()

# matriz de conteo
df_matriz_conteo = (
    df_clean
    .pivot_table(
        values="punt_global",
        index="fami_educacionpadre",
        columns="fami_educacionmadre",
        aggfunc="count"))


# ======================================================
# EXPORTAR A EXCEL (CON VARIAS HOJAS)

with pd.ExcelWriter("C:/Users/paula/OneDrive/Desktop/Andes/8 semestre/Analitica/Proyectos/Proyecto 1 - ICFES/analisis_educacion_padres.xlsx", engine="openpyxl") as writer:
    df_padre.to_excel(writer, sheet_name="Promedio_Padre", index=False)
    df_madre.to_excel(writer, sheet_name="Promedio_Madre", index=False)
    df_brechas.to_excel(writer, sheet_name="Brechas", index=False)
    df_matriz.to_excel(writer, sheet_name="Matriz_Promedios")
    df_matriz_conteo.to_excel(writer, sheet_name="Matriz_Conteo")

print("Archivo Excel generado: analisis_educacion_padres.xlsx")

# ======================================================
# GRÁFICO DE BARRAS COMBINADO (PADRE vs MADRE)
# ======================================================

# Unificamos categorías que existan en ambos
niveles_comunes = sorted(
    list(
        set(df_padre["fami_educacionpadre"])
        .intersection(set(df_madre["fami_educacionmadre"]))))

# Filtrar en el mismo orden
padre_plot = df_padre[
    df_padre["fami_educacionpadre"].isin(niveles_comunes)
].set_index("fami_educacionpadre").loc[niveles_comunes]

madre_plot = df_madre[
    df_madre["fami_educacionmadre"].isin(niveles_comunes)
].set_index("fami_educacionmadre").loc[niveles_comunes]

x = np.arange(len(niveles_comunes))
width = 0.35

plt.figure(figsize=(14,6))

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