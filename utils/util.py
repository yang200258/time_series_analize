import time

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from baseClass.baseMysql import MysqlConn

# aggregating dataFrame by the resample
from utils.timedata import year_list


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


def save_data(pred):
    mc_test = MysqlConn('59.212.39.6', 'jikong', 'Zh~m,nhG!3', 'jcfx', 'utf8')
    mc_formal = MysqlConn()
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
    mc_test.add(sql, ls)
    mc_formal.add(sql, ls)


def add_empty_data(res_data):
    q_ls = []
    p_ls = []
    for p, q in res_data:
        p_ls.append(p)
        q_ls.append((p, int(q)))
    for x in year_list:
        if x not in p_ls:
            q_ls.append((x, 0))
    return q_ls

