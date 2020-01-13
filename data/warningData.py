import pandas as pd
from baseClass.baseMysql import MysqlConn
from model.WarningModel import WarningModel
from utils.timedata import cal_year, cal_month, start_week_date, end_week_date
from utils.util import trans_mysql_data, generalWarn, save_warn_data


def getWarningData(mc, dis_list):
    sql_dise = '''SELECT DISEASES_NAME,DISEASE_CODE from dim_infect_disease'''
    # 获取所有疾病对应code及names
    dise_ls = dict(mc.getAll(sql_dise))
    sql_year = '''SELECT YEAR(ACCIDENT_DATE) as year,DISEASE_NAME as name, count(ID_CARD) as count 
            from `t_card_infection`
            where DISEASE_NAME in %s AND YEAR(ACCIDENT_DATE) >= %s AND DISEASE_NAME IS NOT NULL
            GROUP BY DISEASE_NAME,YEAR(ACCIDENT_DATE) ORDER BY YEAR(ACCIDENT_DATE),DISEASE_NAME''' % (ds, cal_year)
    sql_month = '''SELECT YEAR(ACCIDENT_DATE) as year,DISEASE_NAME as name,count(ID_CARD) as count  from `t_card_infection`
            where DISEASE_NAME in %s AND YEAR(ACCIDENT_DATE) >= %s AND DISEASE_NAME IS NOT NULL AND MONTH(ACCIDENT_DATE)=%s
            GROUP BY DISEASE_NAME,YEAR(ACCIDENT_DATE) ORDER BY YEAR(ACCIDENT_DATE),DISEASE_NAME''' % (
        ds, cal_year, cal_month)
    sql_week = '''SELECT YEAR(ACCIDENT_DATE) as year,DISEASE_NAME as name,count(ID_CARD) as count from `t_card_infection`
            where DISEASE_NAME in %s AND DISEASE_NAME IS NOT NULL
             and ((ACCIDENT_DATE between '%s' and  '%s') or (ACCIDENT_DATE between '%s' and  '%s') or 
            (ACCIDENT_DATE between '%s' and  '%s') or (ACCIDENT_DATE between '%s' and  '%s') or 
            (ACCIDENT_DATE between '%s' and '%s')) 
            GROUP BY YEAR(ACCIDENT_DATE) ORDER BY YEAR(ACCIDENT_DATE),DISEASE_NAME''' % (ds, start_week_date[1],
                                                                                         end_week_date[1],
                                                                                         start_week_date[2],
                                                                                         end_week_date[2],
                                                                                         start_week_date[3],
                                                                                         end_week_date[3],
                                                                                         start_week_date[4],
                                                                                         end_week_date[4],
                                                                                         start_week_date[5],
                                                                                         end_week_date[5])

    # 获取数据
    y_res = mc.getAll(sql_year)
    m_res = mc.getAll(sql_month)
    w_res = mc.getAll(sql_week)

    # 转化数据
    five_year_data = trans_mysql_data(y_res, dis_list)
    five_month_data = trans_mysql_data(m_res, dis_list)
    five_week_data = trans_mysql_data(w_res, dis_list)

    # 合并5年的数据
    five_data = pd.concat([five_year_data, five_month_data, five_week_data], axis=1, keys=['year', 'month', 'week'])
    three_data = five_data.iloc[-4:].copy()
    return five_data, three_data, dise_ls


ds = ('痢疾', '登革热', '丙肝', '戊肝', '乙肝', '百日咳', '淋病', '梅毒', '流行性感冒',
      '流行性腮腺炎', '风疹', '急性出血性结膜炎', '手足口病', '其它感染性腹泻病')
mc_test = MysqlConn('mysql-test-warning')
mc_formal = MysqlConn('mysql-formal-warning')
five_data_test, three_data_test, dis_ls_test = getWarningData(mc_test, ds)
five_data_formal, three_data_formal, dis_ls_formal = getWarningData(mc_formal, ds)

t = WarningModel(five_data_test).cal_frame
t2 = WarningModel(three_data_test).cal_frame

save_warn_data(mc_test, t, 2, dis_ls_test)
save_warn_data(mc_test, t2, 1, dis_ls_test)

mc_test.dispose()
mc_formal.dispose()
