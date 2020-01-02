import logging

from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.background import BlockingScheduler

import data.handFootMouth as handFootMouth
from data.warningData import five_data, three_data
from model.ArimaModel import ArimaModel
from model.warningModel import WarningModel
from utils.util import format_pred, save_data

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='log.txt',
                    filemode='a')
scheduler = BlockingScheduler()


def my_listener(event):
    if event.exception:
        print('任务出现异常！')
    else:
        print('任务照常运行...')


scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
scheduler._logger = logging


@scheduler.scheduled_job('cron', month='1-12', day='1', hour='0', minute='1', second='0')
def hand_foot_mouth():
    print('Get the hand_foot_mouth disease forecast data.')
    # plot the trend pic
    # util.plot_trend(handFootMouth.hfm_train, handFootMouth.hfm_test)

    # create the model by arima
    arima = ArimaModel(handFootMouth.hfm_train, handFootMouth.hfm_test, (2, 1, 1), (2, 1, 1, 12))

    # validate the model
    # pred_static, pred_static_ci, mse_static = arima.static_validate()
    # pred_dynamic, pred_ci_dynamic, mse_dynamic = arima.dynamic_validate()

    # generate the forecast data
    pred_ci = arima.predict(2)
    pred_results = format_pred(pred_ci)

    # save the forecast data to database
    save_data(pred_results)

    # create the model by HoltWinter
    # holt = HoltWintersModel(handFootMouth.hfm_train, handFootMouth.hfm_test, 2)
    # holt.plot_validate()
    # x = holt.predict(3)


@scheduler.scheduled_job('cron', month='1-12', day='1-31', hour='0', minute='1', second='0')
def warning_disease():
    t = WarningModel(five_data)
    t2 = WarningModel(three_data)


if __name__ == '__main__':
    with open('log.txt', 'a', encoding='utf8') as f:
        try:
            scheduler.start()
            f.write('the task run successful!\n')
        except Exception:
            scheduler.shutdown()
            f.write('***********************the task run error!*****************************\n')
