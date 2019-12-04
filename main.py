from apscheduler.schedulers.background import BackgroundScheduler

import data.handFootMouth as handFootMouth
from model.ArimaModel import ArimaModel
from utils.util import format_pred, save_data
scheduler = BackgroundScheduler()


@scheduler.scheduled_job('cron', month='1-12', day='1', hour='0', minute='0', second='0')
def main():
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


if __name__ == '__main__':
    scheduler.start()
