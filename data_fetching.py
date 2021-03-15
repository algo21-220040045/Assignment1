#要计算G-score来选股回测
import numpy as np
import os 
import datetime
import pandas as pd
import cx_Oracle as database

#设置字符串编码格式
os.environ["NlS_LANG"]="SIMPLIFIED CHINESE_CHINA.UTF8"
con=database.connect("windquery","wind2010query","10.2.89.132:1521/winddb")
#%%
# =============================================================================
# 取交易日期，从2008年开始
# =============================================================================
sql='''
           select distinct acal.TRADE_DAYS
           from wind.AShareCalendar acal
           where acal.S_INFO_EXCHMARKET = 'SSE'
    '''   
enddate=(datetime.datetime.today()-datetime.timedelta(days=1)).strftime("%Y%m%d")
trad_date_list = pd.read_sql(sql,con,index_col=None).sort_values(by = 'TRADE_DAYS', ascending = True).set_index(keys="TRADE_DAYS",drop=False).loc["20071231":enddate,:].index.tolist()
pd.DataFrame(trad_date_list).to_excel("./数据/交易日期.xlsx")
#%%
# =============================================================================
# 记录换仓的交易日
# =============================================================================
year=list(range(2008,2021))
data_traday = pd.DataFrame(trad_date_list)
cha_day=[]
for i in range(len(data_traday)-1):
    if int(str(data_traday.iloc[i][0])[:4]) in year:
        if str(data_traday.iloc[i][0])[4:6] in ['04','08','10']:
           if str(data_traday.iloc[i][0])[4:6] != str(data_traday.iloc[i+1][0])[4:6]:
              cha_day.append(str(data_traday.iloc[i][0])) 
pd.DataFrame(cha_day[3:]).to_excel("./数据/换仓日.xlsx")
#%%
def near_rep_date(date):
    '''
    任意输入一个日期，输出一个过去最近的报告期
    '''    
    rep_date=['0331','0630','0930','1231']
    if date[4:] in rep_date:
        return date
    else:
        if date[4:6] in ["01","02","03"]:
           return str(int(date[:4])-1)+'1231'
        elif date[4:6] in ["04","05","06"]:
           return date[:4]+'0331'
        elif date[4:6] in ["07","08","09"]:
           return date[:4]+'0630'
        else:
           return date[:4]+'0930'

def last_rep_date(date):
    '''
    输入一个报告期，输出前一个报告期,删除亏损公司用
    '''
    if date[4:6]=='03':
       return str(int(date[:4])-1)+'1231'
    elif date[4:6]=='06':
       return date[:4]+'0331'
    else:
       return str(int(date[:6])-3)+'30'
#%%
# =============================================================================
# 读取每日收益率
# =============================================================================
try:
    os.mkdir("./数据/日收益率")
except OSError:
    print("文件夹已创建")
filelist=os.listdir(r"./数据/日收益率")
for num,i in enumerate(trad_date_list[:-1]):
    if not trad_date_list[num+1]+".xlsx" in filelist:
        print("正在读取第{}个交易日期{}收益相关数据".format(num+1, trad_date_list[num+1]))
        sql = '''
                 select distinct a.S_INFO_WINDCODE as 股票代码,
                        a.S_DQ_PCTCHANGE as 日涨跌幅
                 from wind.AShareEODPrices a
                 where a.TRADE_DT = '{trad_date}'
              '''
        sql = sql.format(trad_date = trad_date_list[num+1])
        mv_data=pd.read_sql(sql,con,index_col=None)
        mv_data.to_excel("./数据/日收益率/"+trad_date_list[num+1]+".xlsx")
        print(trad_date_list[num+1]+"的日收益数据已导出！")
    else:
        print("第{}个交易日期{}日收益相关数据已提取过".format(num+1, trad_date_list[num+1]))
print("诶呦！不错呦")
#%%
# =============================================================================
# 读取每日流通市值
# =============================================================================
try:
    os.mkdir("./数据/流通市值")
except OSError:
    print("文件夹已创建")
filelist=os.listdir(r"./数据/流通市值")
for num,i in enumerate(trad_date_list[:-1]):
    if not trad_date_list[num+1]+".xlsx" in filelist:
        print("正在读取第{}个交易日期{}流通市值相关数据".format(num+1, trad_date_list[num+1]))
        sql = '''
                 select distinct a.S_INFO_WINDCODE as Wind代码,
                        a.TRADE_DT as 交易日,
                        a.S_DQ_MV as 当日流通市值
                 from wind.AShareEODDerivativeIndicator a
                 where a.TRADE_DT = '{trad_date}'
              '''
        sql = sql.format(trad_date = trad_date_list[num+1])
        mv_data=pd.read_sql(sql,con,index_col=None)
        mv_data.to_excel("./数据/流通市值/"+trad_date_list[num+1]+".xlsx")
        print(trad_date_list[num+1]+"的流通市值数据已导出！")
    else:
        print("第{}个交易日期{}的流通市值相关数据已提取过".format(num+1, trad_date_list[num+1]))
print("诶呦！不错呦")
#%%
# =============================================================================
# 选取ST股
# =============================================================================
try:
    os.mkdir("./数据/ST股")
except OSError:
    print("文件夹已创建")
filelist=os.listdir(r"./数据/ST股")

for num,i in enumerate(trad_date_list[:-1]):
    if not trad_date_list[num+1]+".xlsx" in filelist:
        print("正在读取第{}个交易日期{}ST股相关数据".format(num+1, trad_date_list[num+1]))
        sql='''
           select ast.s_info_windcode as wind_code
           from   wind.AShareST ast
           where ast.ENTRY_DT <= '{financialdate}' and 
                 (ast.REMOVE_DT >= '{financialdate}' or ast.REMOVE_DT is NULL) and
                 ast.S_TYPE_ST = 'S'
        '''
        sql = sql.format(financialdate = trad_date_list[num+1])
        st_data=pd.read_sql(sql,con,index_col=None)
        st_data["交易日期"] = trad_date_list[num+1]
        st_data.to_excel("./数据/ST股/"+trad_date_list[num+1]+".xlsx")
        print(trad_date_list[num+1]+"的ST股数据已导出！")
    else:
        print("第{}个交易日期{}的ST股相关数据已提取过".format(num+1, trad_date_list[num+1]))
print("诶呦！不错呦")
#%%
# =============================================================================
# 上市满半年的股票
# =============================================================================
try:
    os.mkdir("./数据/满半年")
except OSError:
    print("文件夹已创建")
filelist=os.listdir(r"./数据/满半年")
for i in cha_day[3:]:
    if not i+".xlsx" in filelist:
        sql='''
               select ashare.s_info_windcode as windcode
               from wind.AShareDescription ashare   
               where TO_NUMBER(to_date('{financialdate}','yyyymmdd') -
                              to_date(ashare.S_INFO_LISTDATE,'yyyymmdd')) >= 183 and
                     (ashare.S_INFO_DELISTDATE >= '{financialdate}' or 
                      ashare.S_INFO_DELISTDATE is NULL)
            '''
        sql = sql.format(financialdate = i)
        data = pd.read_sql(sql,con,index_col=None)
        data.to_excel("./数据/满半年/"+ i +".xlsx")
        print(i+"完成！")
    else:
        print("{}数据已提取过".format(i))
#%%        
# =============================================================================
# 交易状态
# =============================================================================
try:
    os.mkdir("./数据/交易状态")
except OSError:
    print("文件夹已创建")
filelist=os.listdir(r"./数据/交易状态")
for i in cha_day[3:]:
    if not i+".xlsx" in filelist:
        sql = '''
                 select distinct a.S_INFO_WINDCODE as Wind代码,
                        a.TRADE_DT as 交易日,
                        a.S_DQ_TRADESTATUS as 当日流通市值
                 from wind.AShareEODPrices a
                 where a.TRADE_DT = '{trad_date}'
              '''
        sql = sql.format(financialdate = i)
        data = pd.read_sql(sql,con,index_col=None)
        data.to_excel("./数据/交易状态/"+ i +".xlsx")
        print(i+"完成！")
    else:
        print("{}数据已提取过".format(i))
#%%        
# =============================================================================
# 交易状态
# =============================================================================
try:
    os.mkdir("./数据/上财报亏损")
except OSError:
    print("文件夹已创建")
filelist=os.listdir(r"./数据/上财报亏损")
for i in cha_day[3:]:
    if not i+".xlsx" in filelist:
        sql='''
              select distinct apro.s_info_windcode as windcode,
                     apro.S_QFA_DEDUCTEDPROFIT as 上财报利润
              from wind.AShareFinancialIndicator apro   
              where apro.REPORT_PERIOD = '{financialdate}' and
                    apro.S_QFA_DEDUCTEDPROFIT < 0
            ''' 
        sql = sql.format(financialdate = last_rep_date(near_rep_date(i)))
        data = pd.read_sql(sql,con,index_col=None)
        data.to_excel("./数据/上财报亏损/"+ i +".xlsx")
        print(i+"完成！")
    else:
        print("{}数据已提取过".format(i))
#%%
# =============================================================================
# 导入pb
# =============================================================================
data_pb=pd.DataFrame()
for i in cha_day[3:]:
    sql='''
          select distinct apro.s_info_windcode as windcode,
                 apro.S_VAL_PB_NEW as PB
          from wind.AShareEODDerivativeIndicator apro   
          where apro.TRADE_DT = '{financialdate}'
        ''' 
    sql = sql.format(financialdate = i)
    mid_data = pd.read_sql(sql,con,index_col=None).set_index("WINDCODE")
    mid_data.columns = [i]
    data_pb = pd.concat([data_pb,mid_data],axis=1)
    print(i+"完成！")
data_pb.to_excel("./数据/PB.xlsx")
#%%
# =============================================================================
# 导入pe
# =============================================================================
data_pe = pd.DataFrame()
for i in cha_day[3:]:
    sql='''
          select distinct apro.s_info_windcode as windcode,
                 apro.S_VAL_PE as PE
          from wind.AShareEODDerivativeIndicator apro   
          where apro.TRADE_DT = '{financialdate}'
        ''' 
    sql = sql.format(financialdate = i)
    mid_data = pd.read_sql(sql,con,index_col=None).set_index("WINDCODE")
    mid_data.columns = [i]
    data_pe = pd.concat([data_pe,mid_data],axis=1)
    print(i+"完成！")
data_pe.to_excel("./数据/PE.xlsx")
#%%
# =============================================================================
# 导入研发费用
# =============================================================================
data_res=pd.DataFrame()
for i in cha_day[3:]:
    sql='''
          select distinct apro.s_info_windcode as windcode,
                 apro.RD_EXPENSE as 研发费用
          from wind.AShareFinancialIndicator apro   
          where apro.REPORT_PERIOD = '{financialdate}'
        ''' 
    sql = sql.format(financialdate = near_rep_date(i))
    mid_data = pd.read_sql(sql,con,index_col=None).set_index("WINDCODE")
    mid_data.columns = [i]
    data_res = pd.concat([data_res,mid_data],axis=1)
    print(i+"完成！")
data_res.to_excel("./数据/研发费用.xlsx")
#%%
# =============================================================================
# 导入广告
# =============================================================================
data_adv=pd.DataFrame()
for i in cha_day[3:]:
    sql='''
          select distinct apro.s_info_windcode as windcode,
                 apro.APE_COS as 广告宣传
          from wind.FinNotesDetail apro   
          where apro.REPORT_PERIOD = '{financialdate}' and
                apro.STATEMENT_TYPE = 408001000
        ''' 
    sql = sql.format(financialdate = near_rep_date(i))
    mid_data = pd.read_sql(sql,con,index_col=None).set_index("WINDCODE")
    mid_data.columns = [i]
    data_adv = pd.concat([data_adv,mid_data],axis=1)
    print(i+"完成！")
data_adv.to_excel("./数据/广告费用.xlsx")
#%%
# =============================================================================
# 导入现金流量
# =============================================================================
data_fcf = pd.DataFrame()
for i in cha_day[3:]:
    sql='''
          select distinct apro.s_info_windcode as windcode,
                 apro.NET_CASH_FLOWS_OPER_ACT as 经营活动现金流量
          from wind.AShareCashFlow apro   
          where apro.REPORT_PERIOD = '{financialdate}' and
                apro.STATEMENT_TYPE = 408001000
        ''' 
    sql = sql.format(financialdate = near_rep_date(i))
    mid_data = pd.read_sql(sql,con,index_col=None).set_index("WINDCODE")
    mid_data.columns = [i]
    data_fcf = pd.concat([data_fcf,mid_data],axis=1)
    print(i+"完成！")
data_fcf.to_excel("./数据/经营活动现金流量.xlsx")
#%%
# =============================================================================
# 导入净利润
# =============================================================================
data_nep = pd.DataFrame()
for i in cha_day[3:]:
    sql='''
          select distinct apro.s_info_windcode as windcode,
                 apro.NET_PROFIT_INCL_MIN_INT_INC as 净利润
          from wind.AShareIncome apro   
          where apro.REPORT_PERIOD = '{financialdate}' and
                apro.STATEMENT_TYPE = 408001000
        ''' 
    sql = sql.format(financialdate = near_rep_date(i))
    mid_data = pd.read_sql(sql,con,index_col=None).set_index("WINDCODE")
    mid_data.columns = [i]
    data_nep = pd.concat([data_nep,mid_data],axis=1)
    print(i+"完成！")
data_nep.to_excel("./数据/净利润.xlsx")
#%%
# =============================================================================
# 导入资本支出
# =============================================================================
data_cap = pd.DataFrame()
for i in cha_day[3:]:
    sql='''
          select distinct apro.s_info_windcode as windcode,
                 apro.S_FA_CAPITALIZEDTODA as 资本支出
          from wind.AShareFinancialIndicator apro   
          where apro.REPORT_PERIOD = '{financialdate}' 
        ''' 
    sql = sql.format(financialdate = near_rep_date(i))
    mid_data = pd.read_sql(sql,con,index_col=None).set_index("WINDCODE")
    mid_data.columns = [i]
    data_cap = pd.concat([data_cap,mid_data],axis=1)
    print(i+"完成！")
data_cap.to_excel("./数据/资本支出.xlsx")
#%%
# =============================================================================
# 导入总资产
# =============================================================================
data_toa = pd.DataFrame()
for i in cha_day[3:]:
    sql='''
          select distinct apro.s_info_windcode as windcode,
                 apro.TOT_ASSETS as 总资产
          from wind.AShareBalanceSheet apro   
          where apro.REPORT_PERIOD = '{financialdate}' and
                apro.STATEMENT_TYPE = 408001000
        ''' 
    sql = sql.format(financialdate = near_rep_date(i))
    mid_data = pd.read_sql(sql,con,index_col=None).set_index("WINDCODE")
    mid_data.columns = [i]
    data_toa = pd.concat([data_toa,mid_data],axis=1)
    print(i+"完成！")
data_toa.to_excel("./数据/总资产.xlsx")
#%%
# =============================================================================
# 导入单季度总资产净利率
# =============================================================================
data_roa = pd.DataFrame()
for i in cha_day[3:]:
    sql='''
          select distinct apro.s_info_windcode as windcode,
                 apro.S_QFA_ROA as 总资产净利率
          from wind.AShareFinancialIndicator apro   
          where apro.REPORT_PERIOD = '{financialdate}'
        ''' 
    sql = sql.format(financialdate = near_rep_date(i))
    mid_data = pd.read_sql(sql,con,index_col=None).set_index("WINDCODE")
    mid_data.columns = [i]
    data_roa = pd.concat([data_roa,mid_data],axis=1)
    print(i+"完成！")
data_roa.to_excel("./数据/ROA.xlsx")
#%%
# =============================================================================
# 取交易日期，从2004年开始
# =============================================================================
sql='''
           select distinct acal.TRADE_DAYS
           from wind.AShareCalendar acal
           where acal.S_INFO_EXCHMARKET = 'SSE'
    '''   
enddate=(datetime.datetime.today()-datetime.timedelta(days=1)).strftime("%Y%m%d")
trad_date_list1 = pd.read_sql(sql,con,index_col=None).sort_values(by = 'TRADE_DAYS', ascending = True).set_index(keys="TRADE_DAYS",drop=False).loc["20031231":enddate,:].index.tolist()
# =============================================================================
# 记录换仓的交易日
# =============================================================================
year1=list(range(2003,2021))
data_traday1 = pd.DataFrame(trad_date_list1)
cha_day1=[]
for i in range(len(data_traday1)-1):
    if int(str(data_traday1.iloc[i][0])[:4]) in year1:
        if str(data_traday1.iloc[i][0])[4:6] in ['04','08','10']:
           if str(data_traday1.iloc[i][0])[4:6] != str(data_traday1.iloc[i+1][0])[4:6]:
              cha_day1.append(str(data_traday1.iloc[i][0]))           
# =============================================================================
# 导入前五年总资产净利率
# =============================================================================
data_roa1 = pd.DataFrame()
for i in cha_day1:
    sql='''
          select distinct apro.s_info_windcode as windcode,
                 apro.S_QFA_ROA as 总资产净利率
          from wind.AShareFinancialIndicator apro   
          where apro.REPORT_PERIOD = '{financialdate}'
        ''' 
    sql = sql.format(financialdate = near_rep_date(i))
    mid_data = pd.read_sql(sql,con,index_col=None).set_index("WINDCODE")
    mid_data.columns = [i]
    data_roa1 = pd.concat([data_roa1,mid_data],axis=1)
    print(i+"完成！")

data_var_roa = pd.DataFrame(index = data_roa1.index,columns = data_roa1.columns[15:])
for i in range(len(data_var_roa.columns)):
    data_var_roa.iloc[:,i] = np.std(data_roa1.iloc[:,i:15+i],axis=1)
data_var_roa.to_excel("./数据/ROA方差.xlsx")
#%%    
# =============================================================================
# 取交易日期，从2003年开始
# =============================================================================

              
# =============================================================================
# 导入前5年营业收入同比
# =============================================================================
data_rev_yoy = pd.DataFrame()
for i in cha_day1:
    sql='''
          select distinct apro.s_info_windcode as windcode,
                 apro.S_QFA_YOYSALES as 营业收入同比增长率
          from wind.AShareFinancialIndicator apro   
          where apro.REPORT_PERIOD = '{financialdate}'
        ''' 
    sql = sql.format(financialdate = near_rep_date(i))
    mid_data = pd.read_sql(sql,con,index_col=None).set_index("WINDCODE")
    mid_data.columns = [i]
    data_rev_yoy = pd.concat([data_rev_yoy,mid_data],axis=1)
    print(i+"完成！")

data_var_rev_yoy = pd.DataFrame(index = data_rev_yoy.index, columns = data_rev_yoy.columns[15:])
for i in range(len(data_var_rev_yoy.columns)):
    data_var_rev_yoy.iloc[:,i] = np.std(data_rev_yoy.iloc[:,i:15+i],axis=1)
data_var_rev_yoy.to_excel("./数据/销售增长率方差.xlsx")
 


#%%
#指数每个月后一个交易日的成分股
index_numbe=['000300.SH',#沪深300
            '000016.SH',#上证50
            '000905.SH',#中证500
            '000906.SH',#中证800
            '000852.SH',#中证1000
            '881001.WI',#Wind全A
            '000688.SH',#科创50
            '399006.SZ']#创业板指
try:
    os.mkdir("./指数成分股")
except OSError:
    print("文件夹已创建")
filelist=os.listdir(r"./指数成分股")

temp=pd.DataFrame(data=trad_date_list,index=trad_date_list,columns=["traday"])
temp=(temp.loc[(temp["traday"]).apply(lambda x:str(x)[:6])!=(temp["traday"].shift(-1)).apply(lambda x:str(x)[:6]),:]).index.tolist()[:-1]
for i in index_numbe:
    for j in range(len(temp)):
        if not i +"-" + temp[j] +".xlsx" in filelist:
            if i!='881001.WI':
               sql_ind='''
                           select com_stock.com_stock_code
                           from (select ind.S_CON_WINDCODE as com_stock_code
                                 from wind.AIndexMembers ind   
                                 where ind.s_info_windcode = '{info_code}' and
                                       ind.S_CON_INDATE  <= '{tar_date}' and 
                                       (ind.S_CON_OUTDATE  >= '{tar_date}' or ind.S_CON_OUTDATE is NULL)) com_stock
                       '''
               sql_ind = sql_ind.format(info_code = i, tar_date = temp[j])
               pd.read_sql(sql_ind,con,index_col=None).to_excel("./指数成分股/"+ i +"-" + temp[j] +".xlsx")
               print(i+"在"+temp[j]+"的计算完成！")
            else:
               sql_ind='''
                           select com_stock.com_stock_code
                           from (select ind.S_CON_WINDCODE as com_stock_code
                                 from wind.AIndexMembersWIND ind   
                                 where ind.F_INFO_WINDCODE = '{info_code}' and
                                       ind.S_CON_INDATE  <= '{tar_date}' and 
                                       (ind.S_CON_OUTDATE  >= '{tar_date}' or ind.S_CON_OUTDATE is NULL)) com_stock
                       '''
               sql_ind = sql_ind.format(info_code = i, tar_date = temp[j])
               pd.read_sql(sql_ind,con,index_col=None).to_excel("./指数成分股/"+ i +"-" + temp[j] +".xlsx")
               print(i+"在"+temp[j]+"的计算完成！")                 
        else:
            print(i+"在"+temp[j]+"已提取过")


#%%
#各个行业开始的时间
shenwan1 = pd.read_excel("申万行业指数代码.xlsx",sheet_name = '一级')
shenwan1 = shenwan1.set_index("所属申万行业名称[行业级别] 一级行业")
shenwan2 = pd.read_excel("申万行业指数代码.xlsx",sheet_name = '二级')
shenwan2 = shenwan2.set_index("所属申万行业名称[行业级别] 二级行业")
shenwan3 = pd.read_excel("申万行业指数代码.xlsx",sheet_name = '三级')
shenwan3 = shenwan3.set_index("所属申万行业名称[行业级别] 三级行业")

hangye_begin_date1 = pd.DataFrame()
for i in shenwan1.iloc[:,0].tolist():
    sql_hangye='''
                select a.S_INFO_LISTDATE from wind.AIndexDescription a where a.S_INFO_WINDCODE='{hangye_code}'
               '''
    sql_hangye = sql_hangye.format(hangye_code = i)
    hangye_begin_date1.loc[i,"开始日期"] = pd.read_sql(sql_hangye,con,index_col=None).iloc[0,0]
hangye_begin_date1.to_excel("./申万一级开始日期.xlsx")

hangye_begin_date2 = pd.DataFrame()
for i in shenwan2.iloc[:,0].tolist():
    sql_hangye='''
                select a.S_INFO_LISTDATE from wind.AIndexDescription a where a.S_INFO_WINDCODE='{hangye_code}'
               '''
    sql_hangye = sql_hangye.format(hangye_code = i)
    hangye_begin_date2.loc[i,"开始日期"] = pd.read_sql(sql_hangye,con,index_col=None).iloc[0,0]
hangye_begin_date2.to_excel("./申万二级开始日期.xlsx")

hangye_begin_date3 = pd.DataFrame()
for i in shenwan3.iloc[:,0].tolist():
    sql_hangye='''
                select a.S_INFO_LISTDATE from wind.AIndexDescription a where a.S_INFO_WINDCODE='{hangye_code}'
               '''
    sql_hangye = sql_hangye.format(hangye_code = i)
    hangye_begin_date3.loc[i,"开始日期"] = pd.read_sql(sql_hangye,con,index_col=None).iloc[0,0]
hangye_begin_date3.to_excel("./申万三级开始日期.xlsx")
#%%
#申万行业剔除三种特殊情况后每个月最后一个交易日的成分股
try:
    os.mkdir("./申万一级成分股")
except OSError:
    print("文件夹已创建")
filelist=os.listdir("./申万一级成分股")
temp=pd.DataFrame(data=trad_date_list,index=trad_date_list,columns=["traday"])
temp=(temp.loc[(temp["traday"]).apply(lambda x:str(x)[:6])!=(temp["traday"].shift(-1)).apply(lambda x:str(x)[:6]),:]).index.tolist()[:-1]
for i in shenwan1.iloc[:,0].tolist():
    for j in range(len(temp)):
            sql_hangye='''
                           select com_stock.com_stock_code
                           from (select swi.S_CON_WINDCODE as com_stock_code
                                 from wind.SWIndexMembers swi   
                                 where swi.s_info_windcode = '{hangye_code}' and
                                       swi.S_CON_INDATE  <= '{tar_date}' and 
                                       (swi.S_CON_OUTDATE  >= '{tar_date}' or swi.S_CON_OUTDATE is NULL)) com_stock
                        '''
            if not i +"-"+ temp[j] +".xlsx" in filelist:
                   sql_hangye = sql_hangye.format(hangye_code = i, tar_date =temp[j])
                   pd.read_sql(sql_hangye,con,index_col=None).to_excel("./申万一级成分股/"+ i +"-"+ temp[j] +".xlsx")
                   print("申万一级的"+i+"在"+temp[j]+"的计算完成！")
            else:
                   print("申万一级的"+i+"在"+temp[j]+"已提取过")


#%%
try:
    os.mkdir("./申万二级成分股")
except OSError:
    print("文件夹已创建")
filelist=os.listdir("./申万二级成分股")
temp=pd.DataFrame(data=trad_date_list,index=trad_date_list,columns=["traday"])
temp=(temp.loc[(temp["traday"]).apply(lambda x:str(x)[:6])!=(temp["traday"].shift(-1)).apply(lambda x:str(x)[:6]),:]).index.tolist()[:-1]
for i in shenwan2.iloc[:,0].tolist():
    for j in range(len(temp)):
        sql_hangye='''
                       select com_stock.com_stock_code
                       from (select swi.S_CON_WINDCODE as com_stock_code
                             from wind.SWIndexMembers swi   
                             where swi.s_info_windcode = '{hangye_code}' and
                                   swi.S_CON_INDATE  <= '{tar_date}' and 
                                   (swi.S_CON_OUTDATE  >= '{tar_date}' or swi.S_CON_OUTDATE is NULL)) com_stock
                    '''
        if not i +"-"+ temp[j] +".xlsx" in filelist:
           sql_hangye = sql_hangye.format(hangye_code = i, tar_date =  temp[j])
           pd.read_sql(sql_hangye,con,index_col=None).to_excel("./申万二级成分股/"+ i +"-"+ temp[j] +".xlsx")
           print("申万二级的"+i+"在"+temp[j]+"的计算完成！")
        else:
            print("申万二级的"+i+"在"+temp[j]+"已提取过")


#%%
shenwan3 = pd.read_excel("申万行业指数代码.xlsx",sheet_name = '三级')
shenwan3 = shenwan3.set_index("所属申万行业名称[行业级别] 三级行业")
try:
    os.mkdir("./申万三级成分股")
except OSError:
    print("文件夹已创建")
filelist=os.listdir("./申万三级成分股")
temp=pd.DataFrame(data=trad_date_list,index=trad_date_list,columns=["traday"])
temp=(temp.loc[(temp["traday"]).apply(lambda x:str(x)[:6])!=(temp["traday"].shift(-1)).apply(lambda x:str(x)[:6]),:]).index.tolist()[:-1]
for i in shenwan3.iloc[:,0].tolist():
    for j in range(len(temp)):
        sql_hangye='''
                       select com_stock.com_stock_code
                       from (select swi.S_CON_WINDCODE as com_stock_code
                             from wind.SWIndexMembers swi   
                             where swi.s_info_windcode = '{hangye_code}' and
                                   swi.S_CON_INDATE  <= '{tar_date}' and 
                                   (swi.S_CON_OUTDATE  >= '{tar_date}' or swi.S_CON_OUTDATE is NULL)) com_stock
                    '''
        if not i +"-"+ temp[j] +".xlsx" in filelist:
           sql_hangye = sql_hangye.format(hangye_code = i, tar_date = temp[j])
           pd.read_sql(sql_hangye,con,index_col=None).to_excel("./申万三级成分股/"+ i +"-"+temp[j] +".xlsx")
           print("申万三级的"+i+"在"+temp[j]+"的计算完成！") 
        else:
           print("申万三级的"+i+"在"+temp[j]+"已提取过")

    


