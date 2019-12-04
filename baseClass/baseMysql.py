import pymysql


class MysqlConn(object):
    def __init__(self, host="10.0.16.177", user="root", password="root", database="jikong", charset="utf8"):
        self.conn = pymysql.connect(host=host, user=user, password=password, database=database, charset=charset)
        self.cursor = self.conn.cursor()

    def select(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def add(self, sql, T):
        # self.cursor.execute(sql)
        effect_rows = self.cursor.executemany(sql, T)
        self.conn.commit()
        return effect_rows

    def __del__(self):
        self.cursor.close()
        self.conn.close()
