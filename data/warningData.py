import pandas as pd
from baseClass.baseMysql import MysqlConn
from utils.timedata import cal_year, cal_month, start_week_date, end_week_date
from utils.util import trans_mysql_data

mc = MysqlConn('mysql-test-warning')
sql_year = '''SELECT YEAR(ACCIDENT_DATE) as year,DISEASE_NAME as name,count(ID_CARD) as count from `t_card_infection`
        where DISEASE_NAME in ('痢疾','登革热','丙肝','戊肝','乙肝','百日咳','淋病','梅毒','流行性感冒', 
        '流行性腮腺炎','风疹','急性出血性结膜炎','手足口病','其它感染性腹泻病') 
        AND YEAR(ACCIDENT_DATE) >= %s AND DISEASE_NAME IS NOT NULL
        GROUP BY DISEASE_NAME,YEAR(ACCIDENT_DATE) ORDER BY YEAR(ACCIDENT_DATE),DISEASE_NAME''' % cal_year
sql_month = '''SELECT YEAR(ACCIDENT_DATE) as year,DISEASE_NAME as name,count(ID_CARD) as count  from `t_card_infection`
        where DISEASE_NAME in ('痢疾','登革热','丙肝','戊肝','乙肝','百日咳','淋病','梅毒','流行性感冒', 
        '流行性腮腺炎','风疹','急性出血性结膜炎','手足口病','其它感染性腹泻病') 
        AND YEAR(ACCIDENT_DATE) >= %s AND DISEASE_NAME IS NOT NULL AND MONTH(ACCIDENT_DATE)=%s
        GROUP BY DISEASE_NAME,YEAR(ACCIDENT_DATE) ORDER BY YEAR(ACCIDENT_DATE),DISEASE_NAME''' % (cal_year, cal_month)
sql_week = '''SELECT YEAR(ACCIDENT_DATE) as year,DISEASE_NAME as name,count(ID_CARD) as count from `t_card_infection`
        where DISEASE_NAME in ('痢疾','登革热','丙肝','戊肝','乙肝','百日咳','淋病','梅毒','流行性感冒', 
        '流行性腮腺炎','风疹','急性出血性结膜炎','手足口病','其它感染性腹泻病') AND DISEASE_NAME IS NOT NULL
         and ((ACCIDENT_DATE between '%s' and  '%s') or (ACCIDENT_DATE between '%s' and  '%s') or 
        (ACCIDENT_DATE between '%s' and  '%s') or (ACCIDENT_DATE between '%s' and  '%s') or 
        (ACCIDENT_DATE between '%s' and '%s')) 
        GROUP BY YEAR(ACCIDENT_DATE) ORDER BY YEAR(ACCIDENT_DATE),DISEASE_NAME''' % (
    start_week_date[1], end_week_date[1],
    start_week_date[2], end_week_date[2],
    start_week_date[3], end_week_date[3],
    start_week_date[4], end_week_date[4],
    start_week_date[5], end_week_date[5])

five_year_data = trans_mysql_data(mc.getAll(sql_year))
five_month_data = trans_mysql_data(mc.getAll(sql_month))
five_week_data = trans_mysql_data(mc.getAll(sql_week))

# 合并5年的数据
five_data = pd.concat([five_year_data, five_month_data, five_week_data], axis=1, keys=['year', 'month', 'week'])
three_data = five_data.iloc[-4:-1]
now_data = five_data.iloc[-1:]

