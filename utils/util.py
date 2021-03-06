import time

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from model.ArimaModel import ArimaModel
from model.WarningModel import WarningModel

from utils.timedata import year_list, now_year, cal_month, cal_week

area_id = '8cca28b405ac11e4a031d96810bebd04'
area_code = '460000000000'
area_name = '海南省'
level_code = '460000000000'
full_name = '海南省'


# aggregating dataFrame by the resample
def aggregating(data_frame, style):
    data_frame['Datetime'] = pd.to_datetime(data_frame['Datetime'], format="%Y-%m-%d")
    data_frame['Count'] = pd.to_numeric(data_frame['Count'])
    data_frame.index = data_frame['Datetime']
    return data_frame.resample(style).sum()


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


def save_pred_data(mc, pred):
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
    mc.insertMany(sql, ls)


def save_warn_data(mc, data, type_cal, dise_ls, week_num, is_restore):
    sql = '''insert into 
        t_infect_t_distribution_warning(UUID, CAL_AREA_ID, CAL_AREA_CODE, CAL_AREA_LEVEL_CODE, 
        CAL_AREA_NAME, CAL_AREA_FULL_NAME, title_cal, TYPE_YEAR_CODE, TYPE_TIME_CODE, DISEASE_NAME, DISEASE_CODE,
        COUNT_CAL, MEAN_CAL, SKEW_CAL, STD_CAL, INTERVAL_UP_CAL, CV_CAL, IS_ACTIVE, WARNING_STATE, WARNING_TIME,
        UPDATE_TIME,  CREATE_TIME) 
        values(UUID(), %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, 
        str_to_date(%s,'%%Y-%%m-%%d %%H:%%i:%%s'), str_to_date(%s,'%%Y-%%m-%%d %%H:%%i:%%s'), 
        str_to_date(%s,'%%Y-%%m-%%d %%H:%%i:%%s'))
        on duplicate key update COUNT_CAL=%s,MEAN_CAL=%s,SKEW_CAL=%s,STD_CAL=%s,INTERVAL_UP_CAL=%s,CV_CAL=%s,
        WARNING_STATE=%s,WARNING_TIME=%s,UPDATE_TIME=%s'''
    ls = []
    now = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    type_time = {"year": 1, "month": 2, "week": 3}
    type_title = {1: "%s年" % now_year, 2: "%s年%s月" % (now_year, cal_month), 3: "%s年第%s周" % (now_year, week_num)}
    for index, row in data:
        item = list(data[index][row][-6:])
        title_cal = type_title[type_time[index]]
        if is_restore:
            warning_state = 0 if (int(item[0]) < int(item[4])) or (int(item[0]) == int(item[4]) == 0) else 1
            warning_time = None if (int(item[0]) < int(item[4])) or (int(item[0]) == int(item[4]) == 0) else now
        else:
            verified_ls = get_verified_data(mc)
            str_ver = "%s-%s-%s-%s" % (title_cal, type_cal, type_time[index], dise_ls[row])
            if verified_ls.setdefault(str_ver, 0):
                warning_state = verified_ls[str_ver].split('@')[0]
                warning_time = verified_ls[str_ver].split('@')[1]
            else:
                warning_state = 0 if (int(item[0]) < int(item[4])) or (int(item[0]) == int(item[4]) == 0) else 1
                warning_time = None if (int(item[0]) < int(item[4])) or (int(item[0]) == int(item[4]) == 0) else now
        t = area_id, area_code, level_code, area_name, full_name, title_cal, type_cal, type_time[index], row, \
            dise_ls[row], int(item[0]), round(item[1], 2), round(item[2], 2), round(item[3], 2), int(item[4]), \
            round(item[5], 2), '1', warning_state, warning_time, now, now, int(item[0]), round(item[1], 2), \
            round(item[2], 2), round(item[3], 2), int(item[4]), round(item[5], 2), warning_state, warning_time, now
        if type_cal == 1 and type_time[index] == 3 and title_cal=='2020年第24周' and dise_ls[row] == '0302':
            print(int(item[0]), round(item[1], 2), round(item[2], 2), round(item[3], 2), int(item[4]), round(item[5], 2))
        ls.append(t)
    mc.insertMany(sql, ls)


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


def get_verified_data(mc):
    sql_verified = '''select title_cal,TYPE_YEAR_CODE,TYPE_TIME_CODE,DISEASE_CODE,WARNING_TIME,warning_state from t_infect_t_distribution_warning 
                            where warning_state <> 0'''
    verified_res = list(mc.getAll(sql_verified))
    ls = {}
    for item in verified_res:
        ls["%s-%s-%s-%s" % (item[0], item[1], item[2], item[3])] = "%s@%s" % (item[5], item[4])
    return ls


def generalPred(mc, hfm_train, hfm_test):
    # plot the trend pic
    # util.plot_trend(handFootMouth.hfm_train, handFootMouth.hfm_test)

    # create the model by arima
    arima_test = ArimaModel(hfm_train, hfm_test, (2, 1, 1), (2, 1, 1, 12))

    # validate the model
    # pred_static, pred_static_ci, mse_static = arima.static_validate()
    # pred_dynamic, pred_ci_dynamic, mse_dynamic = arima.dynamic_validate()

    # generate the forecast data
    pred_ci = arima_test.predict(2)
    pred_results = format_pred(pred_ci)

    # save the forecast data to database
    save_pred_data(mc, pred_results)

    # create the model by HoltWinter
    # holt = HoltWintersModel(handFootMouth.hfm_train, handFootMouth.hfm_test, 2)
    # holt.plot_validate()
    # x = holt.predict(3)


def generalWarn(mc, five_data, three_data, dis_ls, i=cal_week, is_restore=False):
    t = WarningModel(five_data).cal_frame
    t2 = WarningModel(three_data).cal_frame

    save_warn_data(mc, t, 2, dis_ls, i, is_restore)
    save_warn_data(mc, t2, 1, dis_ls, i, is_restore)
