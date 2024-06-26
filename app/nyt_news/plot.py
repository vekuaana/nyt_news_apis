import yaml
import os
import logging.config
import streamlit as st
import numpy as np
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError
from connection_db import MongoDBConnection
import pandas as pd
from config import PACKAGE_ROOT


logger = logging.getLogger(__name__)


try:
    # Attempt to connect to MongoDB within a container environment
    logger.info("Try to log with mongodb container")
    db = MongoDBConnection('localhost').conn_db
except ServerSelectionTimeoutError:
    # Handle the case where the connection times out if we try to connect outside the container
    logger.info("Try to connect outside the container with localhost")
    db = MongoDBConnection('mongodb').conn_db
except OperationFailure as of:
    logger.error(of)


collection = db["usa_election_articles"]
data = pd.DataFrame(list(collection.find({})))
data['year'] = [int(str(x)[:4]) for x in data['pub_date']]
data = data.explode('main_candidate').fillna('')
data['cleaned_polarity'] = [[d['prediction'] for d in x if d["entity"] == y] for x, y in list(zip(data['polarity'], data['main_candidate']))]
data['cleaned_polarity'] = [x[0] if x and isinstance(x, list) else np.nan if x == [] else x for x in data['cleaned_polarity'] ]


data = data.dropna(axis=0, subset=['cleaned_polarity'])

year = st.sidebar.slider('year', int(data['year'].min()), int(data['year'].max()))
election_id = st.sidebar.selectbox('election_id', options=['All'] + list(data['election_id'].unique()))
main_candidate = st.sidebar.selectbox('main_candidate', options=['All'] + list(data['main_candidate'].unique()))
polarity = st.sidebar.selectbox('polarity', options=['All'] + list(data['cleaned_polarity'].unique()))

filtered_data = data.copy()
# Filter data based on sidebar inputs
if election_id != 'All':
    filtered_data = filtered_data[filtered_data['election_id'] == election_id]
if main_candidate != 'All':
    filtered_data = filtered_data[filtered_data['main_candidate'] == main_candidate]
if polarity != 'All':
    filtered_data = filtered_data[filtered_data['cleaned_polarity'] == polarity]
filtered_data = filtered_data[filtered_data['year'] >= year]

import plotly.express as px
st.subheader('Nombre de documents par année d election sur les candidats')
st.bar_chart(filtered_data['year'].value_counts())



st.subheader('Polarité')
fig = px.pie(filtered_data, names='cleaned_polarity', title='Distribution de la polarité')
st.plotly_chart(fig)

st.subheader('Livres recommandés')
st.bar_chart(filtered_data['cleaned_polarity'].value_counts().nlargest(10))

