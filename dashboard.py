import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')


st.set_page_config(page_title='Superstore',page_icon=":barchart:",layout='wide')

st.title(" :bar_chart: Superstore Dashboard")
st.write('The dashboard is based from Superstore data that can be retrieved from this link : https://community.tableau.com/s/question/0D54T00000CWeX8SAL/sample-superstore-sales-excelxls')
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)


#os.chdir(r"D:\streamlit")
df =  pd.read_csv('superstore.csv',encoding= "ISO-8859-1")

state2abbrev = {
        'Alaska': 'AK',
        'Alabama': 'AL',
        'Arkansas': 'AR',
        'Arizona': 'AZ',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'District of Columbia': 'DC',
        'Delaware': 'DE',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Hawaii': 'HI',
        'Iowa': 'IA',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Massachusetts': 'MA',
        'Maryland': 'MD',
        'Maine': 'ME',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Missouri': 'MO',
        'Mississippi': 'MS',
        'Montana': 'MT',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Nebraska': 'NE',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'Nevada': 'NV',
        'New York': 'NY',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Virginia': 'VA',
        'Vermont': 'VT',
        'Washington': 'WA',
        'Wisconsin': 'WI',
        'West Virginia': 'WV',
        'Wyoming': 'WY',
        'Puerto Rico': 'PR',
        'Virigin Islands': 'VI'
    }

df['State_id'] = df['State'].map(state2abbrev)

col1,col2 = st.columns((2))
df['Order Date'] = pd.to_datetime(df['Order Date'])

startDate = pd.to_datetime(df['Order Date']).min()
endDate = pd.to_datetime(df['Order Date']).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("Start Date", endDate))

df = df[(df['Order Date'] >= date1) & (df['Order Date'] <= date2)].copy()

#Region
st.sidebar.header('Choose your filter :')
region = st.sidebar.multiselect("Select Region :", df['Region'].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df['Region'].isin(region)]


#State
state = st.sidebar.multiselect("Select State :", df2['State'].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2['State'].isin(state)]

#City
city = st.sidebar.multiselect("Select City :", df3['City'].unique())
if not city:
    df4 = df3.copy()
else:
    df4 = df3[df3['City'].isin(city)]

#filtering data
if not region and not state and not city :
    filtered_df = df
elif not state and not city :
    filtered_df = df[df['Region'].isin(region)]
elif not region and not city:
    filtered_df = df[df['State'].isin(state)]
elif city:
    filtered_df = df[df['City'].isin(city)]
elif state and city :
    filtered_df = df[df['State'].isin(state) & df['City'].isin(city)]
elif region and city :
    filtered_df = df[df['Region'].isin(region) & df['City'].isin(city)]
elif region and state :
    filtered_df = df[df['Region'].isin(region) & df['State'].isin(state)]
else:
    filtered_df = df[df["Region"].isin(region) & df["State"].isin(state) & df["City"].isin(city)]

category_df = filtered_df.groupby(by=['Category'],as_index=False)['Sales'].sum()

mapping_df = filtered_df.groupby(['State_id']).agg({'Sales':'sum'}).reset_index()

def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column, locationmode="USA-states",
                               color_continuous_scale=input_color_theme,
                              range_color=(0, max(filtered_df.Sales)),
                               scope="usa",
                               labels={'Sales':'Sales'}
                              )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth

st.markdown('#### Number of Sales based on States')
    
choropleth = make_choropleth(mapping_df, 'State_id', 'Sales', 'Blues')
st.plotly_chart(choropleth, use_container_width=True)


colc1,colc2 = st.columns((2))
with colc1:
    st.subheader("Category by Sales")
    fig = px.bar(category_df, x= 'Category', y ='Sales', text=['${:,.2f}'.format(x) for x in category_df['Sales']],
                 template='seaborn')
    st.plotly_chart(fig,use_container_width=True,height=200)

with colc2:
    st.subheader("Sales by Region")
    fig = px.pie(filtered_df,values='Sales',names='Region',hole=0.5)
    fig.update_traces(text = filtered_df['Region'], textposition ='outside')
    st.plotly_chart(fig,use_container_width=True,height=200)

#Downloadable dataset

cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap='Blues'))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download data",data=csv,file_name="category.csv",mime='text/csv',
                           help="Click here to download the data as CSV")
with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by='Region',as_index=False)['Sales'].sum()
        st.write(region.style.background_gradient(cmap='Oranges'))
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button("Download data",data=csv,file_name="region.csv",mime='text/csv',
                           help="Click here to download the data as CSV")
    
    
filtered_df['month_year'] = filtered_df['Order Date'].dt.to_period('M')
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df['month_year'].dt.strftime('%Y :%b'))['Sales'].sum()).reset_index()
fig2 = px.line(linechart,x='month_year',y ='Sales',labels={'Sales':'Amount'},height=500,width=1000,template='gridon')

st.plotly_chart(fig2,use_container_width=True)

with st.expander('View Date of TimeSeries:'):
    st.write(linechart.T.style.background_gradient(cmap='Blues'))
    csv = linechart.to_csv(index=False).encode('utf-8')
    st.download_button('Download data',data=csv,file_name='timeseries.csv',mime='text/csv')

# teemap region,category,sub-category

st.subheader('Hierarchical view of Sales')    
fig3 = px.treemap(filtered_df,path=['Region','Category','Sub-Category'],values='Sales',hover_data=['Sales'],
                  color='Sub-Category')
fig3.update_layout(width=800,height=650)
st.plotly_chart(fig3,use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Segment with Sales')
    fig = px.pie(filtered_df,values='Sales',names='Segment',template='plotly_dark')
    fig.update_traces(text=filtered_df['Segment'],textposition='inside')
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader('Category with Sales')
    fig = px.pie(filtered_df,values='Sales',names='Category',template='gridon')
    fig.update_traces(text=filtered_df['Category'],textposition='inside')
    st.plotly_chart(fig,use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")

with st.expander("Summary_Table"):
    df_sample = df[0:5][['Region','State','City','Category','Sales','Profit','Quantity']]
    fig = ff.create_table(df_sample,colorscale='Cividis')
    st.plotly_chart(fig,use_container_width=True)

    st.markdown('Month wise sub-Category Table')
    filtered_df['month'] = filtered_df['Order Date'].dt.month_name()
    sub_category_Year = pd.pivot_table(data=filtered_df, values= 'Sales',index=['Sub-Category'],columns='month')
    st.write(sub_category_Year.style.background_gradient(cmap='Blues'))

#scatter plot

data1 = px.scatter(filtered_df,x = 'Sales',y='Profit', size='Quantity')
data1['layout'].update(title='Relationship between Sales and Profits',
                           titlefont=dict(size=20),xaxis=dict(title='Sales',titlefont=dict(size=18)),
                           yaxis=dict(title='Prodit',titlefont=dict(size=18)))
st.plotly_chart(data1,use_container_width=True)    

with st.expander('Vide Data'):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap='Oranges'))

#download the entire dataset:

csv = df.to_csv(index=False).encode('utf-8')
st.download_button('Download Data',data=csv,file_name='superstore_data.csv',mime='text/csv',
                           help="Click here to download the data as CSV")