import pymysql


class MysqlConn(object):
    def __init__(self, host="59.212.39.7", user="jcfx", password="Q@4Zc7zd2BAtx9$N", database="jcfx", charset="utf8"):
        self.conn = pymysql.connect(host=host, user=user, password=password, database=database, charset=charset)
        self.cursor = self.conn.cursor()

    def select(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def add(self, sql, T):
        # self.cursor.execute(sql)
        print(sql)
        print(T)
        effect_rows = self.cursor.executemany(sql, T)
        self.conn.commit()
        return effect_rows

    def __del__(self):
        self.cursor.close()
        self.conn.close()
