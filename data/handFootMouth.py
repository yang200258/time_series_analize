from baseClass.baseMysqlPool import MysqlConn
import pandas as pd
from utils.util import aggregating


def getData(mc):
    sql = '''SELECT min(t.ONSET_DATE), sum(t.ONSET_NUMBER) as n
            from `ifd_onset_death_cal` t
            where t.IFD_CODE = 4000 and t.ONSET_YEAR > 2013
            GROUP BY YEAR(t.ONSET_DATE), month(t.ONSET_DATE), day(t.ONSET_DATE)
            ORDER BY YEAR(t.ONSET_DATE), month(t.ONSET_DATE), day(t.ONSET_DATE)'''
    res = mc.getAll(sql)

    labels = pd.DataFrame(res, columns=['Datetime', 'Count'])

    # labels['date'] = pd.to_datetime(labels['Datetime'], format="%Y-%m-%d").dt.normalize()

    # aggregate the data to M/3M/Year
    hfm_m = aggregating(labels, 'MS')
    hfm_test = hfm_m.iloc[-6:]
    hfm_train = hfm_m.iloc[0:-6]

    return hfm_test, hfm_train


mc_test = MysqlConn('mysql-test-forecast')
mc_formal = MysqlConn('mysql-formal-forecast')

hfm_test_test, hfm_train_test = getData(mc_test)
hfm_test_formal, hfm_train_formal = getData(mc_formal)

mc_formal.dispose()
mc_test.dispose()
# hfm_m['Datetime'] = pd.to_datetime(hfm_m.index)
# hfm_m = labels.set_index('Datetime')
# hfm_3m = aggregating(labels, 'Q', '%Y-%m-%d')
# hfm_y = aggregating(labels, 'A', '%Y-%m-%d')

