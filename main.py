import logging
from importlib import reload

from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.background import BlockingScheduler

from baseClass.baseMysql import MysqlConn
from data import warningData
from data.warningData import five_data_test, five_data_formal, three_data_test, three_data_formal, dis_ls_test, \
    dis_ls_formal

from utils.util import generalPred, generalWarn
import data.handFootMouth as handFootMouth
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='log.txt',
                    filemode='a')
scheduler = BlockingScheduler()


def my_listener(event):
    if event.exception:
        print('任务出现异常！')
    else:
        print('任务照常运行...')


scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
scheduler._logger = logging


@scheduler.scheduled_job('cron', month='1-12', day='1', hour='00', minute='2', second='0')
def hand_foot_mouth():
    reload(handFootMouth)
    print('Get the hand_foot_mouth disease forecast data.')
    mc_test = MysqlConn('mysql-test-forecast')
    mc_formal = MysqlConn('mysql-formal-forecast')

    generalPred(mc_test, handFootMouth.hfm_train_test, handFootMouth.hfm_test_test)
    generalPred(mc_formal, handFootMouth.hfm_train_formal, handFootMouth.hfm_test_formal)

    mc_test.dispose()
    mc_formal.dispose()


@scheduler.scheduled_job('cron', hour='00', minute='2', second='0')
def warning_disease():
    reload(warningData)
    mc_test = MysqlConn('mysql-test-warning')
    mc_formal = MysqlConn('mysql-formal-warning')

    generalWarn(mc_test, five_data_test, three_data_test, dis_ls_test)
    generalWarn(mc_test, five_data_formal, three_data_formal, dis_ls_formal)

    mc_test.dispose()
    mc_formal.dispose()


if __name__ == '__main__':
    with open('log.txt', 'a', encoding='utf8') as f:
        try:
            scheduler.start()
            f.write('任务运行成功!\n')
        except Exception:
            scheduler.shutdown()
            f.write('***********************任务运行失败!*****************************\n')
