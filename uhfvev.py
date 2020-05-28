import time

from baseClass.baseMysql import MysqlConn

mc_formal = MysqlConn('mysql-formal-forecast')
now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
ls = [('2020', '02', '2020-02-01', 1928, 37, 1, str(now), str(now))]
sql = '''REPLACE into ifd_forecast_cal(UUID, CAL_YEAR, CAL_MONTH,CAL_DATE, MAX_FORECAST_COUNT, MIN_FORECAST_COUNT,
            IS_ACTIVE, CREATE_TIME, DEFAULT_TIME) 
            values(UUID(), %s, %s, str_to_date(%s,'%%Y-%%m-%%d'), %s, %s, %s, str_to_date(%s,'%%Y-%%m-%%d %%H:%%i:%%s')
            , str_to_date(%s,'%%Y-%%m-%%d %%H:%%i:%%s'))'''
mc_formal.insertMany(sql, ls)