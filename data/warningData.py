from baseClass.baseMysql import MysqlConn
from utils.timedata import cal_year, cal_month, start_week_date, end_week_date


mc = MysqlConn()
sql_year = '''SELECT min(t.ONSET_YEAR),sum(t.ONSET_NUMBER) as n
        from `ifd_onset_death_cal` t
        where t.IFD_CODE = 4000 and t.ONSET_YEAR >= %s
        GROUP BY YEAR(t.ONSET_DATE) ORDER BY YEAR(t.ONSET_DATE)''' % cal_year
sql_month = '''SELECT min(t.ONSET_YEAR),sum(t.ONSET_NUMBER) as n
        from `ifd_onset_death_cal` t
        where t.IFD_CODE = 4000 and month(t.ONSET_DATE) = %s and t.ONSET_YEAR >= %s
        GROUP BY YEAR(t.ONSET_DATE) ORDER BY YEAR(t.ONSET_DATE)''' % (cal_month, cal_year)
sql_week = '''SELECT min(t.ONSET_YEAR),sum(t.ONSET_NUMBER) as n from `ifd_onset_death_cal` t
        where t.IFD_CODE = 4000 and ((t.ONSET_DATE between '%s' and  '%s') or (t.ONSET_DATE between '%s' and  '%s') or 
        (t.ONSET_DATE between '%s' and  '%s') or (t.ONSET_DATE between '%s' and  '%s') or (t.ONSET_DATE between '%s' and
          '%s') or (t.ONSET_DATE between '%s' and '%s'))
        GROUP BY YEAR(t.ONSET_DATE) ORDER BY YEAR(t.ONSET_DATE)''' % (start_week_date[0], end_week_date[0],
                                                                      start_week_date[1], end_week_date[1],
                                                                      start_week_date[2], end_week_date[2],
                                                                      start_week_date[3], end_week_date[3],
                                                                      start_week_date[4], end_week_date[4],
                                                                      start_week_date[5], end_week_date[5])

res_year_five = mc.select(sql_year)
res_month_five = mc.select(sql_month)
res_week_five = mc.select(sql_week)

res_year_three = res_year_five[-4:]
res_month_three = res_month_five[-4:]
res_week_three = res_week_five[-4:]
# year_fiv


#
# labels = pd.DataFrame(res, columns=['Datetime', 'Count'])
# labels['date'] = pd.to_datetime(labels['Datetime'], format="%Y-%m-%d").dt.normalize()

# aggregate the data to M/3M/Year
# hfm_m = aggregating(labels, 'MS')
# hfm_test = hfm_m.iloc[-6:]
# hfm_train = hfm_m.iloc[0:-6]
