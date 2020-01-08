import time

import pymysql
from DBUtils.PooledDB import PooledDB
from pymysql.cursors import DictCursor

from .config import Config


class BasePymysqlPool(object):
    """
        父类连接池，用于初始化数据库连接
    """

    def __init__(self, host, port, user, password, db_name):
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = str(password)
        self.db_name = db_name
        self.conn = None
        self.cursor = None


class MysqlConn(BasePymysqlPool):
    """
        MYSQL数据库对象，负责产生数据库连接 , 此类中的连接采用连接池实现获取连接对象：conn = Mysql.getConn()
                释放连接对象;conn.close()或del conn
    """
    __pool = None

    def __init__(self, conf_name=None):
        self.conf = Config().get_content(conf_name)
        super().__init__(**self.conf)
        self._conn = self.__getConn()
        self._cursor = self._conn.cursor()

    def __getConn(self):
        """
           @summary: 静态方法，从连接池中取出连接
           @return MySQLdb.connection
        """
        if MysqlConn.__pool is None:
            maxconnections = 15
            __pool = PooledDB(creator=pymysql,
                              maxconnections=maxconnections,
                              host=self.host,
                              user=self.user,
                              port=self.port,
                              password=self.password,
                              db=self.db_name,
                              use_unicode=True,
                              charset='utf8',
                              # cursorclass=DictCursor
                              )
        return __pool.connection()

    def getAll(self, sql, param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list(字典对象)/boolean 查询到的结果集
        """
        print('开始获取数据')
        start = time.time()
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchall()
        else:
            result = False
        end = time.time()
        print('获取数据共用时： %s' % (end - start))
        return result

    def getOne(self, sql, param=None):
        """
            @summary: 执行查询，并取出第一条
            @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
            @param param: 可选参数，条件列表值（元组/列表）
            @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchone()
        else:
            result = False
        return result

    def getMany(self, sql, num, param=None):
        """
            @summary: 执行查询，并取出num条结果
            @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
            @param num:取得的结果条数
            @param param: 可选参数，条件列表值（元组/列表）
            @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.executesql, param
        if count > 0:
            ret = self._cursor.fetchmany(num)
        else:
            ret = False
        return ret

    def insertMany(self, sql, values):
        """
            @summary: 向数据表插入多条记录
            @param sql:要插入的ＳＱＬ格式
            @param values:要插入的记录数据tuple(tuple)/list[list]
            @return: count 受影响的行数
        """
        count = self._cursor.executemany(sql, values)
        self._conn.commit()
        return count

    def __query(self, sql, param=None):
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        return count

    def update(self, sql, param=None):
        """
            @summary: 更新数据表记录
            @param sql: ＳＱＬ格式及条件，使用(%s,%s)
            @param param: 要更新的  值 tuple/list
            @return: count 受影响的行数
        """
        count = self.__query(sql, param)
        if count > 0:
            self._conn.commit()
        else:
            self._conn.rollback()
        return count

    def insert(self, sql, param=None):
        """
            @summary: 更新数据表记录
            @param sql: ＳＱＬ格式及条件，使用(%s,%s)
            @param param: 要更新的  值 tuple/list
            @return: count 受影响的行数
        """
        count = self.__query(sql, param)
        if count > 0:
            self._conn.commit()
        else:
            self._conn.rollback()
        return count

    def delete(self, sql, param=None):
        """
            @summary: 删除数据表记录
            @param sql: ＳＱＬ格式及条件，使用(%s,%s)
            @param param: 要删除的条件 值 tuple/list
            @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def begin(self):
        """
            @summary: 开启事务
        """
        self._conn.autocommit(0)

    def end(self, option='commit'):
        """
        @summary: 结束事务
        """
        if option == 'commit':
            self._conn.commit()
        else:
            self._conn.rollback()

    def dispose(self, isEnd=1):
        """
            @summary: 释放连接池资源
        """
        if isEnd == 1:
            self.end('commit')
        else:
            self.end('rollback')
        print("释放连接池资源 %s,%s" % (self.host, self.db_name))
        self._cursor.close()
        self._conn.close()

    def __del__(self):
        print("释放连接池资源 %s,%s" % (self.host, self.db_name))
        self._cursor.close()
        self._conn.close()
