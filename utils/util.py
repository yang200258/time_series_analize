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
    mc_test = MysqlConn('mysql-test-jcfx')
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
    mc_test.add(sql, ls)
    mc_formal.add(sql, ls)


ds = ['痢疾', '登革热', '丙肝', '戊肝', '乙肝', '百日咳', '淋病', '梅毒', '流行性感冒',
      '流行性腮腺炎', '风疹', '急性出血性结膜炎', '手足口病', '其它感染性腹泻病']


# TODO 需要优化从数据库拿出的列表数据，如何更高效转化为dataframe
def trans_mysql_data(res_data):
    data = pd.DataFrame(index=year_list, columns=ds)
    start = time.time()
    for item in res_data:
        data.at[item[0], item[1]] = item[2]
    data.fillna(0, inplace=True)
    end = time.time() - start
    print('处理从数据库获取的数据共用时：%s 秒' % end)
    return data
