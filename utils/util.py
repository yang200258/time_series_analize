import time

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from baseClass.baseMysql import MysqlConn

from utils.timedata import year_list, cal_week, now_year, cal_month


# aggregating dataFrame by the resample
def aggregating(data_frame, style):
    data_frame['Datetime'] = pd.to_datetime(data_frame['Datetime'], format="%Y-%m-%d")
    data_frame['Count'] = pd.to_numeric(data_frame['Count'])
    data_frame.index = data_frame['Datetime']
    return data_frame.resample(style).sum()


def dic_key(dic):
    return dic['AIC']


def plot_trend(train, test):
    train.Count.plot(figsize=(15, 8), title="train data", fontsize=14)
    test.Count.plot(figsize=(15, 8), title="test data", fontsize=14)
    # show the plot
    plt.show()


def format_pred(pred):
    pred['lower'] = pred.apply(lambda x: (x['lower Count'] + x['upper Count']) / 2, axis=1)
    pydata_array = pred.index.to_pydatetime()
    date_only_array = np.vectorize(lambda s: s.strftime('%Y-%m-%d'))(pydata_array)
    pred.index = pd.Series(date_only_array)
    return pred


def save_pred_data(pred):
    mc_test = MysqlConn('mysql-test-forecast')
    mc_formal = MysqlConn('mysql-formal-forecast')
    ls = []
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    for index, row in pred.iterrows():
        d = index.split('-')
        t = d[0], d[1], index, int((row['upper Count'] + abs(row['upper Count']))) // 2, \
            int((row['lower'] + abs(row['lower']))) // 2, 1, str(now), str(now)
        ls.append(t)
    sql = '''REPLACE into ifd_forecast_cal(UUID, CAL_YEAR, CAL_MONTH,CAL_DATE, MAX_FORECAST_COUNT, MIN_FORECAST_COUNT,
            IS_ACTIVE, CREATE_TIME, DEFAULT_TIME) 
            values(UUID(), %s, %s, str_to_date(%s,'%%Y-%%m-%%d'), %s, %s, %s, str_to_date(%s,'%%Y-%%m-%%d %%H:%%i:%%s')
            , str_to_date(%s,'%%Y-%%m-%%d %%H:%%i:%%s'))'''
    mc_test.insertMany(sql, ls)
    mc_formal.insertMany(sql, ls)
    mc_test.dispose()
    mc_formal.dispose()


def save_warn_data(data, type_cal, dise_ls):
    mc_test = MysqlConn('mysql-test-warning')
    # mc_formal = MysqlConn('mysql-formal-warning')
    sql = '''REPLACE into 
        t_infect_t_distribution_warning(UUID, title_cal, TYPE_YEAR_CODE, TYPE_TIME_CODE, DISEASE_NAME, DISEASE_CODE,COUNT_CAL,
         MEAN_CAL, SKEW_CAL, STD_CAL, INTERVAL_UP_CAL, CV_CAL, IS_ACTIVE, warning_state, WARNING_TIME, UPDATE_TIME,  CREATE_TIME) 
        values(UUID(), %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, str_to_date(%s,'%%Y-%%m-%%d %%H:%%i:%%s'), str_to_date(%s,'%%Y-%%m-%%d %%H:%%i:%%s')
                , str_to_date(%s,'%%Y-%%m-%%d %%H:%%i:%%s'))'''
    ls = []
    now = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    type_time = {"year": 1, "month": 2, "week": 3}
    type_title = {1: "%s年" % now_year, 2: "%s年%s月" % (now_year, cal_month), 3: "%s年第%s周" % (now_year, cal_week)}
    for index, row in data:
        item = list(data[index][row][-6:])
        warning_state = 0 if (int(item[0]) < int(item[4])) or (int(item[0]) == int(item[4]) == 0) else 1
        warning_time = None if (int(item[0]) < int(item[4])) or (int(item[0]) == int(item[4]) == 0) else now
        title_cal = type_title[type_time[index]]
        t = title_cal, type_cal, type_time[index], row, dise_ls[row], int(item[0]), round(item[1], 2), round(item[2], 2)\
            , round(item[3], 2), int(item[4]), round(item[5], 2), '1', warning_state, warning_time, now, now
        ls.append(t)
    mc_test.insertMany(sql, ls)
    mc_test.dispose()


# TODO 需要优化从数据库拿出的列表数据，如何更高效转化为dataframe
def trans_mysql_data(res_data, ds):
    data = pd.DataFrame(index=year_list, columns=ds)
    start = time.time()
    for item in res_data:
        data.at[item[0], item[1]] = item[2]
    data.fillna(0, inplace=True)
    end = time.time() - start
    print('处理从数据库获取的数据共用时：%s 秒' % end)
    return data
