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

baseDataPath = ""
sourceData = []
dataFrames = []
dataFrameIndex = 0
xAxisKey = "casa"
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
    global xAxisKey

    changed_inputs = [
        x["prop_id"]
        for x in callback_context.triggered
    ]
    if "xaxis.options" in changed_inputs:
        raise PreventUpdate
    
    if search_value is None:
        raise PreventUpdate

    xAxisKey = None

    for o in options:
        if search_value == o["value"]:
            selectedKey = options[search_value]["label"]
            xAxisKey = selectedKey

    DF=dataFrames[dataFrameIndex]["data"]
    print(">>>UpdateXAxis: ", xAxisKey)
    return drawFigure(DF),

@app.callback(
        Output("graph", "children", allow_duplicate=True),
        Output("columns", "options", allow_duplicate=True),
        Input("columns", "value"),
        Input("columns", "options"),
        Input("xaxis", "value"), 
        prevent_initial_call=True,
    )
def updateColumns(columnsValues, columnsOptions, xAxisOptionIndex):
    global dataColumns
    
    if len(dataFrames) == 0:
        raise PreventUpdate

    changed_inputs = [
        x["prop_id"]
        for x in callback_context.triggered
    ]
    if "columns.options" in changed_inputs:
        raise PreventUpdate

    if columnsValues is None:
        raise PreventUpdate

    if not isinstance(columnsValues, list):
        columnsValues = [columnsValues]    

    DF = dataFrames[dataFrameIndex]["data"]
    DF_KEYS = DF.keys()
    columnsOptions = [{"label": DF_KEYS[x], "value":x} for x in range(len(DF_KEYS)) if DF_KEYS[x] != xAxisKey]
    if not columnsValues or columnsValues == []:
        dataColumns = [ DF_KEYS[x] for x in range(len(DF_KEYS)) if DF_KEYS[x] != xAxisKey ]
    else:
        dataColumns = [ option["label"] for option in columnsOptions if option["label"] != xAxisKey ]

    return [
        drawFigure(DF),
        columnsOptions,
    ]

def drawFigure(tableData):
    global xAxisKey
    global dataColumns

    if tableData is None:
      fig = go.Figure()
    else:
        fig=px.line(
            tableData, 
            x=xAxisKey,
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
        )

    figCount = 1
    if figCount > 1:
        return html.Div([
            dbc.Card(
                dbc.CardBody([
                    dcc.Graph(
                        figure = fig,
                        config={'displayModeBar': False},
                    ),
                    dcc.Graph(
                        figure = fig,
                        config={'displayModeBar': False},
                    ),
                ])
            ),  
        ])
    else:
        return html.Div([
            dbc.Card(
                dbc.CardBody([
                    dcc.Graph(
                        figure = fig,
                        config={
                            'displayModeBar': False
                        }
                    ),
                ])
            ),  
        ])


def drawTable(tableData):
    DrawingTable=True

    if tableData is None:
        return dash_table.DataTable(
            id='data-table',
            data=[],
            columns=[],)

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
    global xAxisKey
    global dataColumns

    DF = None
    DF_KEYS = []
    dataColumns = None
    xAxisKey = ""

    if len(dataFrames) > 0 :
        DF = dataFrames[dataFrameIndex]["data"]
        DF_KEYS = DF.keys()
        xAxisKey = DF_KEYS[0]
        dataColumns = [DF_KEYS[1]]

    return dbc.Container([
            dbc.Card(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Card(
                                dbc.CardBody([
                                    html.Label("Label1",id="label1"),
                                ])
                            ),
                        ], width=3),
                        dbc.Col([
                            dbc.Card(
                                dbc.CardBody([
                                    html.Label("Label2",id="label2"),
                                ])
                            ),
                        ], width=3),
                        dbc.Col([
                            dbc.Card(
                                dbc.CardBody([
                                    html.Label("Label3",id="label3"),
                                ])
                            ),
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
                        html.Div([
                            html.Label("Search path"),
                            html.Br(),
                            dcc.Input(
                                id="dataset-path",
                                type="text",
                                placeholder="Enter datasets path",
                                debounce = True,
                                size='60',
                            ), 
                            dcc.Input(
                                id="dataset-filename-filter",
                                type="text",
                                value="csv",
                                placeholder="Filename filter(separate;!negate)",
                                debounce = True,
                                size='30',
                            ),
                            dcc.Input(
                                id="dataset-dir-filter",
                                type="text",
                                placeholder="Folder filter(separate;!negate)",
                                debounce = True,
                                size='30',
                            ),
                        ]),
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
                                value=xAxisKey,
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
        Input("dataset-path", "value"),
        Input("dataset-filename-filter", "value"),
        Input("dataset-dir-filter", "value"),
        )
def update_dataset_list(datasetsPath, filenameFilterStr, folderFilterStr):
    global dataFrames

    if not datasetsPath:
        raise PreventUpdate

    filenameFilter = []
    if isinstance( filenameFilterStr, str):
        filenameFilter = filenameFilterStr.split(";")
    folderFilter = []
    if isinstance( folderFilterStr, str):
        folderFilter = folderFilterStr.split(";")

    dataFrames = []

    filtered_files = []

    excludesDir = [ f[1:] for f in folderFilter if len(f)>0 and f[0] == "!" ]
    excludesDir = excludesDir + [".venv", ".git"]
    includesDir = [ f for f in folderFilter if len(f)>0 and not f[0] == "!" ]
    excludes = [ f[1:] for f in filenameFilter if len(f)>0 and f[0] == "!" ]
    includes = [ f for f in filenameFilter if len(f)>0 and not f[0] == "!" ]

    for root, dirs, files in os.walk(datasetsPath):
        # exclude dirs
        dirs[:] = [d for d in dirs if not any(word in d for word in excludesDir)]
        if len(includesDir) > 0:
            dirs[:] = [d for d in dirs if any(word in d for word in includesDir)]
            if not any(word in root for word in includesDir):
                continue

        # exclude/include files
        files = [os.path.normpath(os.path.join(root, f)) for f in files]
        files = [f for f in files if not any(word in f for word in excludes)]
        if len(includes) > 0:
            files = [f for f in files if any(word in f for word in includes)]

        for fname in files:
            filtered_files.append(fname) 
            try:
                df = LoadData(fname)  
                dataFrames.append( { "path": fname, "data" : df} )
            except:
                print("ERROR: file not found: ", fname)
        
    if len(filtered_files) > 1:
        baseDataPath = os.path.commonpath(filtered_files)
        baseDataPath = os.path.dirname(baseDataPath)
        filtered_files = [f[len(baseDataPath)+1:] for f in filtered_files]
        for df in dataFrames:
            df["name"]=df["path"][len(baseDataPath)+1:]

    filtered_files = [{ "label": filtered_files[i], "value": i } for i in range(len(filtered_files))]
    return filtered_files

@app.callback(
    Output("graph", "children", allow_duplicate=True),
    Output("table-content", "children"),
    Output("xaxis", "options"),
    Output("xaxis", "value"),
    Output("columns", "options", allow_duplicate=True),
    Output("columns", "value"),
    Input('dataset-select', 'value'),
    Input('data-table', 'data'),
    Input('data-table', 'columns'),
    prevent_initial_call=True,
)
def UpdateTableSelectedDataset(datasetIndex, rows, columns):
    global xAxisKey
    global dataColumns

    if datasetIndex is None:
        raise PreventUpdate

    dataFrameIndex = datasetIndex
    DF = dataFrames[dataFrameIndex]["data"]

    changed_inputs = [
        x["prop_id"]
        for x in callback_context.triggered
    ]

    if "dataset-select.value" in changed_inputs:
        DF_KEYS = DF.keys()
        xAxisOptionsIndex = 0
        xAxisKey = DF_KEYS[xAxisOptionsIndex] if len(DF_KEYS) > 0 else ""
        xAxisOptions=[{"label": DF_KEYS[x], "value":x} for x in range(len(DF_KEYS))]
        dataColumns = [ key for key in DF_KEYS if key != xAxisKey]
        columnsOptions=[{"label": DF_KEYS[x], "value":x} for x in range(len(DF_KEYS)) if x != xAxisOptionsIndex]
        print("Updated dataset-select. XKey: ", xAxisKey)
        return [
            drawFigure(DF),
            drawTable(DF),
            xAxisOptions,
            xAxisOptionsIndex,
            columnsOptions,
            ["fps"],
        ]

    if "data-table.data" in changed_inputs or "data-table.columns" in changed_inputs:
        DF = pd.DataFrame(rows, columns=[c['name'] for c in columns])
        print("Updated data-table. XKey: ", xAxisKey)
        print(DF.head())
        return [
            drawFigure(DF),
            no_update,# drawTable(df),
            no_update,#xAxisOptions,
            no_update,#xaxisValue
            no_update,#columnsOptions,
            no_update,#columnsValue
        ]

#########################################################

if __name__ == '__main__':
    update_dataset_list("../data", "csv", "")
    app.layout = RefreshPage()

    # Run app and display result inline in the notebook
    app.run_server(debug=True)
