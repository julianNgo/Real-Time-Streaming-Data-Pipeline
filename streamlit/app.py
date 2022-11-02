import streamlit as st # web development
import numpy as np # np mean, np random 
import pandas as pd # read csv, df manipulation
import time # to simulate a real time data, time loop 
import plotly.express as px # interactive charts
import psycopg2

#### Dashboard design
st.set_page_config(
    page_title = 'Dashboard',
    page_icon = '✅',
    layout = 'wide'
)

# dashboard title

st.title("Event Message Dashboard")

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

conn = init_connection()

# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=1)
def sql_to_dataframe(query):
    cur = conn.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cols = []
    for elt in cur.description:
        cols.append(elt[0])
    df = pd.DataFrame(data= data, columns= cols)
    return df

# creating a single-element container.
placeholder = st.empty()
i = 0
while True:
    df = sql_to_dataframe("SELECT * FROM raw_event_message_db ORDER BY event_datetime desc;")
    # Print results.
    df = df.loc[:,['event_id','event_server_status_color_name_severity_level', 'event_datetime','event_server_type', 'event_country_code',
        'event_country_name', 'event_city_name',
        'event_estimated_issue_resolution_time',
        'event_server_status_color_name',
        'event_server_status_severity_level',
        'event_message_count']]

    random_val_1 = int(np.random.choice(range(1,100)))
    random_val_2 = int(np.random.choice(range(100,1000)))
    with placeholder.container():
        st.markdown("### KPI")
        kpi1, kpi2 = st.columns(2)
        kpi1.metric(label="Random ⏳", value=int(random_val_1), delta= random_val_1)
        kpi2.metric(label="Married Count 💍", value= int(random_val_2), delta= random_val_2)

        st.markdown("### Line Chart")
        fig = px.line(df.head(30), x="event_datetime", y="event_estimated_issue_resolution_time")
        st.write(fig)

        st.markdown("### Detailed Data View")
        st.dataframe(df)
        time.sleep(1)
    