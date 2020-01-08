import datetime
import time

now = datetime.datetime.now()
now_year = now.year

cal_year = now_year - 5
cal_month = now.month
cal_week = now.isocalendar()[1]
year_list = [x for x in range(cal_year, now_year + 1)]
# years = [x for x in range(cal_year_five, now_year)]
start_week_date = [time.strftime("%Y-%m-%d", time.strptime('%s-%s-1' % (x, cal_week - 1), '%Y-%U-%w'))
                   for x in range(cal_year, now_year + 1)]
end_week_date = [((
        datetime.datetime.strptime(
            time.strftime("%Y-%m-%d", time.strptime('%s-%s-6' % (x, cal_week - 1), '%Y-%U-%w')), "%Y-%m-%d")
        + datetime.timedelta(days=+1)
).strftime("%Y-%m-%d")) for x in range(cal_year, now_year + 1)]
