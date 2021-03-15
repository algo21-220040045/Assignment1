
#要计算G-score来选股回测
import numpy as np
import pandas as pd

def dishy(stock = None,hangye = None, shangye = None):#输入股票池，输出行业分布
    res = pd.DataFrame(index = hangye, columns = stock.columns)
    res = res.fillna(0)
    for day in list(stock.columns):
        for s in list(stock[str(day)].dropna()):
            hy = shangye.loc[s,shangye.columns[0]]
            res.loc[hy,day] += 1
    return res  

def dismv(stock = None):
    #市值的日频分布，输出每10分位数
    res = pd.DataFrame(index = data_traday.iloc[1:,0], columns = [0,10,20,30,40,50,60,70,80,90,100])
    for i in range(stock.shape[1]):#对于每个换仓日，找出这次换仓持续时间上用什么股票，然后在该时间段上添加收益率
        timebeg = int(stock.columns[i])
        stocklist = stock[stock.columns[i]].dropna()
        if i == list(range(stock.shape[1]))[-1]:
           timeend = data_traday.iloc[-1,0]
        else:
           timeend = int(stock.columns[i+1])
        starti = data_traday.iloc[:,0].tolist().index(timebeg)#找出起始结束那两天在traday里的位置
        endi = data_traday.iloc[:,0].tolist().index(timeend)
        
        for j in range(starti,endi+1):
            lmv_day = data_lmv[data_traday.iloc[j,0]]
            lmv_day = lmv_day[lmv_day["WIND代码"].isin(stocklist)].set_index('WIND代码').sort_index()  
            res.loc[data_traday.iloc[j,0]] = np.percentile(lmv_day,[0,10,20,30,40,50,60,70,80,90,100])
    return res

def dmaxdd(rt_series = None):#日频的最大回撤   
    rt_series=pd.DataFrame(rt_series).copy()
    rt_series=(rt_series+1).cumprod()
    maxdrawdown=((rt_series.cummax()-rt_series)/rt_series.cummax()).max().squeeze()
    enddate=((rt_series.cummax()-rt_series)/rt_series.cummax()).idxmax(axis=0).squeeze()
    stdate=rt_series.loc[:enddate,:].idxmax(axis=0).squeeze()
    return maxdrawdown,stdate,enddate        
        
def daret(rt_series = None):#日频的复合年收益
    rt_series=pd.DataFrame(rt_series).copy()
    rt_series=(1+rt_series).cumprod()
    ann_rt=(rt_series.iloc[-1,0]/rt_series.iloc[0,0])**(250/rt_series.shape[0])-1
    return ann_rt

def dannstd(rt_series=None):
    rts=pd.DataFrame(rt_series).copy()
    ann_std = float(np.std(rts))*(np.sqrt(250))
    return ann_std

def anmaxdd(rt_series=None):
    anmdd = pd.DataFrame(columns=["最大回撤","开始时间","结束时间"])
    rt_series = rt_series.to_frame()
    rt_series["date"] = rt_series.index.astype(str)
    rt_series["year"] = ''
    for i in range(len(rt_series)):
        rt_series.iloc[i,2] =  rt_series.iloc[i,1][:4]    
    for i in range(2013,2021):
        rt_anual = rt_series[rt_series['year']==str(i)].iloc[:,0]
        anmdd.loc[i] = dmaxdd(rt_anual)
    return anmdd  
 
def anincome(rt_series=None):
    anin = pd.Series()
    rt_series = rt_series.to_frame()
    rt_series["date"] = rt_series.index.astype(str)
    rt_series["year"] = ''
    for i in range(len(rt_series)):
        rt_series.iloc[i,2] =  rt_series.iloc[i,1][:4]    
    for i in range(2013,2022):
        anin.loc[i] = rt_series[rt_series['year']==str(i)].iloc[:,0].add(1).cumprod().iloc[-1]-1
    return anin          

def annstd(rt_series=None):#把期间收益率转换为月收益率
    rts=pd.DataFrame(index=cha_day[3:-1],columns=['月收益率'])
    for i in range(len(rts)):
        if rts.index[i][4:6] == '04':
            rts.iloc[i,0] = (1+rt_series[i])**(1/4)-1
        elif rts.index[i][4:6] == '08':
            rts.iloc[i,0] = (1+rt_series[i])**(1/2)-1
        else:
            rts.iloc[i,0] = (1+rt_series[i])**(1/6)-1
    rtstd=rts.std().squeeze()
    ann_std=rtstd*np.sqrt(12)
    return ann_std

data_traday = pd.read_excel("./数据/交易日期.xlsx")
data_pb = pd.read_excel("./数据/PB.xlsx")
data_roa = pd.read_excel("./数据/ROA.xlsx")
data_roa_var = pd.read_excel("./数据/ROA方差.xlsx")
data_adv = pd.read_excel("./数据/广告费用.xlsx")
data_fcf = pd.read_excel("./数据/经营活动现金流量.xlsx")
data_nei = pd.read_excel("./数据/净利润.xlsx")
data_sw1 = pd.read_excel("./数据/申万一级行业.xlsx").drop(["证券简称"],axis=1).set_index("证券代码",drop=True)
data_sag = pd.read_excel("./数据/销售增长率方差.xlsx")
data_res = pd.read_excel("./数据/研发费用.xlsx")
data_cap = pd.read_excel("./数据/资本支出.xlsx")
data_toa = pd.read_excel("./数据/总资产.xlsx")
data_ret_sw = pd.read_excel("./数据/高估值指数收益率.xlsx").set_index("DateTime")
data_ret_sw = data_ret_sw.iloc[:,0]/100

cha_day = list(pd.read_excel("./数据/换仓日.xlsx").iloc[:,0])

data_cap = data_cap.T.fillna(method = 'ffill').T
data_adv = data_adv.T.fillna(method = 'ffill').T
data_fcf = data_fcf.T.fillna(method = 'ffill').T
data_nei = data_nei.T.fillna(method = 'ffill').T
data_res = data_res.T.fillna(method = 'ffill').T
data_roa = data_roa.T.fillna(method = 'ffill').T
data_sag = data_sag.T.fillna(method = 'ffill').T
data_toa = data_toa.T.fillna(method = 'ffill').T
data_roa_var = data_roa_var.T.fillna(method = 'ffill').T
data_fmi = data_fcf-data_nei
data_fta = data_fcf/data_toa

data_lmv = {}
data_tra = {}
data_hay = {}
data_los = {}
data_ret = {}
data_st = {}
index_numbe=['000300.SH',#沪深300
            '000016.SH',#上证50
            '000905.SH',#中证500
            '000906.SH',#中证800
            '000852.SH',#中证1000
            '881001.WI',#Wind全A
            '000688.SH',#科创50
            '399006.SZ']#创业板指
for i in cha_day:  
    data_hay[i] = pd.read_excel("./数据/满半年/"+ str(i) +".xlsx")
    data_tra[i] = pd.read_excel("./数据/交易状态/"+ str(i) +".xlsx")
    data_los[i] = pd.read_excel("./数据/上财报亏损/"+ str(i) +".xlsx")
    data_st[i] = pd.read_excel("./数据/ST股/"+ str(i) +".xlsx")
    print(str(i) + '完成')
    
con_st = {}
for ind in index_numbe:
    ind_st = {}
    for i in cha_day:  
        ind_st[i] = pd.read_excel("./数据/指数成分股/"+ ind+"-"+str(i) +".xlsx")
        print(ind+"的"+str(i)+"完成！")
    con_st[ind] = ind_st
        

for i in data_traday.iloc[1:,0]:
    data_lmv[i] = pd.read_excel("./数据/流通市值/"+ str(i) +".xlsx")
    data_ret[i] = pd.read_excel("./数据/日收益率/"+ str(i) +".xlsx")
    print(str(i) + '完成')

# =============================================================================
# 筛选出9组股票，分别对应0-8分
# =============================================================================

def stock_selection(pb_per = 75, ind = None,is_tech = 0, index_list = [1,2,3,4,5,6,7,8]):
    '''
    pb_per：是每期股票池中股票的PB的分位数在截面上要高于该值
    is_tech：是否在科技行业中筛选，默认不启用，在所有行业中筛选,若启用，请赋值为1
    ind：是你想要使用的行业的代码
    index_list：是指要用哪些指标
    '''
    stock_0 = pd.DataFrame()
    stock_1 = pd.DataFrame()
    stock_2 = pd.DataFrame()
    stock_3 = pd.DataFrame()
    stock_4 = pd.DataFrame()
    stock_5 = pd.DataFrame()
    stock_6 = pd.DataFrame()
    stock_7 = pd.DataFrame()
    stock_8 = pd.DataFrame()
    
    data_fin={}
    for time in cha_day:
        time = str(time)
        data = pd.concat([data_sw1,data_pb[time],data_roa[time],data_fta[time],data_fmi[time],data_roa_var[time],data_sag[time],data_res[time],data_cap[time],data_adv[time]],axis=1,join = 'inner')
        data.columns=["申万一级行业","PB","ROA","经营现金流与总资产之比","经营现金流减净利润","ROA方差","销售增长率方差","研发费用","资本支出","广告费用"]        
        if is_tech:
           data = data[(data["申万一级行业"]=="通信")|(data["申万一级行业"]=="电子")|(data["申万一级行业"]=="计算机")]
        if ind != None:
            data = data[data.index.isin(con_st[ind][int(time)].iloc[:,0])]
        half_year = data_hay[int(time)].iloc[:,0].tolist()
        st = data_st[int(time)].iloc[:,0].tolist()
        trad = data_tra[int(time)]
        trad = list(trad[trad['交易状态']=='交易'].iloc[:,0])
        loss = data_los[int(time)].iloc[:,0].tolist()        
        data = data[data.index.isin(half_year)]
        data = data[~data.index.isin(st)]#去除st
        data = data[data.index.isin(trad)]#去除不可交易的股票
        data = data[~data.index.isin(loss)]#去除最近亏损        
        
        sw_hangye = data["申万一级行业"].drop_duplicates().tolist()  
        st_data = pd.DataFrame()
        for hangye in sw_hangye:
            high_pb = np.percentile(data[data["申万一级行业"]==hangye]["PB"].dropna(),pb_per)
            mid_data = data[data["申万一级行业"]==hangye]
            st_data = pd.concat([st_data,mid_data[mid_data["PB"] > high_pb]])
        
        data = st_data.copy(deep=True)
        
        sw_hangye = data["申万一级行业"].drop_duplicates().tolist()        
        data["score"] = 0
        median_roa = {}
        median_roa_var = {}
        median_fta = {}
        median_sag_var = {}
        median_res = {}
        median_cap = {}
        median_adv = {}
        
        for hangye in sw_hangye:
            median_roa[hangye] = data[data["申万一级行业"]==hangye]["ROA"].dropna().median()
            median_roa_var[hangye] = data[data["申万一级行业"]==hangye]["ROA方差"].dropna().median()
            median_fta[hangye] = data[data["申万一级行业"]==hangye]["经营现金流与总资产之比"].dropna().median()
            median_sag_var[hangye] = data[data["申万一级行业"]==hangye]["销售增长率方差"].dropna().median()
            median_res[hangye] = data[data["申万一级行业"]==hangye]["研发费用"].dropna().median()
            median_cap[hangye] = data[data["申万一级行业"]==hangye]["资本支出"].dropna().median()
            median_adv[hangye] = data[data["申万一级行业"]==hangye]["广告费用"].dropna().median()
        
        for i in data.index:
            if 1 in index_list:
               if data.loc[i,"ROA"] > median_roa[data.loc[i,"申万一级行业"]]:
                  data.loc[i,"score"] += 1
            if 2 in index_list:
               if data.loc[i,"ROA方差"] < median_roa_var[data.loc[i,"申万一级行业"]]:
                  data.loc[i,"score"] += 1
            if 3 in index_list:
               if data.loc[i,"经营现金流与总资产之比"] > median_fta[data.loc[i,"申万一级行业"]]:
                  data.loc[i,"score"] += 1
            if 4 in index_list:
               if data.loc[i,"销售增长率方差"] < median_sag_var[data.loc[i,"申万一级行业"]]:
                  data.loc[i,"score"] += 1
            if 5 in index_list:
               if data.loc[i,"研发费用"] > median_res[data.loc[i,"申万一级行业"]]:
                  data.loc[i,"score"] += 1
            if 6 in index_list:
               if data.loc[i,"资本支出"] > median_cap[data.loc[i,"申万一级行业"]]:
                  data.loc[i,"score"] += 1
            if 7 in index_list:
               if data.loc[i,"广告费用"] > median_adv[data.loc[i,"申万一级行业"]]:
                  data.loc[i,"score"] += 1
            if 8 in index_list:
               if data.loc[i,"经营现金流减净利润"] > 0:
                  data.loc[i,"score"] += 1
            
        stock_0 = pd.concat([stock_0,pd.Series(data[data["score"]==0].index,name=time)],axis=1)
        stock_1 = pd.concat([stock_1,pd.Series(data[data["score"]==1].index,name=time)],axis=1)
        stock_2 = pd.concat([stock_2,pd.Series(data[data["score"]==2].index,name=time)],axis=1)
        stock_3 = pd.concat([stock_3,pd.Series(data[data["score"]==3].index,name=time)],axis=1)
        stock_4 = pd.concat([stock_4,pd.Series(data[data["score"]==4].index,name=time)],axis=1)
        stock_5 = pd.concat([stock_5,pd.Series(data[data["score"]==5].index,name=time)],axis=1)
        stock_6 = pd.concat([stock_6,pd.Series(data[data["score"]==6].index,name=time)],axis=1)
        stock_7 = pd.concat([stock_7,pd.Series(data[data["score"]==7].index,name=time)],axis=1)
        stock_8 = pd.concat([stock_8,pd.Series(data[data["score"]==8].index,name=time)],axis=1)
        
        data_fin[time] = data        
        print(str(time)+"完成！")        
    return stock_0,stock_1,stock_2,stock_3, stock_4,stock_5, stock_6,stock_7, stock_8,data_fin 


def dailyreturn(stock=None):
    #输入股票序列，输出日频收益率序列
    ewret = pd.Series()
    mwret = pd.Series()
    
    for i in range(stock.shape[1]):#对于每个换仓日，找出这次换仓持续时间上用什么股票，然后在该时间段上添加收益率
        timebeg = int(stock.columns[i])
        stocklist = stock[stock.columns[i]].dropna()
        if i == list(range(stock.shape[1]))[-1]:
           timeend = data_traday.iloc[-1,0]
        else:
           timeend = int(stock.columns[i+1])
        starti = data_traday.iloc[:,0].tolist().index(timebeg)#找出起始结束那两天在traday里的位置
        endi = data_traday.iloc[:,0].tolist().index(timeend)
        
        for j in range(starti,endi+1):
            day = data_traday.iloc[j,0]#找出你要计算的那天           
            ret_day = data_ret[day]
            ret_day = ret_day[ret_day["股票代码"].isin(stocklist)].set_index('股票代码').sort_index()
            
            if j == starti:#如果j是该期开始的那天，应该直接对该期股票池设置权重
                dewei = pd.Series()#储存等权下的每日权重
                dmwei = pd.Series()#储存市值加权下的每日权重
                lmv_day = data_lmv[data_traday.iloc[j-1,0]]
                lmv_day = lmv_day[lmv_day["WIND代码"].isin(stocklist)].set_index('WIND代码').sort_index()           
                for s in list(stocklist):
                    dewei.loc[s] = 1/len(stocklist) 
                    dmwei.loc[s] = float(lmv_day.loc[s]/lmv_day.sum())
                ldewei = dewei#储存上一日的权重
                ldmwei = dmwei
                      
            else:#以后的天里，权重是上一天的权重乘上一天的1+收益率
                lday = data_traday.iloc[j-1,0]#上一天
                lret_day = data_ret[lday]
                lret_day = lret_day[lret_day["股票代码"].isin(stocklist)].set_index('股票代码').sort_index()
                dewei = ldewei * (1+lret_day.iloc[:,0]/100)#填写非换仓日时的新一天权重
                dmwei = ldmwei * (1+lret_day.iloc[:,0]/100)
                dewei = dewei/dewei.sum()
                dmwei = dmwei/dmwei.sum()
                ldewei = dewei
                ldmwei = dmwei
            edret = np.sum(dewei*ret_day.iloc[:,0]/100)#等权下的日收益率
            mdret = np.sum(dmwei*ret_day.iloc[:,0]/100)#市权下的日收益率                  
            ewret.loc[day] = edret
            mwret.loc[day] = mdret
        print("第"+str(i)+"次换仓完成！")
    return ewret,mwret

pb_per = 50

# =============================================================================
# 全市场
# =============================================================================
stock_0,stock_1,stock_2,stock_3,stock_4,stock_5,stock_6,stock_7,stock_8,fin_data = stock_selection(pb_per = pb_per)
ret0_ew,ret0_mw = dailyreturn(stock = stock_0)
ret1_ew,ret1_mw = dailyreturn(stock = stock_1)
ret2_ew,ret2_mw = dailyreturn(stock = stock_2)
ret3_ew,ret3_mw = dailyreturn(stock = stock_3)
ret4_ew,ret4_mw = dailyreturn(stock = stock_4)
ret5_ew,ret5_mw = dailyreturn(stock = stock_5)
ret6_ew,ret6_mw = dailyreturn(stock = stock_6)
ret7_ew,ret7_mw = dailyreturn(stock = stock_7)
ret8_ew,ret8_mw = dailyreturn(stock = stock_8)

ret_ew = pd.concat([ret0_ew,ret1_ew,ret2_ew,ret3_ew,ret4_ew,ret5_ew,ret6_ew,ret7_ew,ret8_ew],axis=1)
ret_mw = pd.concat([ret0_mw,ret1_mw,ret2_mw,ret3_mw,ret4_mw,ret5_mw,ret6_mw,ret7_mw,ret8_mw],axis=1)

ret_ew2013 = (ret_ew.loc[20130830:,:]+1).cumprod()
ret_ew2013 = pd.concat([ret_ew2013,(data_ret_sw+1).cumprod()],axis = 1)
ret_mw2013 = (ret_mw.loc[20130830:,:]+1).cumprod()
ret_mw2013 = pd.concat([ret_mw2013,(data_ret_sw+1).cumprod()],axis = 1)

data_ret_sw.index = ret_ew2013.index

res12013 = (ret_ew2013 + 1).cumprod()
res22013 = (ret_mw2013 + 1).cumprod()

stock_group1 = pd.concat([stock_6,stock_7,stock_8])
stock_group2 = pd.concat([stock_4,stock_5,stock_6])
stock_group3 = pd.concat([stock_1,stock_2,stock_3])

ret_1_ew,ret_1_mw = dailyreturn(stock = stock_group1)
ret_2_ew,ret_2_mw = dailyreturn(stock = stock_group2)
ret_3_ew,ret_3_mw = dailyreturn(stock = stock_group3)

netvalue_mw2013 = ((ret_1_mw-ret_3_mw).loc[20130830:]+1).cumprod()
netvalue_ew2013 = ((ret_1_ew-ret_3_ew).loc[20130830:]+1).cumprod()

res_ew_gourp = pd.concat([ret_1_ew.loc[20130830:],ret_2_ew.loc[20130830:],ret_3_ew.loc[20130830:]],axis=1)
res_mw_gourp = pd.concat([ret_1_mw.loc[20130830:],ret_2_mw.loc[20130830:],ret_3_mw.loc[20130830:]],axis=1)

#年化收益
result = pd.DataFrame(index=["等权","市值加权","等权对冲","市值加权对冲","等权超额","市值加权超额"],columns=["年化收益","年化波动","最大回撤","起始日期","结束日期","夏普比"]+list(range(2013,2022)))

result.loc["市值加权","年化收益"] = daret(ret_1_mw.loc[20130830:])
result.loc["市值加权","年化波动"] = dannstd(ret_1_mw.loc[20130830:])   
maxd = dmaxdd(ret_1_mw.loc[20130830:])  
result.loc["市值加权","最大回撤"] = maxd[0]
result.loc["市值加权","起始日期"] = maxd[1]
result.loc["市值加权","结束日期"] = maxd[2]
result.loc["市值加权","夏普比"] = result.loc["市值加权","年化收益"]/result.loc["市值加权","年化波动"]
result.loc["市值加权",list(range(2013,2022))] = anincome(ret_1_mw.loc[20130830:])  

result.loc["等权","年化收益"] = daret(ret_1_ew.loc[20130830:])
result.loc["等权","年化波动"] = dannstd(ret_1_ew.loc[20130830:])   
maxd = dmaxdd(ret_1_ew.loc[20130830:])  
result.loc["等权","最大回撤"] = maxd[0]
result.loc["等权","起始日期"] = maxd[1]
result.loc["等权","结束日期"] = maxd[2]
result.loc["等权","夏普比"] = result.loc["等权","年化收益"]/result.loc["等权","年化波动"]
result.loc["等权",list(range(2013,2022))] = anincome(ret_1_ew.loc[20130830:])   

result.loc["市值加权对冲","年化收益"] = daret(ret_1_mw.loc[20130830:] - ret_3_mw.loc[20130830:])
result.loc["市值加权对冲","年化波动"] = dannstd(ret_1_mw.loc[20130830:] - ret_3_mw.loc[20130830:])   
maxd = dmaxdd(ret_1_mw.loc[20130830:]-ret_3_mw.loc[20130830:])  
result.loc["市值加权对冲","最大回撤"] = maxd[0]
result.loc["市值加权对冲","起始日期"] = maxd[1]
result.loc["市值加权对冲","结束日期"] = maxd[2]
result.loc["市值加权对冲","夏普比"] = result.loc["市值加权","年化收益"]/result.loc["市值加权","年化波动"]
result.loc["市值加权对冲",list(range(2013,2022))] = anincome(ret_1_mw.loc[20130830:] - ret_3_mw.loc[20130830:])  

result.loc["等权对冲","年化收益"] = daret(ret_1_ew.loc[20130830:] - ret_3_ew.loc[20130830:])
result.loc["等权对冲","年化波动"] = dannstd(ret_1_ew.loc[20130830:] - ret_3_ew.loc[20130830:])   
maxd = dmaxdd(ret_1_ew.loc[20130830:] - ret_3_ew.loc[20130830:])  
result.loc["等权对冲","最大回撤"] = maxd[0]
result.loc["等权对冲","起始日期"] = maxd[1]
result.loc["等权对冲","结束日期"] = maxd[2]
result.loc["等权对冲","夏普比"] = result.loc["等权","年化收益"]/result.loc["等权","年化波动"]
result.loc["等权对冲",list(range(2013,2022))] = anincome(ret_1_ew.loc[20130830:] - ret_3_ew.loc[20130830:])   

result.loc["市值加权超额","年化收益"] = daret(ret_1_mw.loc[20130830:]-data_ret_sw)
result.loc["市值加权超额","年化波动"] = dannstd(ret_1_mw.loc[20130830:]-data_ret_sw)   
maxd = dmaxdd(ret_1_mw.loc[20130830:]--data_ret_sw)  
result.loc["市值加权超额","最大回撤"] = maxd[0]
result.loc["市值加权超额","起始日期"] = maxd[1]
result.loc["市值加权超额","结束日期"] = maxd[2]
result.loc["市值加权超额","夏普比"] = result.loc["市值加权","年化收益"]/result.loc["市值加权","年化波动"]
result.loc["市值加权超额",list(range(2013,2022))] = anincome(ret_1_mw.loc[20130830:] - data_ret_sw)  

result.loc["等权超额","年化收益"] = daret(ret_1_ew.loc[20130830:] -data_ret_sw)
result.loc["等权超额","年化波动"] = dannstd(ret_1_ew.loc[20130830:] -data_ret_sw)   
maxd = dmaxdd(ret_1_ew.loc[20130830:] -data_ret_sw)  
result.loc["等权超额","最大回撤"] = maxd[0]
result.loc["等权超额","起始日期"] = maxd[1]
result.loc["等权超额","结束日期"] = maxd[2]
result.loc["等权超额","夏普比"] = result.loc["等权","年化收益"]/result.loc["等权","年化波动"]
result.loc["等权超额",list(range(2013,2022))] = anincome(ret_1_ew.loc[20130830:] - data_ret_sw)   

writer1 = pd.ExcelWriter("./结果/"+"全市场"+str(pb_per)+".xlsx")
result.to_excel(writer1,sheet_name = "结果")
ret_ew2013.to_excel(writer1,sheet_name = "2013后等权8组净值")
ret_mw2013.to_excel(writer1,sheet_name = "2013后市权8组净值")
(1+res_ew_gourp).cumprod().to_excel(writer1,sheet_name = "等权高中低分组净值")
(1+res_mw_gourp).cumprod().to_excel(writer1,sheet_name = "市权高中低分组净值")
stock_group1.to_excel(writer1,sheet_name = "高分组")
stock_group2.to_excel(writer1,sheet_name = "中分组")
stock_group3.to_excel(writer1,sheet_name = "低分组")
netvalue_ew2013.to_excel(writer1,sheet_name = "等权策略净值")
netvalue_mw2013.to_excel(writer1,sheet_name = "市权策略净值")
writer1.save()    

# =============================================================================
# 科技行业
# =============================================================================
stock_0,stock_1,stock_2,stock_3,stock_4,stock_5,stock_6,stock_7,stock_8,fin_data = stock_selection(pb_per = pb_per, is_tech = 1)
ret0_ew,ret0_mw = dailyreturn(stock = stock_0)
ret1_ew,ret1_mw = dailyreturn(stock = stock_1)
ret2_ew,ret2_mw = dailyreturn(stock = stock_2)
ret3_ew,ret3_mw = dailyreturn(stock = stock_3)
ret4_ew,ret4_mw = dailyreturn(stock = stock_4)
ret5_ew,ret5_mw = dailyreturn(stock = stock_5)
ret6_ew,ret6_mw = dailyreturn(stock = stock_6)
ret7_ew,ret7_mw = dailyreturn(stock = stock_7)
ret8_ew,ret8_mw = dailyreturn(stock = stock_8)

ret_ew = pd.concat([ret0_ew,ret1_ew,ret2_ew,ret3_ew,ret4_ew,ret5_ew,ret6_ew,ret7_ew,ret8_ew],axis=1)
ret_mw = pd.concat([ret0_mw,ret1_mw,ret2_mw,ret3_mw,ret4_mw,ret5_mw,ret6_mw,ret7_mw,ret8_mw],axis=1)

ret_ew2013 = (ret_ew.loc[20130830:,:]+1).cumprod()
ret_ew2013 = pd.concat([ret_ew2013,(data_ret_sw+1).cumprod()],axis = 1)
ret_mw2013 = (ret_mw.loc[20130830:,:]+1).cumprod()
ret_mw2013 = pd.concat([ret_mw2013,(data_ret_sw+1).cumprod()],axis = 1)

res12013 = (ret_ew2013+1).cumprod()
res22013 = (ret_mw2013+1).cumprod()

stock_group1 = pd.concat([stock_6,stock_7,stock_8])
stock_group2 = pd.concat([stock_4,stock_5,stock_6])
stock_group3 = pd.concat([stock_1,stock_2,stock_3])

ret_1_ew,ret_1_mw = dailyreturn(stock = stock_group1)
ret_2_ew,ret_2_mw = dailyreturn(stock = stock_group2)
ret_3_ew,ret_3_mw = dailyreturn(stock = stock_group3)

netvalue_mw2013 = ((ret_1_mw-ret_3_mw).loc[20130830:]+1).cumprod()
netvalue_ew2013 = ((ret_1_ew-ret_3_ew).loc[20130830:]+1).cumprod()

res_ew_gourp = pd.concat([ret_1_ew.loc[20130830:],ret_2_ew.loc[20130830:],ret_3_ew.loc[20130830:]],axis=1)
res_mw_gourp = pd.concat([ret_1_mw.loc[20130830:],ret_2_mw.loc[20130830:],ret_3_mw.loc[20130830:]],axis=1)

#年化收益
result = pd.DataFrame(index=["等权","市值加权","等权对冲","市值加权对冲","等权超额","市值加权超额"],columns=["年化收益","年化波动","最大回撤","起始日期","结束日期","夏普比"]+list(range(2013,2022)))

result.loc["市值加权","年化收益"] = daret(ret_1_mw.loc[20130830:])
result.loc["市值加权","年化波动"] = dannstd(ret_1_mw.loc[20130830:])   
maxd = dmaxdd(ret_1_mw.loc[20130830:])  
result.loc["市值加权","最大回撤"] = maxd[0]
result.loc["市值加权","起始日期"] = maxd[1]
result.loc["市值加权","结束日期"] = maxd[2]
result.loc["市值加权","夏普比"] = result.loc["市值加权","年化收益"]/result.loc["市值加权","年化波动"]
result.loc["市值加权",list(range(2013,2022))] = anincome(ret_1_mw.loc[20130830:])  

result.loc["等权","年化收益"] = daret(ret_1_ew.loc[20130830:])
result.loc["等权","年化波动"] = dannstd(ret_1_ew.loc[20130830:])   
maxd = dmaxdd(ret_1_ew.loc[20130830:])  
result.loc["等权","最大回撤"] = maxd[0]
result.loc["等权","起始日期"] = maxd[1]
result.loc["等权","结束日期"] = maxd[2]
result.loc["等权","夏普比"] = result.loc["等权","年化收益"]/result.loc["等权","年化波动"]
result.loc["等权",list(range(2013,2022))] = anincome(ret_1_ew.loc[20130830:])   

result.loc["市值加权对冲","年化收益"] = daret(ret_1_mw.loc[20130830:] - ret_3_mw.loc[20130830:])
result.loc["市值加权对冲","年化波动"] = dannstd(ret_1_mw.loc[20130830:] - ret_3_mw.loc[20130830:])   
maxd = dmaxdd(ret_1_mw.loc[20130830:]-ret_3_mw.loc[20130830:])  
result.loc["市值加权对冲","最大回撤"] = maxd[0]
result.loc["市值加权对冲","起始日期"] = maxd[1]
result.loc["市值加权对冲","结束日期"] = maxd[2]
result.loc["市值加权对冲","夏普比"] = result.loc["市值加权","年化收益"]/result.loc["市值加权","年化波动"]
result.loc["市值加权对冲",list(range(2013,2022))] = anincome(ret_1_mw.loc[20130830:] - ret_3_mw.loc[20130830:])  

result.loc["等权对冲","年化收益"] = daret(ret_1_ew.loc[20130830:] - ret_3_ew.loc[20130830:])
result.loc["等权对冲","年化波动"] = dannstd(ret_1_ew.loc[20130830:] - ret_3_ew.loc[20130830:])   
maxd = dmaxdd(ret_1_ew.loc[20130830:] - ret_3_ew.loc[20130830:])  
result.loc["等权对冲","最大回撤"] = maxd[0]
result.loc["等权对冲","起始日期"] = maxd[1]
result.loc["等权对冲","结束日期"] = maxd[2]
result.loc["等权对冲","夏普比"] = result.loc["等权","年化收益"]/result.loc["等权","年化波动"]
result.loc["等权对冲",list(range(2013,2022))] = anincome(ret_1_ew.loc[20130830:] - ret_3_ew.loc[20130830:])   

result.loc["市值加权超额","年化收益"] = daret(ret_1_mw.loc[20130830:]-data_ret_sw)
result.loc["市值加权超额","年化波动"] = dannstd(ret_1_mw.loc[20130830:]-data_ret_sw)   
maxd = dmaxdd(ret_1_mw.loc[20130830:]--data_ret_sw)  
result.loc["市值加权超额","最大回撤"] = maxd[0]
result.loc["市值加权超额","起始日期"] = maxd[1]
result.loc["市值加权超额","结束日期"] = maxd[2]
result.loc["市值加权超额","夏普比"] = result.loc["市值加权","年化收益"]/result.loc["市值加权","年化波动"]
result.loc["市值加权超额",list(range(2013,2022))] = anincome(ret_1_mw.loc[20130830:] - data_ret_sw)  

result.loc["等权超额","年化收益"] = daret(ret_1_ew.loc[20130830:] -data_ret_sw)
result.loc["等权超额","年化波动"] = dannstd(ret_1_ew.loc[20130830:] -data_ret_sw)   
maxd = dmaxdd(ret_1_ew.loc[20130830:] -data_ret_sw)  
result.loc["等权超额","最大回撤"] = maxd[0]
result.loc["等权超额","起始日期"] = maxd[1]
result.loc["等权超额","结束日期"] = maxd[2]
result.loc["等权超额","夏普比"] = result.loc["等权","年化收益"]/result.loc["等权","年化波动"]
result.loc["等权超额",list(range(2013,2022))] = anincome(ret_1_ew.loc[20130830:] - data_ret_sw)   

writer1 = pd.ExcelWriter("./结果/"+"科技行业"+str(pb_per)+".xlsx")
result.to_excel(writer1,sheet_name = "结果")
ret_ew2013.to_excel(writer1,sheet_name = "2013后等权8组净值")
ret_mw2013.to_excel(writer1,sheet_name = "2013后市权8组净值")
(1+res_ew_gourp).cumprod().to_excel(writer1,sheet_name = "等权高中低分组净值")
(1+res_mw_gourp).cumprod().to_excel(writer1,sheet_name = "市权高中低分组净值")
stock_group1.to_excel(writer1,sheet_name = "高分组")
stock_group2.to_excel(writer1,sheet_name = "中分组")
stock_group3.to_excel(writer1,sheet_name = "低分组")
netvalue_ew2013.to_excel(writer1,sheet_name = "等权策略净值")
netvalue_mw2013.to_excel(writer1,sheet_name = "市权策略净值")
writer1.save()   