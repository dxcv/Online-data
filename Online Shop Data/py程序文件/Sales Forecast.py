#!/usr/bin/env python
# coding: utf-8

# In[44]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fbprophet import Prophet
import warnings
warnings.filterwarnings("ignore")


# In[45]:


df0=pd.read_csv(r"data/orders.csv")
# df1=pd.read_csv(r'data/transactions.csv')
df1=pd.read_csv(r'data/orders_items.csv')
df=pd.merge(df0,df1,on='订单id',how='inner')
df['订单创建时间']=pd.to_datetime(df['订单创建时间'])
df=df.loc[df['支付状态']=='paid']
sales=df.groupby(['订单创建时间'])['订购数量'].sum().reset_index()
sales.rename(columns={'订单创建时间':'ds','订购数量':'y'},inplace=True)
sales.head()


# In[47]:


# 拟合模型
m=Prophet()# Prophet对象进行实例化来拟合模型，任何影响预测过程的设置都将在构造模型时被指定
m.fit(sales)# 利用fit() 代入历史数据集来拟合模型


# In[49]:


# 构建待预测日期数据框，periods=90代表除历史数据的日期外再往后推90天
future=m.make_future_dataframe(periods=90)
future.tail()


# In[93]:


# 预测数据集
forecast=m.predict(future)
forecast[['ds','yhat','yhat_lower','yhat_upper']].tail()
# 预测日期，预测结果值，预测结果上下界


# In[81]:


# 展示预测结果
m.plot(forecast)


# In[82]:


m.plot_components(forecast)


# In[94]:


forecast1=forecast
forecast1['ds']=forecast1['ds'].apply(lambda x: x.strftime('%Y-%m-%d'))


# In[100]:


from pyecharts import Line
import time
line=Line('未来三个月每日预测销售量')
line.add('销售量',forecast1['ds'].tail(90).values,forecast1['yhat'].tail(90).values,xaxis_rotate=40)
line.render(path=r'KPI/predict/未来三个月每天的销售量.html')
line


# In[ ]:





# In[ ]:




