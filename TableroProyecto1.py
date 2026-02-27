import dash
from dash import dcc
from dash import html 
import pandas as pd

from Proyecto1 import (cargar_y_preparar,pregunta1,pregunta2,pregunta3)

#Cargar datos limpios
df, df_p3, desigualdad, orden_educativo = cargar_y_preparar()

#Generar graficas 
fig_p1_1, fig_p1_2, tabla_modelos = pregunta1(df, desigualdad)
tabla_p2_padre, tabla_p2_madre, fig_p2_3, fig_p2_4 = pregunta2(df, orden_educativo)
fig_p3_1, fig_p3_2, fig_p3_3 = pregunta3(df_p3)

app= dash.Dash(__name__)
server= app.server

app.layout = html.Div(
    style = {"fontFamily": "Arial", "padding": "20px"},
    children=[
        #Logos - como assets
        html.Img(src="/assets/logo_andes.png", style={"height": "80px"}),
        html.Img(src="/assets/logo_cauca.png", style={"height": "80px"}),

        #Título y descripción
        html.H1("Análisis de la desigualdad educativa en Cauca", style={'textAlign': 'center'}),
        html.Div(children= '''Este tablero presenta un análisis de la desigualdad educativa en el departamento del Cauca,
                  Colombia. Se han utilizado datos de la pruebas Saber 11 para explorar las diferencias en 
                 el acceso a la educación según diferentes variables socioeconómicas y geográficas.''', style={'textAlign': 'center'}),
        
        #Pregunta 1
        html.H2("Brechas internas en el desempeño académico por ciudad en el Cauca", style={'marginTop': '40px'}),
        
        dcc.Graph(figure=fig_p1_1, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "400px"}),
        dcc.Graph(figure=fig_p1_2, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "400px"}),
        
        html.H3("Factores asociados al coeficiente de variación", style={'textAlign': 'center', 'marginTop': '30px'}),
        tabla_modelos,
                
        #Pregunta 2
        html.H2("Impacto individual y conjunto del nivel educativo parental en el desempeño académico", style={'marginTop': '40px'}),
        
        html.H4("Nivel educativo del padre", style={'textAlign': 'center'}),
        tabla_p2_padre,
        
        html.H4("Nivel educativo de la madre", style={'textAlign': 'center', 'marginTop': '30px'}),
        tabla_p2_madre,
        
        dcc.Graph(figure=fig_p2_3, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "800px"}),
        dcc.Graph(figure=fig_p2_4, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "800px"}),
        
        #Pregunta 3
        html.H2("Concentración del bajo desempeño académico según estrato, zona y bienes del hogar", style={'marginTop': '40px'}),
        
        dcc.Graph(figure=fig_p3_1, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "400px"}),
        dcc.Graph(figure=fig_p3_2, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "400px"}),
        dcc.Graph(figure=fig_p3_3, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "400px"}),
    ])

if __name__ == "__main__":
    app.run(debug=True)