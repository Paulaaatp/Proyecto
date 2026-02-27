import dash
from dash import dcc
from dash import html 
import pandas as pd

from Proyecto1 import (cargar_y_preparar,pregunta1,pregunta2,pregunta3)

#Cargar datos limpios
df, df_p3, desigualdad, orden_educativo = cargar_y_preparar()

#Generar graficas y tablas
fig_p1_1, fig_p1_2, tabla_modelos = pregunta1(df, desigualdad)
tabla_p2_padre, tabla_p2_madre, fig_p2_3, fig_p2_4 = pregunta2(df, orden_educativo)
fig_p3_1, fig_p3_2, fig_p3_3 = pregunta3(df_p3)

app= dash.Dash(__name__)
server= app.server

#Header con logos  
header = html.Div(
    style = {"fontFamily": "Arial", "padding": "20px"},
    children=[
        #Logos - como assets
        html.Img(src="/assets/logo_andes.png", style={"height": "80px"}),
        html.Img(src="/assets/logo_cauca.png", style={"height": "80px"})])

#Tab0 - Portada
tab_portada = html.Div(#abre1
    style = {"fontFamily": "Arial", "padding": "20px"},
    children=[#abre2
        #Título y descripción
        html.H1("Análisis sobre la desigualdad educativa en Cauca", style={'textAlign': 'center', "color" :"#1A3980"}),
        
        html.Div(#abre2
            style={
                "display": "flex",
                "gap": "30px",
                "alignItems": "center",
                "justifyContent": "center",
                "marginTop": "20px",
            },
            children=[#abre3
                html.Div(
                    style={"maxWidth": "650px", "textAlign": "justify"},
                    children=[
                        html.P(
                            "Se realizó un análisis de la desigualdad educativa en el departamento del Cauca "
                            "a partir de los resultados de las Pruebas Saber 11, con el propósito de identificar " 
                            "las diferencias en el acceso a la educación según diferentes variables socioeconómicas y geográficas.",
                            style={"textAlign": "justify"}),
                        html.Br(),
                        html.Br(),
                        "Con base en este "
                        "análisis, se diseñó una herramienta de analítica orientada a apoyar a la Secretaría de Educación "
                        "del Cauca en la toma de decisiones informadas y en la implementación de estrategias focalizadas "
                        "para reducir la desigualdad educativa en el departamento"],),

                html.Img(
                    src="/assets/foto_icfes.png",
                    style={
                        "width": "300px",
                        "borderRadius": "12px",
                        "boxShadow": "0px 4px 10px rgba(0,0,0,0.2)"}),
            ],#cierra3
        ),#cierra2
    
        html.H3("Preguntas de negocio a investigar", style={"marginTop": "40px","color" :"#1A3980"}),
        html.Ul(children=[
            html.Li("¿Cuáles ciudades del departamento presentan mayores niveles de desigualdad interna en los resultados" 
                    "académicos de las Pruebas Saber 11?"),
            html.Li("¿Cómo varía el desempeño académico de los estudiantes según el nivel educativo del padre en comparación"
                     " con el nivel educativo de la madre?"),
            html.Li("¿Qué combinación de características sociodemográficas "
                    " presenta la mayor concentración de estudiantes en el nivel bajo de desempeño?")])
    ])

#Tab 1 - Pregunta 1
tab_p1 = html.Div(
    style = {"fontFamily": "Arial", "padding": "20px"},
    children=[
        html.H2("Brechas internas en el desempeño académico por ciudad en el Cauca", style={'marginTop': '40px'}),
        
        dcc.Graph(figure=fig_p1_1, style={'width': '100%', 'height': '700px', 'marginBottom': '100px', "maxWidth": "800px"}),
        dcc.Graph(figure=fig_p1_2, style={'width': '100%', 'height': '600px', 'marginBottom': '100px', "maxWidth": "600px"}),
        
        html.H3("Factores asociados al coeficiente de variación", style={'textAlign': 'center', 'marginTop': '30px'}),
        tabla_modelos])

#Tab 2 - Pregunta 2
tab_p2 = html.Div(
    style = {"fontFamily": "Arial", "padding": "20px"},
    children=[
        html.H2("Impacto individual y conjunto del nivel educativo parental en el desempeño académico", style={'marginTop': '40px'}),
        
        html.H4("Nivel educativo del padre", style={'textAlign': 'center'}),
        tabla_p2_padre,
        
        html.H4("Nivel educativo de la madre", style={'textAlign': 'center', 'marginTop': '30px'}),
        tabla_p2_madre,
        
        dcc.Graph(figure=fig_p2_3, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "800px"}),
        dcc.Graph(figure=fig_p2_4, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "800px"})])
        
#Pregunta 3
tab_p3 = html.Div(
    style = {"fontFamily": "Arial", "padding": "20px"},
    children=[
        html.H2("Concentración del bajo desempeño académico según estrato, zona y bienes del hogar", style={'marginTop': '40px'}),
        
        dcc.Graph(figure=fig_p3_1, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "400px"}),
        dcc.Graph(figure=fig_p3_2, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "400px"}),
        dcc.Graph(figure=fig_p3_3, style={'width': '100%', 'height': 'auto', 'marginBottom': '20px', "maxWidth": "400px"})])

app.layout = html.Div(
    children=[
        header,

        dcc.Tabs(
            value="tab-portada",
            children=[
                dcc.Tab(label="Portada", value="tab-portada", children=tab_portada),
                dcc.Tab(label="Pregunta 1", value="tab-p1", children=tab_p1),
                dcc.Tab(label="Pregunta 2", value="tab-p2", children=tab_p2),
                dcc.Tab(label="Pregunta 3", value="tab-p3", children=tab_p3)])])

if __name__ == "__main__":
    app.run(debug=True)