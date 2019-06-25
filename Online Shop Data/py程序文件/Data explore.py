#!/usr/bin/env python
# coding: utf-8

# ### 1、Connect Mysql Database

# In[7]:


import pandas as pd
import numpy as np
import pymysql
conn=pymysql.connect(host='127.0.0.1',user='root',passwd='root123',db='test_data',charset='utf8')
sql_query1="select * from customers "
sql_query2="select * from orders "
sql_query3="select * from orders_items "
sql_query4="select * from products "
sql_query5="select * from products_skus "
sql_query6="select * from traffic"
sql_query7="select * from transactions "

customers=pd.read_sql(sql_query1,con=conn)
orders=pd.read_sql(sql_query2,con=conn)
orders_items=pd.read_sql(sql_query3,con=conn)
products=pd.read_sql(sql_query4,con=conn)
products_skus=pd.read_sql(sql_query5,con=conn)
traffic=pd.read_sql(sql_query6,con=conn)
transactions=pd.read_sql(sql_query7,con=conn)


# ### 2、Data Information

# In[8]:


customers.columns=[['用户id','用户名','注册时间']]
print(customers.info())
print(customers['注册时间'].max())
customers.describe()


# In[9]:


orders_items.columns=[['订单物品id','订单id','产品id','产品分类','sku id','sku 名称',
                      '产品名称','物流状态','价格','订购数量']]
print(orders_items.info())
orders_items[['订单物品id','订单id','产品id','产品分类','sku id','sku 名称','产品名称','物流状态']].describe()


# In[10]:


orders.columns=[['订单id','订单创建时间','订单关闭时间','订单取消时间','用户id','支付状态','物流状态',
                 '订单处理时间','实际付款金额','物流价格','扣后价格','总折扣','总售价']]
print(orders.info())
orders.describe()
# orders.head()


# In[11]:


products_skus.columns=[['sku id','产品id','产品类别','sku 产品','sku 创建时间','售价']]
print(products_skus.info())
products_skus[['sku id','产品id','产品类别','sku 产品','sku 创建时间']].describe()


# In[12]:


products.columns=[['产品id','产品名称','产品类别','产品创建时间','产品发布时间']]
print(products.info())
products.head()


# In[13]:


transactions.columns=[['订单id','交易id','父交易id','交易金额','错误码','交易类别','交易状态','交易创建日期']]
print(transactions.info())
transactions['交易状态'].describe()


# In[14]:


traffic.columns=[['id','日期','pv','浏览用户数','产品细节页面pv','结算发起数量','产品添加购物车数量','平均session时长/s']]


# ### 3、Conserve Data

# In[15]:


customers.to_csv(r"data/customers.csv")
orders.to_csv(r"data/orders.csv")
orders_items.to_csv(r"data/orders_items.csv")
products.to_csv(r"data/products.csv")
products_skus.to_csv(r"data/products_sku.csv")
traffic.to_csv(r"data/traffic.csv")
transactions.to_csv(r"data/transactions.csv")


# In[ ]:





# In[ ]:




