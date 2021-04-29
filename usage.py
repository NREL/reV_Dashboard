import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from plotly import graph_objs as go
from plotly.graph_objs import *
from dash.exceptions import PreventUpdate

import json,geojson
import pathlib

import nrel_dash_components as ndc
import parallel_coordinate_plot as pcp
import deckgl_ly as dgl


app = dash.Dash(__name__)
app.title = 'reV Dashboard Visualization'

# Plotly mapbox public token
MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoicGRpYXoiLCJhIjoiY2s5c3hsYmlpMWE3YzN2cXFmbnlwcjJydCJ9.Oka9RADl2fwV7HfIGYFyuw"

# region = "Interior/"
# The types of layers
Regions=['CONUS','Great Lakes','Mountain','Northeast','Pacific','Southeast','West North Central','West South Central']

QOI_map = {'Mean Capacity Factor':'Mean_CF','All-in LCOE':'All_in_LCOE','Site LCOE':'Site_LCOE','Area Sq. Km':'Area_Sq_Km','LCOT':'LCOT','Capacity':'Capacity','Distance Km':'Dist_Km'}
revQOI_map = dict(map(reversed, QOI_map.items()))
stat_map = {'Mean':'mean_','Standard Deviation':'stdev_'}
rev_stat_map = dict(map(reversed,stat_map.items()))

# Set the path to the data
PCP_DATA_PATH = pathlib.Path(__file__).parent.joinpath("./data/CONUS/").resolve()

DATA_PATH = pathlib.Path(__file__).parent.joinpath("data").resolve()

# Get inital data for the Parallel Coordinate Plot
with open(PCP_DATA_PATH.joinpath('scenario_averages.json')) as f:
    row_Data = json.load(f)

with open(PCP_DATA_PATH.joinpath('data_info.json')) as f:
    data_Info = json.load(f)

# Color ranges for the different variables
colorMaps = {
    "geojson" : {
        "range": [[166,97,26],[223,194,125],[255,255,255],[128,205,193],[1,133,113]],
        "rangeRGB": ['rgb(166,97,26)','rgb(223,194,125)','rgb(255,255,255)','rgb(128,205,193)','rgb(1,133,113)'],
        "scale": "diverging"
    },
    # "scatterplot": {
    #     "range": [[255,255,212],[254,227,145],[254,196,79],[254,153,41],[236,112,20],[204,76,2],[140,45,4]],
    #     "rangeRGB": ['rgb(255,255,212)','rgb(254,227,145)','rgb(254,196,79)','rgb(254,153,41)','rgb(236,112,20)','rgb(204,76,2)','rgb(140,45,4)'],
    #     "scale" : "quantize"
    # }
    # "scatterplot": {
    #     "range": [[255,255,212],[254,227,145],[254,196,79],[254,153,41],[236,112,20],[204,76,2],[140,45,4]],
    #     "rangeRGB":['rgb(218,218,235)','rgb(188,189,220)','rgb(158,154,200)','rgb(128,125,186)','rgb(106,81,163)','rgb(84,39,143)','rgb(63,0,125)'],
    #     "scale" : "quantize"
    # },
    # "scatterplot_inv": {
    #     "range": [[255,255,212],[254,227,145],[254,196,79],[254,153,41],[236,112,20],[204,76,2],[140,45,4]],
    #     "rangeRGB":['rgb(63,0,125)','rgb(84,39,143)','rgb(106,81,163)','rgb(128,125,186)','rgb(158,154,200)','rgb(188,189,220)','rgb(218,218,235)'],
    #     "scale" : "quantize"
    # }
    "scatterplot": {
        "range": [[255,255,212],[254,227,145],[254,196,79],[254,153,41],[236,112,20],[204,76,2],[140,45,4]],
        "rangeRGB":['rgb(255,255,204)','rgb(255,237,160)','rgb(254,217,118)','rgb(254,178,76)','rgb(254,178,76)','rgb(253,141,60)','rgb(252,78,42)','rgb(227,26,28)','rgb(189,0,38)','rgb(128,0,38)'],
        "scale" : "quantize"
    },

}

# view states for each NREL region selection
viewStates = {
    'West North Central' : {
        "longitude": -87.601,
        "latitude": 43.555,
        "zoom": 3.9,
        "pitch": 0,
        "bearing": 0
    },

    'Mountain' : {
        "longitude": -100.5,
        "latitude": 41.214,
        "zoom": 3.6,
        "pitch": 0,
        "bearing": 0
    },

    'Pacific':{
        "longitude": -111.319,
        "latitude": 41.571,
        "zoom": 3.6,
        "pitch": 0,
        "bearing": 0
    },
    'Interior' : {
        "longitude": -74.70707,
        "latitude": 37.518328,
        "zoom": 3,
        "pitch": 0,
        "bearing": 0
    },
    'CONUS' : {
        "longitude": -80.929,
        "latitude": 37.737,
        "zoom": 2.75,
        "pitch": 0,
        "bearing": 0
    },
    'West South Central' : {
        "longitude": -90.258,
        "latitude": 31.783,
        "zoom": 4.5,
        "pitch": 0,
        "bearing": 0
    },
    'Great Lakes': {
        "longitude": -76.988023,
        "latitude": 42.491511,
        "zoom": 4.5,
        "pitch": 0,
        "bearing": 0
    },

    'Southeast' : {
        "longitude": -72.224,
        "latitude": 33.026,
        "zoom": 3.9,
        "pitch": 0,
        "bearing": 0
    },

    'Northeast' : {
        "longitude": -68.196,
        "latitude": 43.0,
        "zoom": 4.5,
        "pitch": 0,
        "bearing": 0
    },
}
app.layout =  ndc.NRELApp(
    appName="reV Dashboard Visualization",
    children=[
        html.Hr(),
        html.Div(className='section', children=[
            html.Div(className='tile is-ancestor', children=[
                # Left UI tiles
                html.Div(className='tile is-vertical is-3 uiDivs', children=[
                    # Data display UI
                    html.Div(className='tile' , children=[
                        html.Div(className='tile is-parent', children=[
                            html.Article(className='tile is-child notification is-dark', children=[
                                html.P(className='title', children=["Region Selection"]),
                                "NREL Region",
                                dcc.Dropdown(id="lbnl-dropdown",
                                    options=[{"label": i, "value": i}for i in Regions],
                                    value='CONUS'
                                )
                            ])
                        ])
                    ]),
                    # Filters UI
                    html.Div(className='tile' , children=[
                        html.Div(className='tile is-parent is-vertical', children=[
                            html.Article(className='tile is-child notification is-dark', children=[
                            html.P(className='title', children=["Data Options"]),
                            "Quantity of Interest:",
                            dcc.Dropdown(
                                id="qoi_dropdown",
                                options=[{"label": i, "value": QOI_map[i]} for i in QOI_map],
                                value='Area_Sq_Km'
                            ),
                            html.Br(),
                            "Statistic:",
                            dcc.Dropdown(
                                id="stat_dropdown",
                                options=[{"label": i, "value": stat_map[i]} for i in stat_map],
                                value='mean_'
                            ),
                            html.Br(),
                            "Radius Scale:",
                            dcc.Slider(
                                id='radius_slider',
                                min=50,
                                max=1500,
                                step=50,
                                value=750,
                            ),
                            html.Br(),
                            html.Button('Toggle Uncertainty', id='uncertainty_button', n_clicks=1)
                        ])
                      ]),
                    ])
                ]),
                # Map tile
                html.Div(className='tile' , children=[
                    html.Div(className='tile is-parent', children=[
                        html.Div(className='tile is-dark mapDiv', children=[
                            dgl.DeckglLy(
                                id='map',
                                mapboxtoken=MAPBOX_ACCESS_TOKEN,
                                mapStyle='mapbox://styles/mapbox/dark-v10',
                                viewState=viewStates['CONUS']
                            ),
                            dgl.MapLegend(id='mapLegend',
                                title='Map Legend',
                            ),
                          ])
                      ])
                ]),
            ]),
            # Parallel coordinate plot tile
            html.Div(className='tile is-ancestor', children=[
                html.Div(className='tile', children=[
                    html.Div(className='tile is-parent', children=[
                            html.Article(className='tile is-child notification', children=[
                                pcp.Parallel_Coordinate_Plot(
                                            id='pcp',
                                            row_Data = row_Data,
                                            data_Info = data_Info,
                                            activeObjs = [],
                                            uncertainty = True
                                            )
                        ])
                    ])
                ])
            ])
        ])
    ]
)



@app.callback([Output("pcp", "row_Data"), Output("pcp", "data_Info")],[ Input('lbnl-dropdown', 'value')])
def update_pcp(region):
    # If no layer is chosen, don't update
    if region == None:
        raise PreventUpdate()

    SELECTED_DATA_PATH = pathlib.Path(__file__).parent.joinpath("./data/"+region+"/").resolve()

    with open(SELECTED_DATA_PATH.joinpath('scenario_averages.json')) as f:
        row_data = json.load(f)

    with open(SELECTED_DATA_PATH.joinpath('data_info.json')) as f:
        data_info = json.load(f)

    return [row_data, data_info]


@app.callback( Output(component_id='pcp',component_property='uncertainty'),[Input(component_id= 'uncertainty_button',component_property= 'n_clicks')])
def callerBack(n_clicks):
    if n_clicks % 2 == 0:
        return False
    else:
        return True

#Create the callback
@app.callback([Output("map", "layers"), Output("map", "viewState")],[ Input('lbnl-dropdown', 'value'),Input('qoi_dropdown', 'value'),Input('stat_dropdown', 'value'),Input('radius_slider', 'value')  ])
def update_map(region,qoi_value,stat_value,slider_value):
    # The map layers
    mapLayers=[];

    # If no layer is chosen, don't update
    if region == None or qoi_value == None or stat_value == None:
        raise PreventUpdate()

    SELECTED_DATA_PATH = pathlib.Path(__file__).parent.joinpath("./data/"+region+"/").resolve()
    with open(SELECTED_DATA_PATH.joinpath("map_data.json")) as f:
        mapData = json.load(f)

    with open(SELECTED_DATA_PATH.joinpath('map_data_info.json')) as f:
        map_data_info = json.load(f)
    the_qoi = stat_value+qoi_value
    colormap_range = colorMaps['scatterplot']['rangeRGB']
    if qoi_value == 'LCOT' or qoi_value == 'All_in_LCOE' or qoi_value == 'Site_LCOE' or qoi_value == 'Dist_Km':
        colormap_range = colormap_range[::-1]

    revScatterLayer = {
        "type": "ScatterplotLayer",
        "id": "rev-scatter",
        "getPosition": "function(d){return [d.longitude,d.latitude]}",
        "getRadius": "function(d){return d.num_values}",
        "radiusScale":slider_value,
        "data": mapData,
        "value":the_qoi,
        "pickable": True,
        "controller":True,
        "opacity": 0.8,
        "stroked": False,
        "filled": True,
        "radiusMinPixels":1,
        "radiusMaxPixels":300,
        "lineWidthMinPixels": 1,
        "colorMap": {
            "scale": colorMaps['scatterplot']['scale'],
            "value": the_qoi,
            "range": colormap_range,
            "extent": [map_data_info[the_qoi]['min'],map_data_info[the_qoi]['max']]
        }
    }
    mapLayers.append(revScatterLayer)
    viewState = viewStates[region]
    return [mapLayers, viewState]

@app.callback([Output("mapLegend","layers")],[ Input('lbnl-dropdown', 'value'),Input('qoi_dropdown', 'value'),Input('stat_dropdown', 'value') ])
def update_legend(region, qoi_value,stat_value):
    legendLayers = []

    if region == None or qoi_value == None or stat_value == None:
        raise PreventUpdate()


    if qoi_value != None and region != None and stat_value != None:
        colormap_range = colorMaps['scatterplot']['rangeRGB']
        if qoi_value == 'LCOT' or qoi_value == 'All_in_LCOE' or qoi_value == 'Site_LCOE' or qoi_value == 'Dist_Km':
            colormap_range = colormap_range[::-1]
        SELECTED_DATA_PATH = pathlib.Path(__file__).parent.joinpath("./data/"+region+"/").resolve()
        with open(SELECTED_DATA_PATH.joinpath('map_data_info.json')) as f:
            map_data_info = json.load(f)
        the_qoi = stat_value+qoi_value
        layers={
            'type': "colorLegend",
            'id': "dataLayer",
            'value': the_qoi,
            'title': revQOI_map[qoi_value]+"\n ("+ rev_stat_map[stat_value] +")",
            "colorMap": {
                "scale": colorMaps['scatterplot']['scale'],
                "value": the_qoi,
                "range": colormap_range,
                "extent": [map_data_info[the_qoi]['min'],map_data_info[the_qoi]['max']]
            }
        }
        legendLayers.append(layers);
    return [legendLayers]


if __name__ == '__main__':
    app.run_server(debug=True)
