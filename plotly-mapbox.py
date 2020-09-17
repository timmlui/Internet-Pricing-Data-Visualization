import pandas as pd
import plotly.express as px  # module(version 4.7.0)

import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from urllib.request import urlopen
import json
import pycountry


# Start the App
app = dash.Dash(__name__)

# ------------------------------------------------------------------------------
# Mapbox token
token = open(".mapbox-token").read()

# ------------------------------------------------------------------------------
# Import and clean data (importing csv into pandas)
df_mobile_price = pd.read_csv("csv/global-mobile-data-price-comparison-2020.csv")
print(df_mobile_price.head())

df_broadband_price = pd.read_csv("csv/global-broadband-pricing-study-2020.csv")
print(df_broadband_price.head())

df_broadband_speed = pd.read_csv("csv/worldwide-broadband-speed-league-2020-data.csv")
print(df_broadband_speed.head())

# ------------------------------------------------------------------------------
# Used to find the ISO_A3 value for all countries

# list_countries = df['Country_code'].tolist()
# d_country_ISO3 = {} # Pair country names to its ISO
# for country in list_countries:
#   try:
#     country_data = pycountry.countries.search_fuzzy(country)
#     # country_data is a list of objects of class pycountry.db.Country
#     # The first item ie. at index 0 of list is best fit
#     country_ISO3 = country_data[0].alpha_3
#     d_country_ISO3.update({country: country_ISO3})
#   except: # If no country found, empty ISO3
#     print('could not add ISO 3 code for ->', country)
#     d_country_ISO3.update({country: ''})

# # create a new column ISO3
# for k, v in d_country_ISO3.items():
#   df.loc[(df.Country_code == k), 'ISO3'] = v

# ------------------------------------------------------------------------------
# All countries geojson data

# Only ISO_A3 given
# with urlopen('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json') as response:
#     countries = json.load(response)

# ISO_A2 and ISO_A3 given
with urlopen('https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson') as response:
    countries = json.load(response)

# print(df_mobile_price.head())
# print(d_country_ISO3)

# ------------------------------------------------------------------------------
# App layout

app.layout = html.Div([

  html.Div(id='figure_header', children=[]),

  dcc.RadioItems(
    id='radio_data',
    options=[{'label': i, 'value': i} for i in ['Mobile Pricing', 'Broadband Pricing', 'Broadband Speed']],
    value='Mobile Pricing'
  ),

  # html.Br(),

  dcc.Graph(id='world_map', figure={}, style={'height': '700px'}),

  html.Div(
    id='list_container',
    children=[
      html.Div(id='top_five', children=[]),
      html.Div(id='last_five', children=[])
    ]
  )

])

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='figure_header', component_property='children'),
     Output(component_id='world_map', component_property='figure'),
     Output(component_id='top_five', component_property='children'),
     Output(component_id='last_five', component_property='children')],
    [Input(component_id='radio_data', component_property='value')]
)

# Each input is required as an argument for the callback function
def update_graph(option_slctd):

  # Plotly Express - optimized and recommended to use 
  # (but not all graph objects are supported, so may need to use below Plotly Graph Objects)

  if option_slctd == 'Mobile Pricing':
    header = 'MOBILE DATA PRICING 2020 per 1GB (USD)'

    dff=df_mobile_price.copy()
    fig_color="Average price of 1GB (USD)"
    fig_colorscale="dense" #speed, matter, algae, dense, deep
    fig_hover_data={
      "Country code": False,
      "Rank": True,
      "Average price of 1GB (USD)": ':$.2f',
      "Most expensive 1GB (USD)": True,
      "Cheapest 1GB for 30 days (USD)": ':$.2f',
      "Plans measured": True,
      "Sample date": True
    }
    fig_labels={
      "Average price of 1GB (USD)": "Average Price",
      "Most expensive 1GB (USD)": "Most Expensive",
      "Cheapest 1GB for 30 days (USD)": "Cheapest",
      "Plans measured": "Plans Measured",
      "Sample date": "Sample Date"
    }

  elif option_slctd == 'Broadband Pricing':
    header = 'BROADBAND PRICING 2020 per Month (USD)'

    dff=df_broadband_price.copy()
    fig_color="Average cost of a fixed-line broadband package (Per month in USD)"
    fig_colorscale="Bluyl" #speed, matter, algae, dense, deep
    fig_hover_data={
      "Country code": False,
      "Rank": True,
      "Average cost of a fixed-line broadband package (Per month in USD)": ':$.2f',
      "Most expensive fixed-line broadband package measured (USD)": True,
      "Cheapest broadband package measured (USD)": True,
      "Packages measured": True,
      "Sample date": True
    }
    fig_labels={
      "Average cost of a fixed-line broadband package (Per month in USD)": "Average Cost",
      "Most expensive fixed-line broadband package measured (USD)": "Most Expensive",
      "Cheapest broadband package measured (USD)": "Cheapest",
      "Packages measured": "Packages Measured",
      "Sample date": "Sample Date"
    }
  
  elif option_slctd == 'Broadband Speed':
    header = 'BROADBAND DOWNLOAD SPEED 2020 (Mbps)'

    dff=df_broadband_speed.copy()
    fig_color="Mean download speed (Mbps)"
    fig_colorscale="matter" #speed, matter, algae, dense, deep
    fig_hover_data={
      "Country code": False,
      "Rank": True,
      "Mean download speed (Mbps)": ':.2f Mbps',
      "Unique IPs tested": True,
      "Total tests": True,
      "How long it takes to download a 5GB movie (HH:MM:SS)": True
    }
    fig_labels={
      "Mean download speed (Mbps)": "Mean Download Speed",
      "Unique IPs tested": "Unique IPs Tested",
      "Total tests": "Total Tests",
      "How long it takes to download a 5GB movie (HH:MM:SS)": "Avg Time to Download a 5GB movie"
    }

  fig = px.choropleth_mapbox(
    data_frame=dff,
    geojson=countries,
    featureidkey="properties.ISO_A2",
    locations="Country code",
    color=fig_color,
    color_continuous_scale=fig_colorscale, #speed, matter, algae, dense, deep
    hover_name="Name",
    hover_data=fig_hover_data,
    zoom=1,
    center={"lat": 50, "lon": 0},
    opacity=0.3,
    template="plotly_dark",
    labels=fig_labels
  )

  fig.update_layout(mapbox_style="dark", mapbox_accesstoken=token)
  fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

  # Determine the top and last five countries
  dff_top_five=dff.head()
  top_five='Top Five:'
  for i in range(5):
    top_five += ' {}. {}'.format(i+1, dff_top_five["Name"].iloc[i])

  dff_top_five=dff.tail()
  last_five='Bottom Five:'
  for i in reversed(range(5)):
    last_five += ' {}. {}'.format(dff_top_five["Rank"].iloc[i], dff_top_five["Name"].iloc[i])

    # import plotly.graph_objects as go
    # fig = go.Figure(go.Choroplethmapbox(
    #   geojson=countries,
    #   featureidkey="properties.ISO_A2",
    #   locations=df_mobile_price.Country_code,
    #   z=df_mobile_price["Average price of 1GB (USD)"].astype(float),
    #   colorscale="speed",
    #   marker_opacity= 0.3,
    #   hovertemplate=
    #     '<i>Rank</i>: %{df_mobile_price.Rank}' +
    #     '<br><i>Country</i>'
    # ))

  # Each return argument is for their respective outputs
  return header, fig, top_five, last_five


# ------------------------------------------------------------------------------
if __name__ == '__main__':
  app.run_server(debug=True)