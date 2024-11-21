import pandas as pd
import zipfile
import plotly.express as px
import matplotlib.pyplot as plt
import requests
from io import BytesIO
import plotly.graph_objects as go
#from plotly.subplots import make_subplots
from my_plots import *
import streamlit as st

@st.cache_data
def load_name_data():
    names_file = 'https://www.ssa.gov/oact/babynames/names.zip'
    response = requests.get(names_file)
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        dfs = []
        files = [file for file in z.namelist() if file.endswith('.txt')]
        for file in files:
            with z.open(file) as f:
                df = pd.read_csv(f, header=None)
                df.columns = ['name','sex','count']
                df['year'] = int(file[3:7])
                dfs.append(df)
        data = pd.concat(dfs, ignore_index=True)
    data['pct'] = data['count'] / data.groupby(['year', 'sex'])['count'].transform('sum')
    return data

@st.cache_data
def ohw(df):
    nunique_year = df.groupby(['name', 'sex'])['year'].nunique()
    one_hit_wonders = nunique_year[nunique_year == 1].index
    one_hit_wonder_data = df.set_index(['name', 'sex']).loc[one_hit_wonders].reset_index()
    return one_hit_wonder_data

data = load_name_data()
ohw_data = ohw(data)


st.title('That Super Cool Name App')

with st.sidebar:
    input_name = st.text_input('Enter a name: ')
    year_input = st.slider("Year", min_value= 1880, max_value= 2023, value= 2000)
    n_names = st.radio('Number of names per sex', [3, 5, 10])
    on = st.toggle("Activate feature")



tab1, tab2 = st.tabs(['Names', 'Year'])
if on:
    with tab1:
        name_data = data[data['name'] == input_name].copy()
        fig = px.line(name_data, x='year', y='count', color='sex')
        st.plotly_chart(fig)

        next_fig = name_sex_balance_plot(data, name=input_name)
        if next_fig:  # Check if a figure was returned
            st.pyplot(next_fig)

    with tab2:
        fig2 = top_names_plot(data, year=year_input, n=n_names)
        st.plotly_chart(fig2)

        st.write('Unique Names Table')
        output_table = unique_names_summary(data, year_input)
        st.dataframe(output_table)

        with st.expander("See explanation"):
            st.write('''
            The table above gives some statistics based on the year you selected and the female/male names of that year. The Total Names
                    section gives you what you probably can infer, the number of names/number of babies born of that gender. The Unique
                    Names section tells you how many different names there are within both genders. Finally, Percent Unique is a division
                    problem that takes Unique Names and divides it by Total Names for each gender and multiplies it by 100 to give you the 
                    percentage of unique names there are for each gender.
            ''')








