import configparser
import os


class Config(object):
    """获取配置文件内容类"""
    def __init__(self, config_filename="setting.ini"):
        """初始化路径及文件名
        os.path.dirname(__file__): 返回运行文件时当前路径
        os.path.join： 连接当前路径与配置文件名，获得最终文件全路径
        """
        file_path = os.path.join(os.path.dirname(__file__), config_filename)
        self.cf = configparser.ConfigParser()
        self.cf.read(file_path)

    def get_sections(self):
        """获取配置文件内的【】内容"""
        return self.cf.sections()

    def get_options(self, section):
        """获取制定【】下的key-value中的key配置项"""
        return self.cf.options(section)

    def get_content(self, section):
        """将获取的key匹配得到value，并组成对象形式
        self.cf.get(section, option)： 获取section【】下对应key的value值
        """
        result = {}
        for option in self.get_options(section):
            value = self.cf.get(section, option)
            result[option] = int(value) if value.isdigit() else value
        return result
