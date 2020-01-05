import pandas as pd
from baseClass.baseMysql import MysqlConn
from model.warningModel import WarningModel
from utils.timedata import cal_year, cal_month, start_week_date, end_week_date, year_list
from utils.util import add_empty_data

mc = MysqlConn('mysql-ali')
sql_year = '''SELECT YEAR(ACCIDENT_DATE),DISEASE_NAME,count(id) from `t_card_infection`
        where DISEASE_NAME in ('痢疾','登革热','丙肝','戊肝','乙肝','百日咳','淋病','梅毒','流行性感冒', 
        '流行性腮腺炎','风疹','急性出血性结膜炎','手足口病','其它感染性腹泻病') 
        AND YEAR(ACCIDENT_DATE) >= %s AND DISEASE_NAME IS NOT NULL
        GROUP BY DISEASE_NAME,YEAR(ACCIDENT_DATE) ORDER BY YEAR(ACCIDENT_DATE),DISEASE_NAME'''
sql_month = '''SELECT YEAR(ACCIDENT_DATE),DISEASE_NAME,count(id) from `t_card_infection`
        where DISEASE_NAME in ('痢疾','登革热','丙肝','戊肝','乙肝','百日咳','淋病','梅毒','流行性感冒', 
        '流行性腮腺炎','风疹','急性出血性结膜炎','手足口病','其它感染性腹泻病') 
        AND YEAR(ACCIDENT_DATE) >= %s AND DISEASE_NAME IS NOT NULL AND MONTH(ACCIDENT_DATE)=%s
        GROUP BY DISEASE_NAME,YEAR(ACCIDENT_DATE) ORDER BY YEAR(ACCIDENT_DATE),DISEASE_NAME''' % (cal_year, cal_month)
sql_week = '''SELECT YEAR(ACCIDENT_DATE),DISEASE_NAME,count(id) from `t_card_infection`
        where DISEASE_NAME in ('痢疾','登革热','丙肝','戊肝','乙肝','百日咳','淋病','梅毒','流行性感冒', 
        '流行性腮腺炎','风疹','急性出血性结膜炎','手足口病','其它感染性腹泻病') AND DISEASE_NAME IS NOT NULL
         and ((ACCIDENT_DATE between '%s' and  '%s') or (ACCIDENT_DATE between '%s' and  '%s') or 
        (ACCIDENT_DATE between '%s' and  '%s') or (ACCIDENT_DATE between '%s' and  '%s') or 
        (ACCIDENT_DATE between '%s' and '%s')) 
        GROUP BY YEAR(t.ONSET_DATE) ORDER BY YEAR(t.ONSET_DATE),DISEASE_NAME''' % (start_week_date[1], end_week_date[1],
                                                                                   start_week_date[2], end_week_date[2],
                                                                                   start_week_date[3], end_week_date[3],
                                                                                   start_week_date[4], end_week_date[4],
                                                                                   start_week_date[5], end_week_date[5])

res_year_five = mc.getAll(sql_year, cal_year)
# res_month_five = add_empty_data(mc.select(sql_month))
# res_week_five = add_empty_data(mc.select(sql_week))

five_year_data = pd.DataFrame(index=year_list, columns=[('count_year', 'hand'), ('count_year', 'foot')])
# five_month_data = pd.DataFrame(res_month_five, columns=['Date', 'count_month'], index=year_list)
# five_week_data = pd.DataFrame(res_week_five, columns=['Date', 'count_week'], index=year_list)

# 合并5年的数据（方法1）
# five_data = pd.DataFrame(index=year_list)
# five_data['count_year'] = five_year_data['count_year']
# five_data['count_month'] = five_month_data['count_month']
# five_data['count_week'] = five_week_data['count_week']

# 合并5年的数据（方法2）
five_data = pd.concat([five_year_data, five_month_data, five_week_data], axis=1)
five_data.pop('Date')
# five_data = data.iloc[:-1]
# now_data = data.iloc[-1:]
three_data = five_data.iloc[-4:-1]
# 计算标准差\t分布下置信区间
# std_five, interval_five = deal_cal_std_interval(five_data)
# std_three, interval_three = deal_cal_std_interval(three_data)
# 拷贝数据
# five_data = five_data.copy()
# three_data = three_data.copy()
# 均值
# five_data.loc['mean'] = five_data.mean()
# three_data.loc['mean'] = three_data.mean()
# # 标准差
# five_data.loc['std'] = std_five
# three_data.loc['std'] = std_three
# # 偏度系数
# five_data.loc['skew'] = five_data.skew()
# three_data.loc['skew'] = three_data.skew()
# # 变异系数
# five_data.loc['v'] = five_data.loc['std'] / five_data.loc['mean']
# three_data.loc['v'] = three_data.loc['std'] / three_data.loc['mean']
# # 置信区间
# five_data.loc['interval_up'] = [x[1] for x in interval_five]
# three_data.loc['interval_up'] = [x[1] for x in interval_three]
