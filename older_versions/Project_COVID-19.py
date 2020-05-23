#!/usr/bin/env python
# coding: utf-8
<script>
  function code_toggle() {
    if (code_shown){
      $('div.input').hide('500');
      $('#toggleButton').val('Show Code')
    } else {
      $('div.input').show('500');
      $('#toggleButton').val('Hide Code')
    }
    code_shown = !code_shown
  }

  $( document ).ready(function(){
    code_shown=false;
    $('div.input').hide()
  });
</script>
<form action="javascript:code_toggle()"><input type="submit" id="toggleButton" value="Show Code"></form>
# ## REAL-TIME COVID-19: DATA ANALYSIS & VISUALIZATION
# 
# #### Bernardo Carraro Detanico
# #### 01 April 2020
# 
# The outbreak of the new coronavirus disease (COVID-19), caused by the severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2), has quickly become a global health emergency.
# 
# > <li> On 31 December 2019, the WHO (World Health Organization) China Country Office was informed of cases of unknown aetiology pneumonia (unknown cause) detected in Wuhan City, Hubei Province of China. </li>
# > <li> The Chinese authorities identified a new type of coronavirus, which was isolated on 7 January 2020.</li>
# > <li> On 30 January the WHO declared that the outbreak of 2019-nCoV constitutes a Public Health Emergency of International Concern.</li>
# 
# All coronaviruses that have caused diseases to humans have had animal origins, generally in bats, rodents, civet cats and dromedary camels. WHO informs that the COVID-19 most probably has its ecological reservoir in bats, and the transmission to humans has likely occurred through an intermediate animal host – a domestic animal, a wild animal or a domesticated wild animal which has not yet been identified.
# 
# The current project collects the coronavirus disease (COVID-19) data from Johns Hopkins University Center for Systems Science and Engineering (JHU CSSE) repository (https://github.com/CSSEGISandData/COVID-19). The repository is updated daily and contains time series data on **confirmed cases**, **deaths** and **recovered cases**.

# In[1]:


#Libraries:
import pandas as pd
import numpy as np
import datetime as dt
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# In[2]:


# Importing data from Github:
url1 = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
df_conf = pd.read_csv(url1)

url2 = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
df_deaths = pd.read_csv(url2)


# In[3]:


#EDA
df_conf.dtypes
df_deaths.dtypes

# Finding the null values
df_conf.isnull().sum().sort_values(ascending=False)
df_deaths.isnull().sum().sort_values(ascending=False)

#Deleting the 'Province/State' Column
df_conf = df_conf.drop('Province/State', 1)
df_deaths = df_deaths.drop('Province/State', 1)

# Dropping column with NaN
df_conf = df_conf.dropna(axis = 1)
df_deaths = df_deaths.dropna(axis = 1)

# Group by 'Country/Region' column:
df_conf_grouped = df_conf.groupby('Country/Region').sum()
df_deaths_grouped = df_deaths.groupby('Country/Region').sum()

# Change the display precision option in Pandas
pd.set_option('precision', 0)


# ### 1. Geographic distribution of cases worldwide

# In[4]:


#Confirmed cases over the days
df_conf_melt = df_conf.melt(['Country/Region', 'Lat', 'Long'], var_name='Date', value_name='Confirmed')
df_conf_melt['Date'] = pd.to_datetime(df_conf_melt['Date']).dt.date
df_conf_melt = df_conf_melt.sort_values(by=['Date'])
df_conf_melt['Date'] = df_conf_melt['Date'].astype(str)
df_conf_melt['Confirmed'] = df_conf_melt['Confirmed'].replace(np.nan, 0)

fig = px.scatter_geo(df_conf_melt, lat="Lat", lon="Long", color="Country/Region",
                     hover_name="Country/Region", size="Confirmed", projection="natural earth")

fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
fig.show()


# ### 2. Total number of cases and deaths over time

# In[5]:


df_conf_total = pd.DataFrame(df_conf.sum(axis=0).drop(index=[
    'Country/Region','Lat','Long'])).reset_index().rename(columns={'index': 'Date', 0: 'Total Confirmed'})
df_deaths_total = pd.DataFrame(df_deaths.sum(axis=0).drop(index=[
    'Country/Region','Lat','Long'])).reset_index().rename(columns={'index': 'Date', 0: 'Total Deaths'})

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_conf_total['Date'], y=df_conf_total['Total Confirmed'],
                         mode='lines+markers', line_shape='spline', name="confirmed cases", fill='tozeroy'))
fig.add_trace(go.Scatter(x=df_deaths_total['Date'], y=df_deaths_total['Total Deaths'],
                         mode='lines+markers', line_shape='spline', name="deaths", fill='tozeroy'))
fig.add_annotation(
            x=df_conf_total.iloc[-1,0],
            y=df_conf_total.iloc[-1,1],
            text=df_conf_total.iloc[-1,1])
fig.add_annotation(
            x=df_deaths_total.iloc[-1,0],
            y=df_deaths_total.iloc[-1,1],
            text=df_deaths_total.iloc[-1,1])
fig.update_layout(legend=dict(
        x=0,
        y=1.0,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'
        ), yaxis_title="Number",
                 margin=dict(l=20, r=20, t=20, b=20))
fig.show()


# ### 3. Fatality rate
# 
# The **fatality rate** was defined as number of deaths in people who tested positive for SARS-CoV-2 divided by number of SARS-CoV-2 cases. The fatality rate typically is used as a **measure of disease severity** and is related to patients' characteristics, health care system features, and cultural and socioeconomic factors, among others.

# In[6]:


df_deaths_melt = df_deaths.melt(['Country/Region', 'Lat', 'Long'], var_name='Date', value_name='Deaths')
df_deaths_melt = df_deaths_melt.drop(['Country/Region', 'Lat', 'Long'], 1)
df_deaths_melt_g = df_deaths_melt.groupby('Date').sum()
df_deaths_melt_g.reset_index(level=0, inplace=True)
df_deaths_melt_g['Date'] = pd.to_datetime(df_deaths_melt_g['Date'])
df_deaths_melt_g = df_deaths_melt_g.sort_values(by=['Date'])
df_deaths_melt_g['deaths per day'] = df_deaths_melt_g['Deaths'].diff().fillna(17)

df_conf_melt = df_conf.melt(['Country/Region', 'Lat', 'Long'], var_name='Date', value_name='Confirmed')
df_conf_melt = df_conf_melt.drop(['Country/Region', 'Lat', 'Long'], 1)
df_conf_melt_g = df_conf_melt.groupby('Date').sum()
df_conf_melt_g.reset_index(level=0, inplace=True)
df_conf_melt_g['Date'] = pd.to_datetime(df_conf_melt_g['Date'])
df_conf_melt_g = df_conf_melt_g.sort_values(by=['Date'])
df_conf_melt_g.rename(columns = {'Date':'Date1'}, inplace = True)
df_conf_melt_g['confirmed per day'] = df_conf_melt_g['Confirmed'].diff().fillna(555)

join_melts = pd.concat([df_conf_melt_g, df_deaths_melt_g], axis=1).fillna(0)
join_melts['Fatality rate (%)'] = (join_melts['Deaths'] / join_melts['Confirmed'])*100
join_melts['Date'] = join_melts['Date'].dt.strftime('%m/%d/%y')

fig = go.Figure()
fig.add_trace(go.Scatter(x=join_melts['Date'], y=join_melts['Fatality rate (%)'],
                         mode='lines+markers', line_shape='spline', name="Fatality rate (%)", line=dict(color='#00cc96')))
fig.add_annotation(
            x=join_melts.iloc[-1,-4],
            y=join_melts.iloc[-1,-1],
            text=round(join_melts.iloc[-1,-1],2))
fig.update_layout(yaxis_title="Fatality rate (%)", margin=dict(l=20, r=20, t=20, b=20))
fig.show()


# ### 4. Total number of confirmed cases, deaths and fatality rate for the 15 most affected countries

# In[7]:


df_conf_grouped = df_conf.groupby('Country/Region').sum()
df_conf_grouped['Total Confirmed'] = df_conf_grouped.iloc[:,-1]

df_deaths_grouped = df_deaths.groupby('Country/Region').sum()
df_deaths_grouped['Total Deaths'] = df_deaths_grouped.iloc[:,-1]

df_merge = df_conf_grouped.merge(df_deaths_grouped, how='inner', on='Country/Region')
df_merge.reset_index(level=0, inplace=True)
df_merge.sort_values(by=['Total Deaths'], inplace=True, ascending=False)
df_merge = df_merge.head(15)

fig = make_subplots(rows=1, cols=3, subplot_titles=("Confirmed cases (nº)", "Deaths (nº)", "Fatality rate (%)"))
fig.add_trace(
    go.Bar(x=df_merge['Country/Region'], y=df_merge['Total Confirmed']),
    row=1, col=1)
fig.add_trace(
    go.Bar(x=df_merge['Country/Region'], y=df_merge['Total Deaths']),
    row=1, col=2)
fig.add_trace(
    go.Bar(x=df_merge['Country/Region'], y=(df_merge['Total Deaths'] / df_merge['Total Confirmed'])*100),
    row=1, col=3)
fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
fig.show()


# ### 5. Daily new cases and deaths

# In[8]:


df_conf_deaths = join_melts.drop(['Confirmed', 'Date1', 'Deaths', 'Fatality rate (%)'], 1)
df_conf_deaths_m = df_conf_deaths.melt('Date', var_name='cols',  value_name='vals')

# Bar Plot - Cases and deaths per day
fig = px.bar(df_conf_deaths_m, x="Date", y="vals", color='cols', barmode='group',
             height=400)
fig.update_layout(legend=dict(
        x=0,
        y=1.0,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'
        ), barmode='group', xaxis_tickangle=-60, bargap=0.0,
        bargroupgap=0.0, yaxis_title="Number", margin=dict(l=20, r=20, t=20, b=20), legend_title='')
fig.show()


# ### 6. Daily new cases in the last 10 days for the 14 most affected countries + China

# In[9]:


df_conf_grouped = df_conf.groupby('Country/Region').sum()
df_conf_grouped.drop(df_conf_grouped.iloc[:, 0:2], inplace = True, axis = 1) 
df_conf_grouped = df_conf_grouped.diff(axis=1)
df_conf_grouped.reset_index(level=0, inplace=True)
df_conf_grouped.drop(df_conf_grouped.iloc[:, 1:-10], inplace = True, axis = 1)
df_conf_grouped = df_conf_grouped.sort_values(by=df_conf_grouped.columns[-1], ascending=False)
df_conf_grouped['Total Cases'] = df_conf_grouped.sum(axis=1)
df_china = df_conf_grouped[df_conf_grouped['Country/Region']=='China']
df_conf_grouped = df_conf_grouped.head(14)
df_total = pd.concat([df_china, df_conf_grouped], ignore_index=True)
cols = df_total.columns[1:-1]
df_total.style.background_gradient(subset=cols, cmap='Blues', axis=1)


# ### 7. Daily new cases for the 14 most affected countries + China

# In[10]:


df_conf_grouped = df_conf.groupby('Country/Region').sum()
df_conf_grouped.drop(df_conf_grouped.iloc[:, 0:2], inplace = True, axis = 1) 
df_conf_grouped = df_conf_grouped.diff(axis=1)
df_conf_grouped.reset_index(level=0, inplace=True)
df_conf_grouped.drop(df_conf_grouped.iloc[:, 1:1], inplace = True, axis = 1)
df_conf_grouped = df_conf_grouped.sort_values(by=df_conf_grouped.columns[-1], ascending=False)
df_conf_grouped.set_index('Country/Region', inplace = True)
df_conf_grouped = df_conf_grouped.fillna(0)
df_china = df_conf_grouped[df_conf_grouped.index=='China']
df_conf_grouped = df_conf_grouped.head(14)
df_total = pd.concat([df_china, df_conf_grouped], ignore_index=False)
df_conf_t = df_total.T

plot_rows=5
plot_cols=3
z = plot_rows * plot_cols
fig = make_subplots(rows=plot_rows, cols=plot_cols, subplot_titles=(df_conf_t.columns[0:z]), shared_xaxes=True, 
                   vertical_spacing = 0.05)
x = 0
for i in range(1, plot_rows + 1):
    for j in range(1, plot_cols + 1):
        #print(str(i)+ ', ' + str(j))
        fig.add_trace(go.Bar(name = df_conf_t.columns[x], x=df_conf_t.index, y=df_conf_t[df_conf_t.columns[x]].values, 
                                 ), 
                     row=i,
                     col=j)

        x=x+1
fig.update_layout(showlegend=False, height=900, width=980, margin=dict(l=20, r=20, t=20, b=20))
fig.show()


# ### 8. Daily deaths in the last 10 days for the 14 most affected countries + China

# In[11]:


# Deaths in the last 7 days by country (top 15) - Table
df_deaths_grouped = df_deaths.groupby('Country/Region').sum()
df_deaths_grouped.drop(df_deaths_grouped.iloc[:, 0:2], inplace = True, axis = 1) 
df_deaths_grouped = df_deaths_grouped.diff(axis=1)
df_deaths_grouped.reset_index(level=0, inplace=True)
df_deaths_grouped.drop(df_deaths_grouped.iloc[:, 1:-10,], inplace = True, axis = 1)
df_deaths_grouped = df_deaths_grouped.sort_values(by=df_deaths_grouped.columns[-1], ascending=False)
df_deaths_grouped['Total Deaths'] = df_deaths_grouped.sum(axis=1)
df_china = df_deaths_grouped[df_deaths_grouped['Country/Region']=='China']
df_deaths_grouped = df_deaths_grouped.head(14)
df_total = pd.concat([df_china, df_deaths_grouped], ignore_index=True)
cols = df_deaths_grouped.columns[1:-1]
df_total.style.background_gradient(subset=cols, cmap='Reds', axis=1)


# ### 9.Daily deaths for the 14 most affected countries + China

# In[12]:


df_deaths_grouped = df_deaths.groupby('Country/Region').sum()
df_deaths_grouped.drop(df_deaths_grouped.iloc[:, 0:2], inplace = True, axis = 1) 
df_deaths_grouped = df_deaths_grouped.diff(axis=1)
df_deaths_grouped.reset_index(level=0, inplace=True)
df_deaths_grouped.drop(df_deaths_grouped.iloc[:, 1:1], inplace = True, axis = 1)
df_deaths_grouped = df_deaths_grouped.sort_values(by=df_deaths_grouped.columns[-1], ascending=False)
df_deaths_grouped.set_index('Country/Region', inplace = True)
df_deaths_grouped = df_deaths_grouped.fillna(0)
df_china = df_deaths_grouped[df_deaths_grouped.index=='China']
df_deaths_grouped = df_deaths_grouped.head(14)
df_total = pd.concat([df_china, df_deaths_grouped], ignore_index=False)
df_deaths_t = df_total.T

plot_rows=5
plot_cols=3
z = plot_rows * plot_cols
fig = make_subplots(rows=plot_rows, cols=plot_cols, subplot_titles=(df_deaths_t.columns[0:z]), shared_xaxes=True, 
                   vertical_spacing = 0.05)
x = 0
for i in range(1, plot_rows + 1):
    for j in range(1, plot_cols + 1):
        #print(str(i)+ ', ' + str(j))
        fig.add_trace(go.Bar(name = df_deaths_t.columns[x], x=df_deaths_t.index, y=df_deaths_t[df_deaths_t.columns[x]].values, 
                                 ), 
                     row=i,
                     col=j)

        x=x+1
fig.update_layout(showlegend=False, height=900, width=980, margin=dict(l=20, r=20, t=20, b=20))
fig.show()


# In[ ]:




