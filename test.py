import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from statsmodels.tsa.api import ExponentialSmoothing, statespace
from sklearn.metrics import mean_squared_error, r2_score
from math import sqrt
import itertools
import warnings
plt.style.use('fivethirtyeight')
warnings.filterwarnings('ignore')


# aggregating dataFrame by the resample
def aggregating(dataFrame):
    dataFrame['timestamp'] = pd.to_datetime(dataFrame['Datetime'], format="%d-%m-%Y %H:%M")
    dataFrame.index = dataFrame['timestamp']
    return dataFrame.resample('D').mean()


def dic_key(dic):
    return dic['AIC']


# import data and deal it
df = pd.read_csv('train.csv', nrows=11856)
train = df[:10392]
test = df[10392:]
# aggregating
df = aggregating(df)
train = aggregating(train)
test = aggregating(test)
# ------------                                plot the trend pic                               -------------------------

# plot the train and test data
train.Count.plot(figsize=(15, 8), title="train data", fontsize=14)
test.Count.plot(figsize=(15, 8), title="test data", fontsize=14)
# show the plot
plt.show()



# copy the test data
y_hat_avg = test.copy()

# fit the model
fit1 = ExponentialSmoothing(np.asarray(train['Count']), seasonal_periods=7, trend='add', seasonal='add') \
    .fit()
fit2 = ExponentialSmoothing(np.asarray(train['Count']), seasonal_periods=7, trend='add', seasonal='mul') \
    .fit()
fit3 = ExponentialSmoothing(np.asarray(train['Count']), seasonal_periods=7, trend='add', seasonal='add', damped=True) \
    .fit()
fit4 = ExponentialSmoothing(np.asarray(train['Count']), seasonal_periods=7, trend='add', seasonal='mul', damped=True) \
    .fit()

# assign the forecast value to y_hat_avg
y_hat_avg['additive'] = fit1.forecast(len(test))
y_hat_avg['multiplicative'] = fit2.forecast(len(test))
y_hat_avg['additive-dam'] = fit3.forecast(len(test))
y_hat_avg['multiplicative-dam'] = fit4.forecast(len(test))

# plot
ax = train['Count'].plot(figsize=(15, 8), label="observed", title="Holt-Winter model forecast")
test['Count'].plot(ax=ax, label="test data", color="red")
y_hat_avg['additive'].plot(ax=ax, color='blue')
y_hat_avg['multiplicative'].plot(ax=ax, color='red')
y_hat_avg['additive-dam'].plot(ax=ax, color='green')
y_hat_avg['multiplicative-dam'].plot(ax=ax, color='orange')

plt.show()

# compucate the RMSE and R^2,the closer to 1,more stable
results = pd.DataFrame(index=[r"$\alpha$", r"$\beta$", r"$\phi$", r"$\gamma$", r"$\l_0", r"$\b_0", r"$\SSE$",
                              r"$\RMSE$", r"$\R-square"])
params = ['smoothing_level', 'smoothing_slope', 'damping_slope', 'smoothing_seasonal', 'initial_level', 'initial_slope']

results['additive'] = [fit1.params[p] for p in params] + [fit1.sse] + [sqrt(mean_squared_error(test['Count'], y_hat_avg[
    'additive']))] + [r2_score(test['Count'], y_hat_avg['additive'])]
results['multiplicative'] = [fit2.params[p] for p in params] + [fit2.sse] + [
    sqrt(mean_squared_error(test['Count'], y_hat_avg[
        'multiplicative']))] + [r2_score(test['Count'], y_hat_avg['multiplicative'])]
results['additive-dam'] = [fit3.params[p] for p in params] + [fit3.sse] + [
    sqrt(mean_squared_error(test['Count'], y_hat_avg[
        'additive-dam']))] + [r2_score(test['Count'], y_hat_avg['additive-dam'])]
results['multiplicative-dam'] = [fit4.params[p] for p in params] + [fit4.sse] + [
    sqrt(mean_squared_error(test['Count'], y_hat_avg[
        'multiplicative-dam']))] + [r2_score(test['Count'], y_hat_avg['multiplicative-dam'])]

# ------------                                ARIMA forecast model             -------------------------
y_hat_avg = test.copy()
p = d = q = range(0, 2)
pdq = list(itertools.product(p, d, q))
seasonal_pdq = [(x[0], x[1], x[2], 7) for x in pdq]
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


best_model = min(res_data, key=dic_key)
final_model = statespace.SARIMAX(train['Count'], order=best_model['order'], seasonal_order=best_model['seasonal_order'],
                                 enforce_stationarity=False, enforce_invertibility=False)

results = final_model.fit()
print(results.summary().tables[1])
# plot the validate pic
results.plot_diagnostics(figsize=(15, 12))
plt.show()

# ---------static validate forecast

# predict the model value
pred = results.get_prediction(start=pd.to_datetime('2013-11-01'), end=pd.to_datetime('2013-12-31'), dynamic=False)
pred_ci_static = pred.conf_int()
# plot
ax = train['Count'].plot(figsize=(15, 8), label="observed", title="static validate forecast")
test['Count'].plot(ax=ax, label="test data", color="red")
pred.predicted_mean.plot(ax=ax, label="the static predict value by ARIMA model", alpha=.7)
ax.fill_between(pred_ci_static.index, pred_ci_static.iloc[:, 0], pred_ci_static.iloc[:, 1], color="k", alpha=.2)
plt.legend()
plt.show()
# compute the MSE
y_forecast = pred.predicted_mean
mse = ((y_forecast - test['Count']) ** 2).mean()

# -----------dynamic validate forecast

pred_dynamic = results.get_prediction(start=pd.to_datetime('2013-11-01'), end=pd.to_datetime('2013-12-31'),
                                      dynamic=True, full_results=True)
pred_dynamic_ci = pred_dynamic.conf_int()
# plot
ax = train['Count'].plot(figsize=(15, 8), label="observed", title="dynamic validate forecast")
# test['Count'].plot(ax=ax, label="test data", color="red")
pred_dynamic.predicted_mean.plot(ax=ax, label="the dynamic predict value by ARIMA model")
ax.fill_between(pred_dynamic_ci.index, pred_dynamic_ci.iloc[:, 0], pred_dynamic_ci.iloc[:, 1], color="k", alpha=.25)
plt.legend()
plt.show()
# compute the MSE
y_forecasted_dynamic = pred_dynamic.predicted_mean
mse_dynamic = ((y_forecasted_dynamic - test['Count']) ** 2).mean()

# ----------generate the predict data

pred_uc = results.get_forecast(steps=365)
pred_ci = pred_uc.conf_int()
ax = df['Count'].plot(figsize=(20, 15), label="observed", title="final forecast")
pred_uc.predicted_mean.plot(ax=ax, label="predict value by ARIMA model")
ax.fill_between(pred_ci.index, pred_ci.iloc[:, 0], pred_ci.iloc[:, 1], color="k", alpha=.25)
plt.legend()
plt.show()

