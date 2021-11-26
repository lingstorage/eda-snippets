import os
import re
import numpy as np
import pandas as pd
import plotly.graph_objs as go

# Get the absolute path to this script's directory.
WORKING_DIR = os.path.dirname(__file__)


#### Read datasets #####################################################
df_2018 = pd.read_csv(
    r"~/datasets/it-salary-survey-eu/IT Salary Survey EU 2018.csv",
    usecols=["Age", "City", "Company type", "Company size"],
    skipinitialspace=True,
    encoding="utf-8"
)

df_2019 = pd.read_csv(
    r"~/datasets/it-salary-survey-eu/T Salary Survey EU 2019.csv",
    usecols=["Age", "City", "Company type", "Company size"],
    skipinitialspace=True,
    encoding="utf-8"
)

df_2020 = pd.read_csv(
    r"~/datasets/it-salary-survey-eu/IT Salary Survey EU  2020.csv",
    usecols=["Age", "City", "Company type", "Company size"],
    skipinitialspace=True,
    encoding="utf-8"
)

df_2018["Year"] = 2018
df_2019["Year"] = 2019
df_2020["Year"] = 2020

df_all = pd.concat([df_2018, df_2019, df_2020])

na_rate_by_year = df_all \
    .groupby("Year") \
    .apply(lambda x: 100 * x.isna().mean()) \
    .drop(columns=["Year"])


#### Create graphs #####################################################
fig = go.Figure()

for col in na_rate_by_year.columns:
    fig.add_trace(go.Scatter(
        x=na_rate_by_year.index,
        y=na_rate_by_year[col],
        name=col,
        mode="lines+markers"
    ))

fig.update_layout(
    title_text="NA rate (= # of NAs / # of rows * 100)",
    title_font_size=24,
    title_x=0.5,
    title_xanchor="center",
    showlegend=False,
    xaxis_type='category',
    hovermode="x"
)

# Add dropdown menu
buttons_ = list([
    dict(label='All',
         method='update',
         args=[{'visible': na_rate_by_year.columns.isin(na_rate_by_year.columns)},
               {'showlegend': False}])
])

for col in na_rate_by_year.columns:
    buttons_.append(
        dict(label=col,
             method='update',
             args=[{'visible': na_rate_by_year.columns.isin([col])},
                   {'showlegend': False}])
    )

fig.update_layout(
    updatemenus=[
        dict(
            buttons=buttons_,
            direction="down",
            showactive=True,
            x=-0.1,
            xanchor="center",
            y=0.5,
            yanchor="middle"
        ),
    ]
)

fig.show()
fig.write_html(WORKING_DIR + "/output.html")
