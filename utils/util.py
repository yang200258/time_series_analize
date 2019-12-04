import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from baseClass.baseMysql import MysqlConn


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


def save_data(pred):
    mc = MysqlConn()
    ls = []
    for index, row in pred.iterrows():
        d = index.split('-')
        t = d[0], d[1], index, int(row['upper Count']), int(row['lower'])
        ls.append(t)
    sql = '''insert into ifd_forecast_cal(UUID, CAL_YEAR, CAL_MONTH,CAL_DATE, MAX_FORECAST_COUNT, MIN_FORECAST_COUNT)
                                values(UUID(), %s, %s, str_to_date(%s,'%%Y-%%m-%%d'), %s, %s) 
                                on duplicate key update MAX_FORECAST_COUNT=values(MAX_FORECAST_COUNT) and MIN_FORECAST_COUNT=values(MIN_FORECAST_COUNT)'''
    mc.add(sql, ls)
