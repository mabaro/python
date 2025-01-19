import matplotlib.pyplot as plt
import pandas as pd
import panel as pn

pn.extension("perspective")

@pn.cache
def initialize_data():
    dataset = { 'data':[1,2,3], "year":[1998,1999,2001], "temperature":[33,36,33.6] }
    dataframe = pd.DataFrame.from_dict(dataset, orient="index").transpose()
    print(dataframe)
    return dataset, dataframe

def update_name_options(year):
    names = dataframe.keys().to_list()
    print("names: ", names)
    name_select.options = names
    if not name_select.value or name_select.value not in names:
        name_select.value = names[0] if names else None

def update_data_graph(name, year):
    try:
        data_graph.loading = True
        graph_key = "testID"
        # axes = dataset.plot_storm(graph_key)
        # plt.close(axes.figure)
        # data_graph.object = axes.figure
        # storm_table.object = dataset.get_storm(graph_key).to_dataframe()
    finally:
        data_graph.loading = False

# Instantiate Widgets & Pane
year_slider = pn.widgets.IntRangeSlider(
    name="Time", value=(0,600), start=0, end=600, step=1
)
name_select = pn.widgets.Select(name="Name")
data_graph = pn.pane.Matplotlib(plt.figure(), sizing_mode="stretch_both")
storm_table = pn.pane.Perspective(editable=False, sizing_mode="stretch_both")

# Layout the app
sidebar = pn.Column(year_slider, name_select)
main = pn.Tabs(("Preview", data_graph), ("Table", storm_table))

template = pn.template.FastListTemplate(
    sidebar=sidebar,
    main=main,
)

# Initialize data
dataset, dataframe = initialize_data()

# Define Callbacks
pn.bind(update_name_options, year=year_slider.param.value_throttled, watch=True)
pn.bind(update_data_graph, name=name_select, year=year_slider.param.value_throttled, watch=True)

# Pre-populate values
year_slider.param.trigger("value_throttled")

# Serve the app
template.show()