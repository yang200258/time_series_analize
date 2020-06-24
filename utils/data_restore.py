import datetime
import time

# from data.warningData import getWarningData, mc_formal, ds
import data.warningData as wd
from utils.timedata import cal_month, cal_week, now_year, cal_year
import utils.util as ut


def restore_warn_database():
    is_restore = True
    for m in range(cal_month):
        for i in range(cal_week):
            start_week_date = [time.strftime("%Y-%m-%d", time.strptime('%s-%s-1' % (x, i), '%Y-%U-%w'))
                               for x in range(cal_year, now_year + 1)]
            end_week_date = [((datetime.datetime.strptime(
                time.strftime("%Y-%m-%d", time.strptime('%s-%s-6' % (x, i), '%Y-%U-%w')),
                "%Y-%m-%d") + datetime.timedelta(days=+1)
                               ).strftime("%Y-%m-%d")) for x in range(cal_year, now_year + 1)]
            five_data_formal, three_data_formal, dis_ls_formal = wd.getWarningData(wd.mc_formal, wd.ds, cal_year, m,
                                                                                start_week_date, end_week_date)
            ut.generalWarn(wd.mc_formal, five_data_formal, three_data_formal, dis_ls_formal, i+1, is_restore)


if __name__ == '__main__':
    restore_warn_database()
