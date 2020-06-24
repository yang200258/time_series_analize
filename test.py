# import os

from baseClass.baseMysqlPool import MysqlConnPool

if __name__ == "__main__":
    # print(os.path.dirname(__file__))
    mc_test = MysqlConnPool('mysql-host')
    # print(MysqlConn.__pool)

    mc_formal = MysqlConnPool('mysql-host')
    # print(MysqlConn.__pool)

    print(id(mc_test))
    print((id(mc_formal)))
