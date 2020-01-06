import random
import threading
import time
from queue import Queue

import numpy as np
from baseClass.baseMysql import MysqlConn

ds = ['痢疾', '登革热', '丙肝', '戊肝', '乙肝', '百日咳', '淋病', '梅毒', '流行性感冒',
      '流行性腮腺炎', '风疹', '急性出血性结膜炎', '手足口病', '其它感染性腹泻病']
ls = []


def xxx():
    mc = MysqlConn('mysql-ali')
    for i in range(100):
        y = str(random.randint(2015, 2019))
        m = str(random.randint(1, 12))
        d = str(random.randint(1, 28))
        data_str = '''%s-%s-%s''' % (y, m, d)
        name = np.random.choice(ds)
        ls.append((data_str, name))
    print("循环完成")
    sql = '''insert into t_card_infection(ACCIDENT_DATE, DISEASE_NAME)
                            values(str_to_date(%s,'%%Y-%%m-%%d'), %s)'''
    mc.insertMany(sql, ls)


q=Queue(maxsize=10)

start = time.time()
for x in range(10):
    t = threading.Thread(target=xxx)
    q.put(t)
    if q.qsize() == 10:
        join_thread = []
        while not q.empty():
            t = q.get()
            join_thread.append(t)
            t.start()
        for t in join_thread:
            t.join()

end = time.time() - start
print(end)
# sql = "select * from t_card_infection"
# res = mc.select(sql)
