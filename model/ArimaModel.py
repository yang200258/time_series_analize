import warnings
import matplotlib.pyplot as plt
import itertools
from statsmodels.tsa.api import statespace
from utils.util import dic_key
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score
from math import sqrt

plt.style.use('fivethirtyeight')
warnings.filterwarnings('ignore')


class ArimaModel(object):
    def __init__(self, train, test, *args):
        self.best_model_arg = {}
        for item in args:
            if len(item) == 3:
                self.best_model_arg['order'] = item
            if len(item) == 4:
                self.best_model_arg['seasonal_order'] = item
        self.df = pd.DataFrame().append(train).append(test)
        self.train = train
        self.test = test
        self.y_hat_avg = self.test.copy()
        if 'order' not in self.best_model_arg.keys() and 'seasonal_order' not in self.best_model_arg.keys():
            self.best_model_arg = self.generate_model_arg(train)
        # self.fit_validate = self.generate_model(self.train, self.best_model_arg)
        # self.plot_corr(self.fit_validate)
        self.fit = self.generate_model(self.df, self.best_model_arg)

    def generate_model_arg(self, train):
        if 'order' in self.best_model_arg.keys():
            pdq = [self.best_model_arg['order']]
        else:
            p = range(0, 3)
            d = q = range(0, 2)
            pdq = list(itertools.product(p, d, q))
        if 'seasonal_order' in self.best_model_arg.keys():
            seasonal_pdq = self.best_model_arg['seasonal_order']
        else:
            seasonal_pdq = [(x[0], x[1], x[2], 12) for x in pdq]
        res_data = []
        for param in pdq:
            for seasonal_param in seasonal_pdq:
                try:
                    mod = statespace.SARIMAX(train['Count'], order=param, seasonal_order=seasonal_param,
                                             enforce_stationarity=False, enforce_invertibility=False)
                    res = mod.fit()
                    res_data.append({"order": param, "seasonal_order": seasonal_param, "AIC": res.aic})
                except:
                    continue
        print(res_data)
        if res_data:
            return min(res_data, key=dic_key)
        else:
            raise Exception("The res_data is empty!")

    @staticmethod
    def generate_model(train, best_model_arg):
        return statespace.SARIMAX(train['Count'], order=best_model_arg['order'],
                                  seasonal_order=best_model_arg['seasonal_order'],
                                  enforce_stationarity=False, enforce_invertibility=False).fit()

    @staticmethod
    def plot_corr(fit):
        print(fit.summary().tables[1])
        fit.plot_diagnostics(figsize=(15, 12))
        plt.show()

    def static_validate(self):
        # predict the model value
        pred = self.fit_validate.get_prediction(start=pd.to_datetime(self.test.index[0]),
                                                end=pd.to_datetime(self.test.index[-1]), dynamic=False)
        pred_ci_static = pred.conf_int()
        # plot
        # ax = self.train['Count'].plot(figsize=(15, 8), label="observed", title="static validate forecast")
        # self.test['Count'].plot(ax=ax, label="test data", color="red")
        # pred.predicted_mean.plot(ax=ax, label="the static predict value by ARIMA model", alpha=.7)
        # ax.fill_between(pred_ci_static.index, pred_ci_static.iloc[:, 0], pred_ci_static.iloc[:, 1], color="k", alpha=.2)
        # plt.legend()
        # plt.show()
        # compute the MSE
        # y_forecast = pred.predicted_mean
        mse_static = sqrt(
            mean_squared_error(self.test['Count'], self.fit_validate.predict(start=pd.to_datetime(self.test.index[0]),
                                                                             end=pd.to_datetime(self.test.index[-1]),
                                                                             dynamic=False)))
        return pred, pred_ci_static, mse_static

    def dynamic_validate(self):
        pred_dynamic = self.fit_validate.get_prediction(start=pd.to_datetime(self.test.index[0]),
                                                        end=pd.to_datetime(self.test.index[-1]), dynamic=True,
                                                        full_results=True)
        pred_dynamic_ci = pred_dynamic.conf_int()
        # plot
        # ax = self.train['Count'].plot(figsize=(15, 8), label="observed", title="dynamic validate forecast")
        # self.test['Count'].plot(ax=ax, label="test data", color="red")
        # pred_dynamic.predicted_mean.plot(ax=ax, label="the dynamic predict value by ARIMA model")
        # ax.fill_between(pred_dynamic_ci.index, pred_dynamic_ci.iloc[:, 0], pred_dynamic_ci.iloc[:, 1], color="k",
        #                 alpha=.25)
        # plt.legend()
        # plt.show()
        # compute the MSE
        # y_forecast_dynamic = pred_dynamic.predicted_mean
        mse_dynamic = sqrt(
            mean_squared_error(self.test['Count'], self.fit_validate.predict(start=pd.to_datetime(self.test.index[0]),
                                                                             end=pd.to_datetime(self.test.index[-1]),
                                                                             dynamic=True)))
        return pred_dynamic, pred_dynamic_ci, mse_dynamic

    def predict(self, forecast_steps):
        pred_uc = self.fit.get_forecast(steps=forecast_steps)
        pred_ci = pred_uc.conf_int()
        # ax = self.df['Count'].plot(figsize=(20, 15), label="observed", title="final forecast")
        # pred_uc.predicted_mean.plot(ax=ax, label="predict value by ARIMA model")
        # ax.fill_between(pred_ci.index, pred_ci.iloc[:, 0], pred_ci.iloc[:, 1], color="k")
        # plt.legend()
        # plt.show()
        return pred_ci

# ------------                                ARIMA forecast model             -------------------------
# y_hat_avg = test.copy()
# p = d = q = range(0, 2)
# pdq = list(itertools.product(p, d, q))
# seasonal_pdq = [(x[0], x[1], x[2], 7) for x in pdq]
# res_data = []
# for param in pdq:
#     for seasonal_param in seasonal_pdq:
#         try:
#             mod = statespace.SARIMAX(train['Count'], order=param, seasonal_order=seasonal_param,
#                                      enforce_stationarity=False, enforce_invertibility=False)
#             res = mod.fit()
#             res_data.append({"order": param, "seasonal_order": seasonal_param, "AIC": res.aic})
#         except:
#             continue


# best_model = min(res_data, key=dic_key)
# final_model = statespace.SARIMAX(train['Count'], order=best_model['order'], seasonal_order=best_model['seasonal_order'],
#                                  enforce_stationarity=False, enforce_invertibility=False)

# results = final_model.fit()
# print(results.summary().tables[1])
# # plot the validate pic
# results.plot_diagnostics(figsize=(15, 12))
# plt.show()

# ---------static validate forecast

# # predict the model value
# pred = results.get_prediction(start=pd.to_datetime('2013-11-01'), end=pd.to_datetime('2013-12-31'), dynamic=False)
# pred_ci_static = pred.conf_int()
# # plot
# ax = train['Count'].plot(figsize=(15, 8), label="observed", title="static validate forecast")
# test['Count'].plot(ax=ax, label="test data", color="red")
# pred.predicted_mean.plot(ax=ax, label="the static predict value by ARIMA model", alpha=.7)
# ax.fill_between(pred_ci_static.index, pred_ci_static.iloc[:, 0], pred_ci_static.iloc[:, 1], color="k", alpha=.2)
# plt.legend()
# plt.show()
# # compute the MSE
# y_forecast = pred.predicted_mean
# mse = ((y_forecast - test['Count']) ** 2).mean()

# -----------dynamic validate forecast

# pred_dynamic = results.get_prediction(start=pd.to_datetime('2013-11-01'), end=pd.to_datetime('2013-12-31'),
#                                       dynamic=True, full_results=True)
# pred_dynamic_ci = pred_dynamic.conf_int()
# # plot
# ax = train['Count'].plot(figsize=(15, 8), label="observed", title="dynamic validate forecast")
# # test['Count'].plot(ax=ax, label="test data", color="red")
# pred_dynamic.predicted_mean.plot(ax=ax, label="the dynamic predict value by ARIMA model")
# ax.fill_between(pred_dynamic_ci.index, pred_dynamic_ci.iloc[:, 0], pred_dynamic_ci.iloc[:, 1], color="k", alpha=.25)
# plt.legend()
# plt.show()
# # compute the MSE
# y_forecasted_dynamic = pred_dynamic.predicted_mean
# mse_dynamic = ((y_forecasted_dynamic - test['Count']) ** 2).mean()

# ----------generate the predict data

# pred_uc = results.get_forecast(steps=365)
# pred_ci = pred_uc.conf_int()
# ax = df['Count'].plot(figsize=(20, 15), label="observed", title="final forecast")
# pred_uc.predicted_mean.plot(ax=ax, label="predict value by ARIMA model")
# ax.fill_between(pred_ci.index, pred_ci.iloc[:, 0], pred_ci.iloc[:, 1], color="k", alpha=.25)
# plt.legend()
# plt.show()
