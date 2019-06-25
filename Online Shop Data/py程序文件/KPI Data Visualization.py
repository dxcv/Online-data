#!/usr/bin/env python
# coding: utf-8

# ### 1、Import data

# In[10]:


import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")


# ### 2、总体运营指标

# ### 2.1 订单产生效率指标

# In[456]:


orders=pd.read_csv(r"data/orders.csv")
orders['订单处理时间']=pd.to_datetime(orders['订单处理时间'])
orders['年']=orders['订单处理时间'].dt.year
orders['月']=orders['订单处理时间'].dt.month
orders['年月']=orders['年'].map(str)+'-'+orders['月'].map(str)


# voided 无效，refunded 退款 partially_refunded 部分退款 pending 待定 paid 支付

# In[457]:


paid=orders.loc[orders['物流状态']=='fulfilled']  
# 每日订单量 （物流完成的订单才算订单业绩）
paid_num=paid.groupby(['订单创建时间'])['支付状态'].count()
from pyecharts import Line,Bar,Grid
grid=Grid()
bar=Bar("每天订单量")
bar.add("数量",paid_num.index,paid_num.values,label_color=['#404a59'],xaxis_rotate=40,legend_pos ='center',legend_top ='top',is_datazoom_show=True,is_more_utils=True)
grid.add(bar,grid_bottom='25%')
grid.render(path=r"KPI/orders/日订单量.html")


# In[458]:


# 月订单量
month_paid=paid.groupby(['年','月'])['支付状态'].count().reset_index()
month_paid['年月']=month_paid['年'].map(str)+'-'+month_paid['月'].map(str)
line0=Line('月订单量')
line0.add('订单量/次',month_paid['年月'].values,month_paid['支付状态'].values,mark_point=['max','min'],label_color=['#404a59'],xaxis_rotate=40)
line0.render(path=r'KPI/orders/月订单量.html')


# In[459]:


# 月订单同比及订单环比
num_month=paid.groupby(['年','月'])['订单创建时间'].count()
num_month=num_month.reset_index()
num_month['环比增长量']=num_month['订单创建时间'].diff()
num_month['环比']=(num_month['环比增长量']/(num_month['订单创建时间']+num_month['环比增长量'])).round(2)
# 环比增长：（本期-临近一期）/(临近一期)

num_month['同比增长量']=num_month['订单创建时间'].diff(12)
num_month['同比']=(num_month['同比增长量']/(num_month['订单创建时间']+num_month['同比增长量'])).round(2)
# 同比增长：（本期-同期）/同期

num_month['年月']=num_month['年'].map(str)+'-'+num_month['月'].map(str)
# num_month['年月']=pd.to_datetime(num_month['年月'])

from pyecharts import Line
line1=Line("月订单环比")
line1.add('环比',num_month['年月'].values,num_month['环比'].values,mark_point=['max','min'],xaxis_rotate=40)
line1.render(path=r'KPI/orders/环比_num.html')

line2=Line("月订单同比")
line2.add('同比',num_month['年月'].values,num_month['同比'].values,mark_point=['max','min'],xaxis_rotate=40)
line2.render(path=r'KPI/orders/同比_num.html')


# ### 2.2  总体销售业绩指标

# In[460]:


transactions=pd.read_csv(r'data/transactions.csv')

# 每月交易成功率
orders_trascation=pd.merge(orders,transactions,on='订单id',how='left')
rate_success=orders_trascation.groupby(['年','月','交易状态'])['交易状态'].count().unstack().reset_index().fillna(0)
rate_success['交易成功率']=(rate_success['success']/(rate_success['error']+rate_success['failure']+rate_success['pending']+rate_success['success'])).round(2)
rate_success['年月']=rate_success['年'].map(str)+'-'+rate_success['月'].map(str)
line3=Line('每月交易成功率','交易成功率较为平均，平均值为0.93')
line3.add('成功率',rate_success['年月'].values,rate_success['交易成功率'].values,mark_line=['average'],label_color=['#404a59'],xaxis_rotate=40)
line3.render(path=r'KPI/orders/交易成功率.html')


# In[461]:


# 每月成功交易金额
amount=((orders_trascation.groupby(['年','月','交易状态'])['交易金额'].sum()).round(2)).reset_index()
amount=amount.loc[amount['交易状态']=='success']
amount['年月']=amount['年'].map(str)+'-'+amount['月'].map(str)
line4=Line('每月成功交易金额')
line4.add('金额/美元',amount['年月'].values,amount['交易金额'].values,mark_line=['average'],xaxis_rotate=40)
line4.render(path=r'KPI/orders/每月成功交易金额.html')


# In[462]:


# 客单价：每一个顾客平均购买商品的金额，客单价也即是平均交易金额。
order_item=pd.read_csv(r"data/orders_items.csv")
order_tra_item=pd.merge(orders_trascation,order_item,on='订单id',how='left')
num_item=order_tra_item.groupby(['年','月'])['订购数量'].sum().reset_index()
per_sales=pd.merge(amount,num_item,on=['年','月'],how='inner')
per_sales['客单价']=(per_sales['交易金额']/per_sales['订购数量']).round(2)

from pyecharts import Bar,Overlap
line5=Line('每月销售额和客单价')
line5.add('客单价/美元',per_sales['年月'].values,per_sales['客单价'].values,mark_line=['average'],xaxis_rotate=40)

bar1=Bar()
bar1.add('交易量',per_sales['年月'].values,per_sales['订购数量'].values)  ## 每月销售量（交易成功的订购数量）

overlap=Overlap()
overlap.add(line5)
overlap.add(bar1,is_add_yaxis=True,yaxis_index=1)
overlap.render(path=r'KPI/orders/每月销售额和客单价.html')


# ### 2.3 产品类别指标

# In[463]:


# 畅销商品的产品类别
num_product=order_tra_item.groupby(['年','月','产品名称'])['订购数量'].sum().reset_index()
num_product=num_product.sort_values(by='订购数量',ascending=False)

product=pd.read_csv(r'data/products.csv')
num_type=pd.merge(num_product,product,on='产品名称',how='left') 
num_type=num_type.groupby(['产品类别'])['订购数量'].sum().reset_index()
num_type['产品类别'][num_type['订购数量']<1500]='other'
num_type=num_type.groupby(['产品类别'])['订购数量'].sum().reset_index()
num_type=num_type.sort_values(by='订购数量',ascending=False).reset_index()

from pyecharts import Pie
pie=Pie('三年交易产品类别数量对比')
pie.add("",num_type['产品类别'].values,num_type['订购数量'].values,radius=[40,75],is_label_show=True,legend_orient='vertical',legend_pos='bottom')
pie.render(path=r"KPI/orders/三年交易产品类别量.html")


# In[464]:


# 商品年平均价格对比
price=order_tra_item.groupby(['产品名称','年','月'])['价格'].mean().reset_index()
price=pd.merge(price,product,on='产品名称',how='left') 
mean_price=price.groupby(['产品类别','年'])['价格'].mean().unstack().fillna(0).round(2)
mean_price=mean_price.reset_index()
line6=Line('商品年平均价格对比')
line6.add("2016年",mean_price['产品类别'].values,mean_price[2016].values)
line6.add("2017年",mean_price['产品类别'].values,mean_price[2017].values)
line6.add("2018年",mean_price['产品类别'].values,mean_price[2018].values,xaxis_rotate=40,legend_pos ='center',
          legend_top ='top',is_datazoom_show=True,is_more_utils=True)
line6.render(path=r'KPI/orders/商品年平均价格对比.html')


# In[465]:


# 各月份商品价格弹性系数 价格弹性（price elasticity）是指某一种产品销量发生变化的百分比与其价格变化百分比之间的比率
order_tra_item1=order_tra_item.loc[order_tra_item['月']>7]
num_sale=order_tra_item1.groupby(['产品名称','年'])['订购数量'].sum().reset_index()
num_sale=pd.merge(num_sale,product,on='产品名称',how='left') 
sum_sale=num_sale.groupby(['产品类别','年'])['订购数量'].sum().unstack().fillna(0).reset_index()
price_sale=pd.merge(mean_price,sum_sale,on='产品类别',how='inner')
price_sale['价格变化率']=(price_sale['2017_x']-price_sale['2016_x'])/price_sale['2016_x']
price_sale['销量变化率']=(price_sale['2017_y']-price_sale['2016_y'])/price_sale['2016_y']
price_sale['价格弹性系数']=price_sale['销量变化率']/price_sale['价格变化率']
#bar2=Bar('商品价格弹性系数')
#bar2.add('系数',price_sale['产品类别'].values,price_sale['价格弹性系数'].values,xaxis_rotate=40)
#bar2


# ### 2.4 用户消费质量（复购率和回购率指标）

# In[466]:


orders=pd.read_csv(r"data/orders.csv")
orders.drop(['Unnamed: 0'],axis=1,inplace=True)
#print(orders['支付状态'].unique())
orders["订单创建时间"]=pd.to_datetime(orders['订单创建时间'])
orders['年']=orders['订单创建时间'].dt.year
orders['月']=orders['订单创建时间'].dt.month
orders['年月']=orders['年'].map(str)+'-'+orders['月'].map(str)


# In[467]:


# 复购率：在某时间窗口内消费两次及以上的用户在总消费用户中的占比
customer=orders.groupby(['年','月','用户id'])['订单id'].count().reset_index()
all_customer=customer.groupby(['年','月'])['用户id'].count().reset_index()
fugou_customer=customer.loc[customer['订单id']>=2].groupby(['年','月'])['用户id'].count().reset_index()
fugou_rate=pd.merge(all_customer,fugou_customer,on=['年','月'],how='inner')
fugou_rate['复购率']=(fugou_rate['用户id_x']/fugou_rate['用户id_y']).round(2)
fugou_rate.rename(columns={'用户id_x':'消费人数', '用户id_y':'二次消费以上人数'}, inplace = True)
fugou_rate['年月']=fugou_rate['年'].map(str)+'-'+fugou_rate['月'].map(str)

line7=Line('每月用户复购率')
line7.add('百分比(%)',fugou_rate['年月'].values,fugou_rate['复购率'].values,mark_point=['max','min'],xaxis_rotate=40)
line7.render(path=r'KPI/orders/每月用户复购率.html')


# In[474]:


line8=Line('每月消费和二次消费以上用户人数','二次消费客户很稳定，曲线趋近直线，大概在58人左右。这部分的客户是重点维护的优质客户')
line8.add('消费人数',fugou_rate['年月'].values,fugou_rate['消费人数'].values,xaxis_rotate=40,is_fill = True,line_opacity = 0.2,area_opacity = 0.4, symbol = None)
line8.add('复购人数',fugou_rate['年月'].values,fugou_rate['二次消费以上人数'].values,xaxis_rotate=40,
          is_fill = True,line_opacity = 0.2,area_opacity = 0.4, symbol = None,legend_orient='vertical',legend_pos='right')
line8.render(path=r'KPI/orders/每月消费和二次消费以上用户人数.html')
line8


# In[470]:


# 回购率：某一个时间窗口内消费的用户，在下一个时间窗口依旧消费的占比
huigou_rate=orders.groupby(['用户id','年','月'])['订单id'].count().reset_index()
huigou_rate['年月']=huigou_rate['年'].map(str)+'-'+huigou_rate['月'].map(str)
huigou_rate=huigou_rate.groupby(['用户id','年月'])['订单id'].count().unstack().fillna(0)  # 转化数据，将购买过的为1，没有购买的为0
#huigou_rate=huigou_rate.applymap(lambda x: 1 if x>0 else 0)
#huigou_rate=huigou_rate.reset_index()
#huigou_rate.head()

def pur_return(data):
    status=[]
    for i in range(data.shape[0]-1):
        if data.iloc[i]==1:
            if data.iloc[i+1]==1:
                status.append(1)
            if data.iloc[i+1]==0:
                status.append(0)
        else:
            status.append(np.NaN)
    return pd.Series(status)

huigou_rate_return=huigou_rate.apply(pur_return,axis=1)

columns=huigou_rate.columns
columns=np.delete(columns,-1)
huigou_rate_return.columns=columns
huigou=huigou_rate_return.sum()/huigou_rate_return.count()

line12=Line('每月用户回购率')
line12.add('百分比(%)',huigou.index,huigou.values,mark_point=['max','min'],xaxis_rotate=40)
line12.render(path=r'KPI/orders/每月用户回购率.html')


# In[481]:


num_huigou=huigou_rate_return.sum()
num_orders=huigou_rate_return.count()

line13=Line('每月消费和回购人数')
line13.add('回购人数',num_huigou.index,num_huigou.values,xaxis_rotate=40,is_fill = True,line_opacity = 0.2,area_opacity = 0.4, symbol = None)
line13.add('消费人数',num_orders.index,num_orders.values,xaxis_rotate=40,is_fill = True,line_opacity = 0.2,area_opacity = 0.4, symbol = None)
line13.render(path=r'KPI/orders/每月消费和回购人数.html')
line13


# 回购人数较为稳定，但消费人数偶尔会出现波动，可能是营销者淡季的原因，但是这部分回购用户的消费行为也较为稳定，与每月复购用户有一定的重合，是属于优质用户

# ### 2.5  用户消费金额分布

# In[30]:


# 客户消费金额分布图
consumption=paid.groupby(['用户id'])['总售价'].sum().reset_index()
normal=consumption.loc[consumption['总售价']<=2000]
bins=[0,50,100,150,200,300,350,400,450,500,550,600,650,700,750,800,850,900,950,1000,2000]
normal['金额分组']=pd.cut(normal['总售价'],bins,right=False)
con_fenzu=normal.groupby(['金额分组'])['用户id'].count().reset_index()
bar3=Bar('用户消费金额分布图','大部分用户的消费能力确实不高，平均消费金额为726美元左右')
bar3.add('次数',con_fenzu['金额分组'].values,con_fenzu['用户id'].values,mark_line=['average'],xaxis_rotate=40)
bar3.render(path=r'KPI/orders/用户消费金额分布图.html')


# In[31]:


# 高消费用户支付状态  总消费>2000
abnormal=consumption.loc[consumption['总售价']>2000]
abnormal=pd.merge(abnormal,orders,on='用户id',how='left')
zifu_state=abnormal.groupby(['用户id','支付状态'])['订单id'].count().unstack().reset_index()

bar4=Bar('高消费用户支付状态')
bar4.add('paid',zifu_state['用户id'].values,zifu_state['paid'].values,is_stack=True)
bar4.add('partially_refunded',zifu_state['用户id'].values,zifu_state['partially_refunded'].values,is_stack=True)
bar4.add('refunded',zifu_state['用户id'].values,zifu_state['refunded'].values,is_stack=True)
bar4.render(path=r'KPI/orders/高消费用户支付状态.html')


# ### 2.6 用户消费行为分析

# In[220]:


paid=orders.loc[orders['物流状态']=='fulfilled']  
paid['年月']=pd.to_datetime(paid['年月'])
# 第一次消费客户
first_order=paid.groupby(['用户id'])['年月'].min().value_counts().sort_index()

# 用户最后一次消费
last_order=paid.groupby(['用户id'])['年月'].max().value_counts().sort_index()

line9=Line('首次订购和最后一次订购人数对比')
line9.add('首次订购人数',first_order.index,first_order.values,
          is_fill = True,line_opacity = 0.2,area_opacity = 0.4, symbol = None)
line9.add('最后一次订购',last_order.index,last_order.values,
         is_fill = True, line_color = '#000', area_opacity = 0.3,is_smooth = True,xaxis_rotate=40,legend_orient='vertical',legend_pos='right')
line9.render(path=r'KPI/orders/首次订购和最后一次订购人数对比.html')
line9


# 首次订购和最后一次订购的消费者主要集中在2016年。说明很多客户订购一次就不再订购。随着时间的增长，最后订购人数要大于首次订购人数，呈现消费者流的情况，消费者的忠诚度在慢慢下降。

# In[270]:


# 用户生命周期：第一次消费到最后一次消费为整个用户生命
first_last_order=paid.groupby(['用户id'])['订单处理时间'].agg(['min','max']).reset_index()
first_last_order['生命周期']=(first_last_order['max']-first_last_order['min'])/np.timedelta64(1,'D')
print(first_last_order.describe())
zhouqi=first_last_order.groupby(['生命周期'])['用户id'].count().reset_index()
zhouqi=zhouqi.drop([0])
line10=Line('二次消费以上生命周期人数分布图')
line10.add('天数/天',zhouqi['生命周期'].values,zhouqi['用户id'].values)
line10.render(path=r'KPI/orders/生命周期人数分布图.html')
line10


# 所有用户的平均生命周期为36天，中位数为0天，也就是超过一半的用户只消费了一次,这些用户是低质量用户。最大生命周期为576天，相当于这个数据集的总天数，说明该用户从开始到最后都有消费意愿的高质量用户

# In[173]:


# 只消费一次占比
user=orders.groupby(['用户id'])['订单处理时间'].agg(['min','max'])
num_consumption=(user['min']==user['max']).value_counts()
Percent=round(num_consumption/num_consumption.sum(),4)
from pyecharts import Liquid
liquid=Liquid('只消费一次的消费者占比')
liquid.add('',Percent,is_liquid_outline_show=False)
liquid.render(path=r'KPI/orders/只消费一次的消费者占比.html')
liquid


# ##### 用户分层

# RFM模式中：
# 
# R表示客户购买的时间有多远，
# 
# F(Frequency)表示客户在时间内购买的次数，
# 
# M（Monetary）表示客户在时间内购买的金额

# In[214]:


# 用户分层 ：总售价：总消费金额；订购数量：总消费产品数；订单处理时间：最近一次消费时间
feature_user=order_tra_item.pivot_table(index='用户id',values=['订购数量','总售价','订单处理时间'],
                                       aggfunc={'订购数量':'sum','总售价':'sum','订单处理时间':'max'})

# 用户最后消费距现在的时间
feature_user=feature_user.reset_index()
feature_user['当前时间']=orders['订单处理时间'].max()
feature_user['R']=(feature_user['当前时间']-feature_user['订单处理时间'])/np.timedelta64(1,'D')
#-(rfm.order_dt - rfm.order_dt.max())结果为时间类型，将时间格式转化为整数或者浮点数的形式，可以除以单位‘D’，也可以用astype转化

feature_user.rename(columns={'订购数量':'F','总售价':'M'},inplace=True)
feature_user.head()

def feature_func(x):
    level=x.apply(lambda x:'1' if x>0 else '0')
    label=level.R+level.F+level.M
    d={
        '111':'重要价值客户',
        '011':'重要保持客户',
        '101':'重要挽留客户',
        '001':'重要发展客户',
        '110':'一般价值客户',
        '010':'一般保持客户',
        '100':'一般挽留客户',
        '000':'一般发展客户'
    }
    result = d[label]
    return result
    
feature_user['label'] = feature_user[['R','F','M']].apply(lambda x : x - x.mean()).apply(feature_func,axis = 1)
feature_user.head()


# In[227]:


feature_user.groupby(['label'])['M','F','R'].sum().reset_index()


# 从客户消费累计金额中看出，重要保持的客户累计消费金额最高

# In[271]:


feature_user.groupby(['label'])['M','F','R'].count().reset_index()


# 一般挽留客户人数第一，一般发展客户人数第二

# In[280]:


from pyecharts import Scatter
important=feature_user.loc[feature_user['label']=='重要保持客户']
unimportant=feature_user.loc[feature_user['label']!='重要保持客户']
scatter=Scatter('消费者画像','横坐标为购买次数，纵坐标为购买间隔')
scatter.add('重要保持客户',important['F'].values,important['R'].values)
scatter.add('非重要保持客户',unimportant['F'].values,unimportant['R'].values)
scatter.render(path=r'KPI/orders/消费者画像.html')


# 从RFM分层可知，大部分用户为重要保持客户

# ### 2.8  用户网页转化量

# In[283]:


traffic=pd.read_csv(r'data/traffic.csv')
traffic['日期']=pd.to_datetime(traffic['日期'])
traffic['年']=traffic['日期'].dt.year
traffic['月']=traffic['日期'].dt.month


# In[303]:


pv=traffic.groupby(['年','月'])['pv','浏览用户数'].sum().reset_index()
pv['年月']=pv['年'].map(str)+'-'+pv['月'].map(str)

line11=Line('每月页面访问量及访客数量',)
line11.add('PV量',pv['年月'].values,pv['pv'].values,mark_point=['max','min'],xaxis_rotate=40)
line11.add('UV量',pv['年月'].values,pv['浏览用户数'].values,mark_point=['max','min'],xaxis_rotate=40)
line11.render(path=r'KPI/orders/每月页面访问量.html')

