import time

from baseClass.baseMysql import MysqlConn

mc = MysqlConn('mysql-ali')
mc_test = MysqlConn('mysql-test-warning')

sql_verified = '''select title_cal,TYPE_YEAR_CODE,TYPE_TIME_CODE,DISEASE_CODE,WARNING_TIME,warning_state from t_infect_t_distribution_warning 
                            where warning_state <> 0'''
verified_res = list(mc_test.getAll(sql_verified))
lss = {}
str = '2@2020-01-17 00:02:05'
print(str.split('@'))
for item in verified_res:
    lss["%s-%s-%s-%s" % (item[0], item[1], item[2], item[3])] = "%s@%s" % (item[5], item[4])
if lss.setdefault('2', 0):
    print('222')
else:
    print('111')
now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
sql = '''insert into test(name,date,create_time,num,num1,num2) values(%s,str_to_date(%s,'%%Y-%%m-%%d %%H:%%i:%%s'),
            str_to_date(%s,'%%Y-%%m-%%d %%H:%%i:%%s'),%s,%s,%s) 
            on duplicate key update num1=values(num1),num2=values(num2),num=if(values(num1)<values(num2),0,%s)
            '''

ls = [('n1', now, now, 0, 40, 99, None), ('n2', now, now, 1, 5, 4, None), ('n3', now, now, 1, 8, 7, None)]

mc.insertMany(sql, ls)
