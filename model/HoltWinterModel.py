import matplotlib.pyplot as plt
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from math import sqrt
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


class HoltWintersModel(object):
    def __init__(self, train, test, seasonal_periods):
        self.train = train
        self.test = test
        self.seasonal_periods = seasonal_periods
        self.y_hat_avg = test.copy()
        self.fits = self.generate_fit()
        self.validate_forecast()
        self.validates = self.validate_results()
        self.best_fit = self.best_model()

    def generate_fit(self):
        # fit the model
        fit1 = ExponentialSmoothing(np.asarray(self.train['Count']), seasonal_periods=self.seasonal_periods,
                                    trend='add', seasonal='add').fit()
        fit2 = ExponentialSmoothing(np.asarray(self.train['Count']), seasonal_periods=self.seasonal_periods,
                                    trend='add', seasonal='mul').fit()
        fit3 = ExponentialSmoothing(np.asarray(self.train['Count']), seasonal_periods=self.seasonal_periods,
                                    trend='add', seasonal='add', damped=True).fit()
        fit4 = ExponentialSmoothing(np.asarray(self.train['Count']), seasonal_periods=self.seasonal_periods,
                                    trend='add', seasonal='mul', damped=True).fit()
        return fit1, fit2, fit3, fit4

    def validate_forecast(self):
        # assign the forecast value to y_hat_avg
        self.y_hat_avg['additive'] = self.fits[0].forecast(len(self.test))
        self.y_hat_avg['multiplicative'] = self.fits[1].forecast(len(self.test))
        self.y_hat_avg['additive-dam'] = self.fits[2].forecast(len(self.test))
        self.y_hat_avg['multiplicative-dam'] = self.fits[3].forecast(len(self.test))

    def plot_validate(self):
        ax = self.train['Count'].plot(figsize=(15, 8), label="observed", title="Holt-Winter model forecast")
        self.test['Count'].plot(ax=ax, label="test data", color="red")
        self.y_hat_avg['additive'].plot(ax=ax, color='blue')
        self.y_hat_avg['multiplicative'].plot(ax=ax, color='red')
        self.y_hat_avg['additive-dam'].plot(ax=ax, color='green')
        self.y_hat_avg['multiplicative-dam'].plot(ax=ax, color='orange')
        plt.show()

    def validate_results(self):
        # compute the RMSE and R^2,the closer to 1,more stable
        validates = pd.DataFrame(
            index=[r"$\alpha$", r"$\beta$", r"$\phi$", r"$\gamma$", r"$\l_0", r"$\b_0", r"$\SSE$",
                   r"$\RMSE$", "R-square"])
        params = ['smoothing_level', 'smoothing_slope', 'damping_slope', 'smoothing_seasonal', 'initial_level',
                  'initial_slope']
        validates['additive'] = [self.fits[0].params[p] for p in params] + [self.fits[0].sse] + [
            sqrt(mean_squared_error(self.test['Count'], self.y_hat_avg[
                'additive']))] + [r2_score(self.test['Count'], self.y_hat_avg['additive'])]
        validates['multiplicative'] = [self.fits[1].params[p] for p in params] + [self.fits[1].sse] + [
            sqrt(mean_squared_error(self.test['Count'], self.y_hat_avg[
                'multiplicative']))] + [r2_score(self.test['Count'], self.y_hat_avg['multiplicative'])]
        validates['additive-dam'] = [self.fits[2].params[p] for p in params] + [self.fits[2].sse] + [
            sqrt(mean_squared_error(self.test['Count'], self.y_hat_avg[
                'additive-dam']))] + [r2_score(self.test['Count'], self.y_hat_avg['additive-dam'])]
        validates['multiplicative-dam'] = [self.fits[3].params[p] for p in params] + [self.fits[3].sse] + [
            sqrt(mean_squared_error(self.test['Count'], self.y_hat_avg[
                'multiplicative-dam']))] + [r2_score(self.test['Count'], self.y_hat_avg['multiplicative-dam'])]
        return validates

    # ----------generate the best model
    def best_model(self):
        ls = ['additive', 'multiplicative', 'additive-dam', 'multiplicative-dam']
        r2 = self.validates.loc['R-square']
        r2_col = r2[r2 == r2.max()].index
        return self.fits[ls.index(r2_col[0])]

    # ----------generate the predict data
    def predict(self, forecast_periods):
        return self.best_fit.forecast(forecast_periods)

