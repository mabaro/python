from dash import Dash, dcc, html
from dash import dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def drawFigure(tableData):
    return  html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=px.line(
                        df, 
                        x="seconds",
                        y="temperature",
                        color="fps",
                        text = "fps",
                        markers = True,
                    ).update_layout(
                        template='plotly_dark',
                        plot_bgcolor= 'rgba(0, 0, 0, 0)',
                        paper_bgcolor= 'rgba(0, 0, 0, 0)',
                    ).update_traces(textposition="bottom right"),
                    config={
                        'displayModeBar': False
                    }
                )
            ])
        ),  
    ])

def drawTable(index):
    return dash_table.DataTable(
            id='data-table',
            data=df.to_dict("records"),
            columns=[
                    { "name": i, "id": i, "deletable": True, "selectable": True }
                        for i in df.columns
                ],
            editable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            column_selectable="single",
            row_selectable="multi",
            row_deletable=True,
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current= 0,
            page_size= 10,
    )

texts = ["one", "two", "three", "four"]
# Text field
def drawText(index):
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                texts[index]
            ])
        ),
    ])

# Data
df = pd.read_csv("samples.csv")

# Build App
app = Dash(external_stylesheets=[dbc.themes.SLATE])

app.layout = dbc.Container([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    drawText(0)
                ], width=3),
                dbc.Col([
                    drawText(1)
                ], width=3),
                dbc.Col([
                    drawText(2)
                ], width=6),
            ], align='center'), 
            html.Br(),
            dbc.Row([
                dbc.Col([
                    drawFigure(1)
                ], width=12),
            ], align='center'), 
            html.Br(),
            dbc.Row([
                dbc.Col([
                   drawTable(0), 
                ], width=12),
            ], align='center'),      
        ]), color = 'dark'
    ),
], fluid=True)

# Run app and display result inline in the notebook
app.run_server(debug=True)
