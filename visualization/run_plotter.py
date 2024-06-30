from dash.exceptions import PreventUpdate
from dash import Dash, dcc, html, callback, Input, Output
from dash import callback_context, no_update
from dash import dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import glob
import os

app = Dash(external_stylesheets=[dbc.themes.SLATE], prevent_initial_callbacks="initial_duplicate")

sourceData = []
dataFrames = []
dataFrameIndex = 0
xAxis = "casa"
dataColumns = ["noono"]
texts = ["one", "two", "three", "four"]


# table view
tableViewConfig = {
    'visibleRows' : 25
}

@app.callback(
        Output("graph", "children", allow_duplicate=True),
        Input("xaxis", "value"), 
        Input("xaxis", "options"),
        prevent_initial_call=True,
       )          
def updateXAxis(search_value, options):
    global xAxis
    
    if not search_value:
        raise PreventUpdate

    print("updateXAxis search_value: ", search_value)
    print("updateXAxis options: ", options)

    for o in options:
        if search_value == o["value"]:
            selectedKey = options[search_value]["label"]
            xAxis = selectedKey
            texts[0] = selectedKey

    return drawFigure(dataFrames[dataFrameIndex])

@app.callback(
        Output("graph", "children", allow_duplicate=True),
        Input("columns", "value"),
        Input("columns", "options"),
        prevent_initial_call=True,
    )
def updateColumns(search_value, options):
    global dataColumns
    
    if not search_value:
        raise PreventUpdate

    print("updateColumns search_value: ", search_value)
    print("updateColumns options: ", options)

    if not isinstance(search_value, list):
        search_value = [search_value]    

    dataKeys = dataFrames[dataFrameIndex].keys()
    dataColumns = []
    for key in search_value:
        dataColumns.append(dataKeys[key])

    return drawFigure(dataFrames[dataFrameIndex])

def drawFigure(tableData):
    global xAxis
    global dataColumns

    print("drawFigure X: ", xAxis)
    print("drawFigure columns: ", dataColumns)

    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=px.line(
                        tableData, 
                        x=xAxis,
                        y=dataColumns,
                        # color="fps",
                        # text = "fps",
                        markers = True,
                        # labels = {'seconds':'time', 'gpu' : 'GPU freq.' },
                        # hover_data="gpu",
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
    DrawingTable=True
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
            fixed_rows={'headers': True},
            virtualization=True,
            page_action="none",
            page_current= 0,
            page_size=tableViewConfig["visibleRows"],
            export_columns='visible',
            export_format='csv',
            style_table={
                'minHeight': '70vh',
                'maxHeight': '80%',
                'height': '100%', 
                'minWidth': '100%',
                'overflowY': 'auto',
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

# Text field
def drawText(index):
    global texts
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
    global xAxis
    global dataColumns

    DF = dataFrames[dataFrameIndex]
    DF_KEYS = DF.keys() 
    xAxis = DF_KEYS[0]
    dataColumns = [DF_KEYS[1]]
    print("RefreshPage X: ", xAxis)
    print("RefreshPage columns: ", dataColumns)

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
                            drawFigure(DF)
                        ], id='graph', width=12),
                    ], align='center'), 
                    html.Br(),
                    dbc.Row([
                        dbc.Col([
                            dcc.Input(
                                id="dataset-path",
                                type="text",
                                placeholder="Enter datasets path",
                            ),
                        ], width=3),
                        dbc.Col([
                            dcc.Input(
                                id="dataset-filter",
                                type="text",
                                placeholder="Enter datasets filter(; to separate allowed substrings ! to negate)",
                            ),
                        ], width=2),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Dropdown(
                                id='dataset-select',
                                options=[{'label': sourceData[i], 'value': i} for i in range(len(sourceData))],
                                value=dataFrameIndex
                            ),
                        ], width=4),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dcc.Dropdown(
                                id="xaxis",
                                placeholder="Select X axis",
                                options=[{"label": DF_KEYS[x], "value":x} for x in range(len(DF_KEYS))],
                                value=xAxis,
                            ),
                        ]),
                        dbc.Col([
                            dcc.Dropdown(
                                id="columns",
                                placeholder="Select columns",
                                options=[{"label": DF_KEYS[x], "value":x} for x in range(len(DF_KEYS))],
                                value=dataColumns,
                                multi=True,
                            ),
                        ])
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Row([ drawTable(DF)], id='table-content'),
                                dbc.Alert(id='tbl_out'),
                            ],id="table-view", width=12),
                    ], align='center'),      
                ]), color = 'dark'
            ),
        ], fluid=True)

@app.callback(
        Output("dataset-select", "options"), 
        Input("dataset-path", "value"))
def list_datasets(datasetsPath):
    global dataFrames
    
    dataFrames = []

    file_names = os.listdir(datasetsPath)
    file_list = []

    count = 0
    for file in file_names:
        if "csv" in file:
            dataFrames.append( LoadData(filename) )
            file_list.append({'label': sourceData[count], 'value': count} ),
            count = count + 1

    return file_list

@app.callback(
    Output("graph", "children", allow_duplicate=True),
    Output("table-content", "children"),
    Input('dataset-select', 'value'),
    Input('data-table', 'data'),
    Input('data-table', 'columns'),
    prevent_initial_call=True,
)
def UpdateTableSelectedDataset(datasetIndex, rows, columns):
    changed_inputs = [
        x["prop_id"]
        for x in callback_context.triggered
    ]

    if "dataset-select.value" in changed_inputs:
        dataFrameIndex = datasetIndex
        df = dataFrames[dataFrameIndex]
        return [
            drawFigure(df),
            drawTable(df)
        ]

    if "data-table.data" in changed_inputs or "data-table.columns" in changed_inputs:
        dataFrames[datasetIndex] = pd.DataFrame(rows, columns=[c['name'] for c in columns])
        df = dataFrames[datasetIndex]
        return [
            drawFigure(df),
            no_update
        ]

#########################################################

if __name__ == '__main__':
    sourceData = [f for f in glob.glob("*.csv")]
    
    for filename in sourceData:
        dataFrames.append( LoadData(filename) )

    app.layout = RefreshPage()

    # Run app and display result inline in the notebook
    app.run_server(debug=True)
