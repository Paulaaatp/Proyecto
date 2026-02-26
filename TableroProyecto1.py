import dash
from dash import dcc  # dash core components
from dash import html # dash html components
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output

from Proyecto1 import (cargar_y_preparar,generar_imagenesp1,generar_imagenesp2,generar_imagenesp3)

#Cargar datos limpios
df, df_p3, desigualdad, orden_educativo = cargar_y_preparar()

#Generar imagenes 
img_p1_1, img_p1_2 = generar_imagenesp1(df, desigualdad)
img_p2_1, img_p2_2, img_p2_3, img_p2_4 = generar_imagenesp2(df, orden_educativo)
img_p3_1, img_p3_2, img_p3_3 = generar_imagenesp3(df_p3)

app= dash.Dash(__name__)
server= app.server

app.layout = html.Div(
    style = {"fontFamily": "Arial", "padding": "20px"},
    children=[
        html.Img(src="/assets/logo_andes.png", style={"height": "80px"}),
        html.Img(src="/assets/logo_cauca.png", style={"height": "80px"}),
        html.H1("Análisis de la desigualdad educativa en Cauca", style={'textAlign': 'center'}),
        html.Div(children= '''Este tablero presenta un análisis de la desigualdad educativa en el departamento del Cauca,
                  Colombia. Se han utilizado datos de la pruebas Saber 11 para explorar las diferencias en 
                 el acceso a la educación según diferentes variables socioeconómicas y geográficas.''', style={'textAlign': 'center'}),
        
        html.H2("Brechas internas en el desempeño académico por ciudad en el Cauca", style={'marginTop': '40px'}),
        html.Img(src=img_p1_1, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "400px"}),
        html.Img(src=img_p1_2, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "400px"}),
        
        html.H2("Impacto individual y conjunto del nivel educativo parental en el desempeño académico", style={'marginTop': '40px'}),
        html.Img(src=img_p2_1, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "1000px"}),
        html.Img(src=img_p2_2, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "1000px"}),
        html.Img(src=img_p2_3, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "800px"}),
        html.Img(src=img_p2_4, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "800px"}),

        html.H2("Concentración del bajo desempeño académico según estrato, zona y bienes del hogar", style={'marginTop': '40px'}),
        html.Img(src=img_p3_1, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "400px"}),
        html.Img(src=img_p3_2, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "400px"}),
        html.Img(src=img_p3_3, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "400px"}),
    ])

if __name__ == "__main__":
    app.run(debug=True)