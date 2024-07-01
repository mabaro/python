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

    changed_inputs = [
        x["prop_id"]
        for x in callback_context.triggered
    ]
    if "xaxis.options" in changed_inputs:
        raise PreventUpdate
    
    if search_value is None:
        raise PreventUpdate

    xAxis = None

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
    
    changed_inputs = [
        x["prop_id"]
        for x in callback_context.triggered
    ]
    if "columns.options" in changed_inputs:
        raise PreventUpdate

    if search_value is None:
        raise PreventUpdate

    if not isinstance(search_value, list):
        search_value = [search_value]    

    dataKeys = dataFrames[dataFrameIndex].keys()
    dataColumns = [dataKeys[key] for key in (search_value or [])]

    if len(dataColumns) == 0:
        dataColumns = [k for k in dataKeys if k != xAxis ]

    return drawFigure(dataFrames[dataFrameIndex])

def drawFigure(tableData):
    global xAxis
    global dataColumns

    if tableData is None:
      fig = go.Figure()
    else:    
        fig=px.line(
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
        )

    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure = fig,
                    config={
                        'displayModeBar': False
                    }
                )
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
    global xAxis
    global dataColumns

    DF = None
    DF_KEYS = []
    dataColumns = None
    xAxis = ""

    if len(dataFrames) > 0 :
        DF = dataFrames[dataFrameIndex]
        DF_KEYS = DF.keys()
        xAxis = DF_KEYS[0]
        dataColumns = [DF_KEYS[1]]

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
                                debounce = True,
                            ),
                        ], width=3),
                        dbc.Col([
                            dcc.Input(
                                id="dataset-filename-filter",
                                type="text",
                                placeholder="Enter filename filter(; to separate allowed substrings ! to negate)",
                                debounce = True,
                            ),
                        ], width=2),
                        dbc.Col([
                            dcc.Input(
                                id="dataset-dir-filter",
                                type="text",
                                placeholder="Enter folder filter(; to separate allowed substrings ! to negate)",
                                debounce = True,
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

    excludeDirs = [".venv"]
    excludesDir = [ f[1:] for f in folderFilter if len(f)>0 and f[0] == "!" ]
    includesDir = [ f for f in folderFilter if len(f)>0 and not f[0] == "!" ]
    excludes = [ f[1:] for f in filenameFilter if len(f)>0 and f[0] == "!" ]
    includes = [ f for f in filenameFilter if len(f)>0 and not f[0] == "!" ]

    for root, dirs, files in os.walk(datasetsPath):
        # exclude dirs
        dirs[:] = [os.path.join(root, d) for d in dirs]
        dirs[:] = [d for d in dirs if not any(word in d for word in excludesDir)]
        if len(includesDir) > 0:
            dirs[:] = [d for d in dirs if any(word in d for word in includesDir)]
            if not any(word in root for word in includesDir):
                continue

        # exclude/include files
        files = [os.path.join(root, f) for f in files]
        files = [f for f in files if not any(word in f for word in excludes)]
        if len(excludes) > 0:
            files = [f for f in files if not any(word in f for word in excludes)]
        if len(includes) > 0:
            files = [f for f in files if any(word in f for word in includes)]

        for fname in files:
            filtered_files.append(fname) 
            dataFrames.append( LoadData(fname) )


    baseDataPath = os.path.commonpath(filtered_files)
    baseDataPath = os.path.dirname(baseDataPath)
    filtered_files = [f.removeprefix(baseDataPath) for f in filtered_files]

    filtered_files = [{ "label": filtered_files[i], "value": i } for i in range(len(filtered_files))]
    return filtered_files

@app.callback(
    Output("graph", "children", allow_duplicate=True),
    Output("table-content", "children"),
    Output("xaxis", "options"),
    Output("columns", "options"),
    Input('dataset-select', 'value'),
    Input('data-table', 'data'),
    Input('data-table', 'columns'),
    prevent_initial_call=True,
)
def UpdateTableSelectedDataset(datasetIndex, rows, columns):
    global xAxis
    global dataColumns

    changed_inputs = [
        x["prop_id"]
        for x in callback_context.triggered
    ]

    if "dataset-select.value" in changed_inputs:
        if datasetIndex is None:
            raise PreventUpdate

        dataFrameIndex = datasetIndex
        df = dataFrames[dataFrameIndex]
        DF_KEYS = df.keys()
        xAxis = DF_KEYS[0] if len(DF_KEYS) > 0 else ""
        xAxisOptions=[{"label": DF_KEYS[x], "value":x} for x in range(len(DF_KEYS))]
        dataColumns = [ key for key in DF_KEYS if key != xAxis]
        columnsOptions=[{"label": DF_KEYS[x], "value":x} for x in range(len(DF_KEYS)) if x != xAxis]

        return [
            drawFigure(df),
            drawTable(df),
            xAxisOptions,
            columnsOptions,
        ]

    if "data-table.data" in changed_inputs or "data-table.columns" in changed_inputs:
        dataFrames[datasetIndex] = pd.DataFrame(rows, columns=[c['name'] for c in columns])
        df = dataFrames[datasetIndex]
        return [
            drawFigure(df),
            no_update,# drawTable(df),
            no_update,#xAxisOptions,
            no_update,#columnsOptions,
        ]

#########################################################

if __name__ == '__main__':
    sourceData = [f for f in glob.glob("*.csv")]
    
    for filename in sourceData:
        dataFrames.append( LoadData(filename) )

    app.layout = RefreshPage()

    # Run app and display result inline in the notebook
    app.run_server(debug=True)
