import streamlit as st
from rodri_functions import * # Custom functions

st.title('World Athletics: all time top 100 meters')

# Sidebar
with st.sidebar as sb:
    st.title('Dashboard')
    select_gender = st.selectbox('Select gender', ('Men', 'Women'))
    menu = st.radio('Select tab', ('Intro', 'Data', 'Exploratory analysis', 'Plots', 'Maps'))

if menu == 'Intro':
    st.markdown(
        '''
        - #### **Author**: Rodrigo Gasha
        - #### **Date**: 1/2/2023
        '''
        )
    st.markdown('')
    st.image('https://media.aws.iaaf.org/media/Original/b25a46dd-a7cf-4ed1-8cd1-32302a0e365d.jpg')
    st.markdown(
        '''
        The purpose of this data app is to put into practise my visualization skills in Streamlit.
        
        I have scrapped some data from the World Athletics webpage and going to explore it to gain some insights from it.
        ''')
        
        
elif menu == 'Data':
    set_data(select_gender)
    
elif menu == 'Exploratory analysis':
    set_eda(select_gender)

elif menu == 'Plots':
    set_plots(select_gender)
    
elif menu == 'Maps':    
    set_maps(select_gender)
