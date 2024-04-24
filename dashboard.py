import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go

import numpy as np
import pandas as pd
import json


# df = pd.read_csv("HIST_PAINEL_COVIDBR_13mai2021.csv", sep=';')
# df_states = df[(~df['estado'].isna()) & (df['codmun'].isna())]
# df_brasil = df[df['regiao'] == 'Brasil']
# df_states.to_csv('df_states.csv')
# df_brasil.to_csv('df_brasil.csv')

df_brasil = pd.read_csv('df_brasil.csv')
df_states = pd.read_csv('df_states.csv')

df_data = df_states[df_states['estado'] == 'RJ']

select_columns = {"casosAcumulados": "Casos Acumulados",
                  'casosNovos': 'Novos Casos',
                  'obitosAcumulado': 'Óbitos Totais',
                  'obitosNovos': 'óbitos por dia'}

# ----- Analisando o arquivo brazil_geo.json --------
brazil_states = json.load(open('geojson/brazil_geo.json', 'r'))

# type(brazil_states)
# brazil_states.keys()
# type(brazil_states['features'])
# brazil_states['features'][0].keys()
# brazil_states['features'][0]['id']

# ==================================
# Instanciação do Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
fig = px.choropleth_mapbox(df_states, locations='estado', color='casosNovos',
                           center={'lat': -16.95, 'lon': -47.78},
                           zoom=4,
                           geojson=brazil_states,
                           color_continuous_scale='Redor',
                           opacity=0.4,
                           hover_data={'casosAcumulado': True,
                                       'casosNovos': True,
                                       'obitosNovos': True,
                                       'estado': True}
                           )

fig.update_layout(
    paper_bgcolor='#242424',
    autosize=True,
    margin=go.layout.Margin(l=0, r=0, t=0, b=0),
    showlegend=False,
    mapbox_style='carto-darkmatter',

)

fig2 = go.Figure(layout={'template': 'plotly_dark'})
fig2.add_trace(go.Scatter(
    x=df_data['data'],
    y=df_data['casosAcumulado']
))

fig2.update_layout(
    paper_bgcolor='#242424',
    plot_bgcolor='#242424',
    autosize=True,
    margin=dict(l=10, r=10, t=10, b=10)
)

# ==================================
# Construção do Layout
app.layout = dbc.Container(
    dbc.Row([
            dbc.Col([
                    html.Div(
                        [
                            html.H5("Evolução COVID-19"),
                            dbc.Button('BRASIL', color='primary',
                                       id='location-button', size='lg'),
                        ],
                        style={}
                    ),
                    html.P("Informe a data na qual deseja obter informações",
                           style={"margin-top": '40px'}),
                    html.Div(id="div-test",
                             children=[
                                 dcc.DatePickerSingle(
                                     id='date-picker',
                                     min_date_allowed=df_brasil['data'].min(),
                                     max_date_allowed=df_brasil['data'].max(),
                                     initial_visible_month=df_brasil['data'].min(
                                     ),
                                     date=df_brasil['data'].max(),
                                     display_format="MMMM D, YYYY",
                                     style={'border': "0px solid black"})
                             ]
                             ),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.Span("Casos Recuperados"),
                                    html.H3(style={"color": "#adfc92"},
                                            id="casos-recuperados-text"),
                                    html.Span("Em Acompanhamento"),
                                    html.H5(id="em-acompanhamento-text")
                                ])
                            ], color='light', outline=True,
                                style={"margin-top": "10px",
                                       "box-shadow": "0 4px 4px 0 rgba(0,0,0,0.15), 0 4px 20px 0 rgba(0,0,0,0.19)",
                                       "color": "#FFFFFF"}),
                        ], md=4),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.Span("Casos Confirmados Totais"),
                                    html.H3(style={"color": "#389fd6"},
                                            id="casos-confirmados-text"),
                                    html.Span("Novos Casos na data"),
                                    html.H5(id="novos-casos-text")
                                ])
                            ], color='light', outline=True,
                                style={"margin-top": "10px",
                                       "box-shadow": "0 4px 4px 0 rgba(0,0,0,0.15), 0 4px 20px 0 rgba(0,0,0,0.19)",
                                       "color": "#FFFFFF"}),
                        ], md=4),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.Span("Óbitos Confirmados"),
                                    html.H3(
                                        style={"color": "#adfc92"}, id="obitos-text"),
                                    html.Span("Óbitos na data"),
                                    html.H5(id="obitos-data-text")
                                ])
                            ], color='light', outline=True,
                                style={"margin-top": "10px",
                                       "box-shadow": "0 4px 4px 0 rgba(0,0,0,0.15), 0 4px 20px 0 rgba(0,0,0,0.19)",
                                       "color": "#FFFFFF"}),
                        ], md=4)
                    ]),

                    html.Div([
                        html.P("Selecione o tipo de dado que deseja visualizar:", style={
                               "margin-top": '25px'}),
                        dcc.Dropdown(id='location-dropdown',
                                     options=[{"label": j, "value": i}
                                              for i, j in select_columns.items()],
                                     value="casosNovos",
                                     style={'margin-top': "10px"}
                                     ),
                        dcc.Graph(id='line-graph', figure=fig2)
                    ]),
                    ], md=5, style={'padding': "25px",
                                    'background-color': "#242424"}),

            dbc.Col([
                dcc.Loading(id='loading-1', type='default',
                    children=[
                        dcc.Graph(id='choropleth-map', figure=fig,
                                  style={'height': "100vh",
                                         'margin-right': '10px'})
                    ]),
            ], md=7),
            ]), fluid=True)

# ==========================================
# Interactivity

@app.callback(
        [
            Output('casos-recuperados-text', 'children'),
            Output('em-acompanhamento-text', 'children'),
            Output('casos-confirmados-text', 'children'),
            Output('novos-casos-text', 'children'),
            Output('obitos-text', 'children'),
            Output('obitos-data-text', 'children')
        ],

        [
            Input("date-picker",'date'),
            Input('location-button', 'children')
         ],
)
def display_status(date, location):
    if location =='BRASIL':
        df_data_on_date = df_brasil[df_brasil['data']==date]
    else:
        df_data_on_date = df_states[(df_states['estado']==location) & (df_states['data']==date)]

    recuperados_novos = '-' if df_data_on_date['Recuperadosnovos'].isna().values[0] else f"{int(df_data_on_date['Recuperadosnovos'].isna().values[0])}".replace(',','.')
    acompanhamento_novos = '-' if df_data_on_date['Recuperadosnovos'].isna().values[0] else f"{int(df_data_on_date['Recuperadosnovos'].isna().values[0])}".replace(',','.')
    casos_acumulados = '-' if df_data_on_date['casosAcumulado'].isna().values[0] else f"{int(df_data_on_date['casosAcumulado'].isna().values[0])}".replace(',','.')
    casos_novos = '-' if df_data_on_date['Recuperadosnovos'].isna().values[0] else f"{int(df_data_on_date['Recuperadosnovos'].isna().values[0])}".replace(',','.')
    obitos_acumulados = '-' if df_data_on_date['Recuperadosnovos'].isna().values[0] else f"{int(df_data_on_date['Recuperadosnovos'].isna().values[0])}".replace(',','.')
    obitos_novos = '-' if df_data_on_date['Recuperadosnovos'].isna().values[0] else f"{int(df_data_on_date['Recuperadosnovos'].isna().values[0])}".replace(',','.')
    
    return(
            recuperados_novos,
           acompanhamento_novos,
           casos_acumulados,
           casos_novos,
           obitos_acumulados,
           obitos_novos
        )

# -> para acessar uma imagem : html.Img(id="", src=app.get_asset_url("nome do arquivo na pasta assets")), dentro da div
if __name__ == '__main__':
    app.run_server(debug=True)
