from dash import Dash, dcc, html, callback, Input, Output
from dash import dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

app = Dash(external_stylesheets=[dbc.themes.SLATE])

sourceData = []
dataFrame = pd.DataFrame()

# table view
tableViewConfig = {
    'visibleRows' : 20
}

def drawFigure(tableData):
    return  html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=px.line(
                        tableData, 
                        x="seconds",
                        y="temperature",
                        # color="fps",
                        # text = "fps",
                        markers = True,
                        labels = {'sec.':'time', 'gpu' : 'GPU freq.' },
                        hover_data="gpu",
                    ).update_layout(
                        template='plotly_dark',
                        plot_bgcolor= 'rgba(0, 0, 0, 0)',
                        paper_bgcolor= 'rgba(0, 0, 0, 0)',
                        # hovermode="x unified",
                        hoverlabel=dict(
                            bgcolor="black",
                            font_size=14,
                            font_family="Rockwell"
                        ),
                    ).update_traces(
                        textposition="bottom right",
                        # hovertemplate = "Fps:%{fpsColumn}: <br>Temperature: %{y}",
                    ),
                    config={
                        'displayModeBar': False
                    }
                )
            ])
        ),  
    ])

def drawTable(tableData):
    return dash_table.DataTable(
            id='data-table',
            data=tableData.to_dict("records"),
            columns=[
                    { "name": i, "id": i, "deletable": True, "selectable": True }
                        for i in tableData.columns
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
            page_size= tableViewConfig["visibleRows"],
            export_columns='visible',
            export_format='csv',
            style_table={
                'minHeight': '70vh', 'height': '70vh', 'maxHeight': '70vh',
                'minWidth': '100%',
            },
            style_cell={
                'minWidth': '130px', 'width': '130px', 'maxWidth': '130px',
                'textAlign': 'left',
                'fontSize':12,
                'font-family': 'sans-serif',
                'padding': '5px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
            },
            style_data={
                'maxWidth': 0,
                'color': 'black',
                'backgroundColor': 'white',
                'border': '1px solid black'
                },
            style_header={
                'backgroundColor': '#90EE90',
                'color': 'black',
                'fontWeight': 'bold',
                'fontSize':14,
                'border': '1px solid black',
            },
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

def LoadData( filename ):
    return pd.read_csv(filename, delimiter=",", decimal=".")

def RefreshPage() : 
    for filename in sourceData:
        dataFrame = LoadData(filename)

    return dbc.Container([
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
                            drawFigure(dataFrame)
                        ], id='graph', width=12),
                    ], align='center'), 
                    html.Br(),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Num. rows", size="md", style={'display': 'inline-block', 'line-height':"0.1"}),
                            dcc.Input(
                                id="table-view-rows",
                                value=tableViewConfig["visibleRows"],
                                type="number",
                                style={'width': '5vw', 'height': '3vh'}
                            ),
                        ], width=1),
                    ]),
                    dbc.Row([
                        dbc.Col(
                            [
                                drawTable(dataFrame), 
                            ],id="table-view", width=12),
                    ], align='center'),      
                ]), color = 'dark'
            ),
        ], fluid=True)


@app.callback(
    Output("data-table", "page_size"),
    Input('table-view-rows', 'value'),
)
def UpdateTableLayout(numRows):
    return numRows

@callback(
    Output('graph', 'children'),
    Input('data-table', 'data'),
    Input('data-table', 'columns'),
)
def UpdateDataframeFromTable(rows, columns):
    dataFrame = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    return drawFigure(dataFrame)


#########################################################

if __name__ == '__main__':
    sourceData.append("samples.csv")

    app.layout = RefreshPage()

    # Run app and display result inline in the notebook
    app.run_server(debug=True)
