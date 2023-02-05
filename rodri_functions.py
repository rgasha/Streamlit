#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on Tue Jan 31 14:10:47 2023

@author: rodrigogasha
'''

import streamlit as st
import pandas as pd
import numpy as np
import folium
import geojson
import branca.colormap as cmp
import streamlit_folium as st_folium
import plotly.express as px
import holoviews as hv
import hvplot.pandas



def create_df(gender):
    
    global marks_100m
    if gender == 'Women':
        marks_100m = pd.read_json('women_100m_top.json', lines=True)
    else:
        marks_100m = pd.read_json('men_100m_top.json')
  
    # Set features to date
    marks_100m[['DOB','Date']] = marks_100m[['DOB','Date']].apply(lambda x: pd.to_datetime(x).dt.date)
  
    # Athlete's age at the time of setting the record
    marks_100m['Age'] = (marks_100m['Date'] - marks_100m['DOB']).astype('<m8[Y]').astype('Int64')
    
    # Set Rank column to integer type
    marks_100m['Rank'] = marks_100m['Rank'].astype('Int64')
    
    # Remove duplicates
    marks_100m.drop_duplicates(inplace = True)
    
    # Get country full name (https://stackoverflow.com/questions/70335028/how-do-i-convert-an-ioc-country-code-to-country-name)
    ioc = pd.read_html('https://en.wikipedia.org/wiki/List_of_IOC_country_codes')[0]
    ioc = ioc.assign(Code=ioc['Code'].str[-3:]).set_index('Code')['National Olympic Committee']
    marks_100m['countryName'] = marks_100m['Nat'].map(ioc)
    marks_100m['countryName'] = marks_100m['countryName'].fillna('Unknown')
    
    
    
def set_data(gender):
    
    create_df(gender)
    st.dataframe(marks_100m)
    st.write('')
    st.markdown(
    '''
    The dataset was scrapped from the [World Athletics website](https://www.worldathletics.org/) and has 9 columns:
    - **Rank**: position in all time top list
    - **Mark**: measure in seconds of how fast the athlete completed the 100m event 
    - **Competitor**: full name of the athlete
    - **DOB**: date of birth of the athlete
    - **Nat**: nationality
    - **Venue**: location where the competition took place
    - **Date**: date of the competition
    - **Age**: the age of the athlete at the time of setting the record (added by me)
    - **countryName**: country of nationality (added by me)
    '''
    )
    
    
    
def set_eda(gender):
    
    create_df(gender)
    describe = marks_100m.describe()
    st.write(describe)
    st.write('- The average age is ', round(describe['Age'][1],2))
    st.write('- The minimum age is ', round(describe['Age'][3]))
    st.write('- The maximum age is ', round(describe['Age'][7]))
    st.write('')
    st.write('Missing values', marks_100m.isnull().sum(), 
             "There are some missing values in the columns 'DOB' and 'Age', however that won\'t affect our analysis")
    st.write('')
    nat_frequency = marks_100m.countryName.value_counts()
    st.write(nat_frequency)
    st.write('- The first country with the fastest sprinters is ', nat_frequency.index[0], ' with ', nat_frequency[0], ' athletes in the world ranking.')
    st.write('- The second country with the fastest sprinters is ', nat_frequency.index[1], ' with ', nat_frequency[1], ' athletes in the world ranking.')
    st.write('- The third country with the fastest sprinters is ', nat_frequency.index[2], ' with ', nat_frequency[2], ' athletes in the world ranking.')
    
    
    
def set_plots(gender):
    
    create_df(gender)
    
    # Record progression plot
    grouped = marks_100m.groupby(['Date'], as_index=False).agg({'Mark': 'min'})
    
    historic_marks = pd.DataFrame(columns=['Date', 'Mark'])
    historic_marks = historic_marks.append({'Date': grouped.iloc[0, 0], 'Mark': grouped.iloc[0, 1]}, ignore_index=True)
    
    for i in range(1, len(grouped)):
        if grouped.iloc[i, 1] <= grouped['Mark'][0:i].min():
            historic_marks = historic_marks.append({'Date': grouped.iloc[i, 0], 'Mark': grouped.iloc[i, 1]}, ignore_index=True)
    
    result = historic_marks.merge(marks_100m, on = ['Date', 'Mark'])[['Date', 'Mark', 'Competitor', 'countryName']]
    
    fig = px.line(result, 
                  x = result['Date'].astype(str),
                  y = 'Mark', 
                  title = '100m World Record Progression',
                  hover_data = ['Competitor', 'countryName'],
                  labels = {'x': 'Date'},
                  markers = True,
                  )

    st.plotly_chart(fig)
    
    
    # Ranking bar chart
    st.subheader('Ranking plot')
    
    rank_limit = st.slider('Select rank limit', 
                           min_value = 1,
                           max_value = 100,
                           value = 10)

    fig1 = marks_100m[:rank_limit].hvplot.scatter(x = 'Rank', 
                                                  y = 'Mark', 
                                                  hover_cols=['Competitor', 'countryName'], 
                                                  alpha = 0.7)
                                    
    st.write(hv.render(fig1, backend='bokeh'))
    
    # Average age chart
    result2 = marks_100m.groupby(['countryName'], as_index=False).agg({'Age': 'mean'})
    
    choose_country = st.multiselect(label = 'Choose which countries',
                                    options = result2['countryName'],
                                    default = ['Jamaica', 'United States'])

    fig2 = px.bar(result2.loc[result2['countryName'].isin(choose_country)], 
                  x='Age', 
                  y='countryName', 
                  orientation='h',
                  title = 'Average age per country',
                  labels = {'countryName': 'Country'})
    
    st.plotly_chart(fig2)
    
    # Venue plot
    venue_table = marks_100m['Venue'].value_counts().reset_index()
    
    venue_limit = st.slider('Select amount of venues to display', 
                            min_value = 1,
                            max_value = 100,
                            value = 10)
    
    fig3 = px.bar(venue_table[:venue_limit],
                  x = 'index',
                  y = 'Venue',
                  title = 'Venues chart',
                  labels = {'Venue': 'Count',
                            'index': 'Venue Name'}
                  )
    
    st.plotly_chart(fig3)
    st.write('The venue where most of the fastest mark where made is ', venue_table['index'][0], '.')
    

def set_maps(gender):
    
    create_df(gender)
    
    countries_table = marks_100m['Nat'].value_counts().reset_index()

    create_map(countries_table, 'Nat')
    
    st.subheader('Map of frequency of historic marks according to country nationality')
    st_folium.folium_static(m, width = 725)
    st.write('As we can observe in the map, the countries with the fastest runners are United States and Jamaica.')
    
    location_table = marks_100m['Venue']
    location_table = location_table.str[-4:-1].value_counts().reset_index()
    
    create_map(location_table, 'Venue')
    
    st.write('')
    st.subheader('Map of frequency of historic marks according to competition venue')
    st_folium.folium_static(m, width = 725)
    st.write('Most of the competitions where the fastest marks in 100 meters took place in the United States.')



def create_map(df, column_name):
    
    world_map = geojson.load(open('countries.geojson', 'r', encoding = 'utf-8'))
    
    global m
    m = folium.Map(location=[40.4309, -3.6878], zoom_start = 1)

    for location_info in world_map['features']:
        if df.loc[df['index'] == location_info['properties']['ISO_A3']][column_name].empty:
            location_info['properties']['freq'] = 0
        else:
            location_info['properties']['freq'] = int(df.loc[df['index'] == location_info['properties']['ISO_A3']][column_name])

    colors = cmp.LinearColormap(
        ['lightcyan','lightblue', 'steelblue', 'blue'],
        vmin = min(df[column_name]), vmax = max(df[column_name]),
        caption = 'Number of historic marks')

        
    def country_styles (feature):
        return {'radius': 7,
                'fillColor': '#gray' if feature['properties']['freq'] == 0 else colors(feature['properties']['freq']), 
                'color': '#gray' if feature['properties']['freq'] == 0 else colors(feature['properties']['freq']), 
                'weight': 1,
                'opacity': 1,
                'fillOpacity': 0.8}

    folium.GeoJson(world_map, style_function = country_styles,
                    tooltip = folium.GeoJsonTooltip(fields = ['ADMIN', 'freq'],
                                                        aliases=['Country of origin: ','Amount of historic marks: '],
                                                        style = ('background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;')
                    )).add_to(m)
    
    colors.add_to(m)