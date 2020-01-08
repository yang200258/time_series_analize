import numpy as np
from scipy import stats


class WarningModel(object):
    def __init__(self, data_frame):
        self.data_frame = data_frame
        self.cal_frame = data_frame.copy()
        l = len(self.data_frame) - 1
        self.cal_frame.loc['mean'] = self.data_frame[:l].mean()
        self.cal_frame.loc['skew'] = self.data_frame[:l].skew()
        self.cal_frame.loc['std'], interval_list = \
            self.deal_cal_std_interval(self.data_frame[:l])
        self.cal_frame.loc['interval_up'] = [x for x in interval_list]
        self.cal_frame.loc['v'] = self.cal_frame.loc['std'] / self.cal_frame.loc['mean']
        self.cal_frame.fillna(0, inplace=True)

    def deal_cal_std_interval(self, data_frame):
        std_list = []
        interval_list = []
        for index in data_frame.columns:
            std, interval = self.cal_std_interval(data_frame[index])
            std_list.append(std)
            interval_list.append(interval)
        return std_list, interval_list

    @staticmethod
    def cal_std_interval(np_arr):
        list_data = np.array(np_arr)
        x_mean = float(np.mean(list_data))
        x_std = float(np.std(list_data))
        if x_mean == x_std == 0:
            interval = 0
        else:
            interval = int(stats.t.interval(0.95, len(list_data) - 1, x_mean, x_std)[1])
        return x_std, interval
