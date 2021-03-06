# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time     : 2020/2/1 16:22
# @Author   : zky_wind
# @Email    : 475854688@qq.com
# @File     : test_withdraw.py
# @Software : PyCharm
import json
import unittest

from common.excel_handler import ExcelHandler
from common.logger_handler import logger
from common.request_handler import RequestHandler
from config.setting import config
from libs import ddt

# 读取数据
excel_handler = ExcelHandler(config.data_path)
data = excel_handler.get_data('case_withdraw')
login_data = excel_handler.get_data('case_login')[0]


@ddt.ddt
class TestRegister(unittest.TestCase):
    def setUp(self) -> None:
        # 初始化一个session会话
        self.request = RequestHandler()
        # 先登录一个账号
        self.res = self.request.visit(method=login_data['method'],
                                      url=config.host + login_data['url'],
                                      json=json.loads(login_data['data']),
                                      headers=json.loads(login_data['headers']))
        # 获取登录后的token
        self.token = "Bearer {}".format(self.res["data"]["token_info"]["token"])
        # 定义一个测试结果
        self.result = 'NT'

    def tearDown(self) -> None:
        # 关闭session会话
        self.request.close_session()

    @ddt.data(*data)
    def test_register(self, test_data):
        # 打印一个开始的logger信息
        logger.info("测试用例：{}执行中。。。".format(test_data['case_title']))
        # 获取headers
        headers = json.loads(test_data['headers'])
        # 除第一个case外，headers中更新token信息
        if test_data['case_id'] != 1:
            headers['Authorization'] = self.token
        # 访问接口，得到实际结果
        res = self.request.visit(method=test_data['method'],
                                 url=config.host + test_data['url'],
                                 json=json.loads(test_data['data']),
                                 headers=headers)
        # 进行断言
        try:
            self.assertEqual(json.loads(test_data['excepted_result'])['code'], res['code'])
            # 打印日志信息
            logger.info("测试用例：{}-OK".format(test_data["case_title"]))
            # 测试结果赋值Pass
            self.result = "Pass"
        except AssertionError as e:
            # 打印日志信息
            logger.info("测试用例：{}-Error，报错：{}".format(test_data['case_title'], e))
            # 测试结果赋值Fail
            self.result = "Fail"
            # 抛出异常
            raise e
        finally:
            # 将测试的实际结果写到excel表中
            excel_handler.change_cell(config.data_path, "case_withdraw",
                                      int(test_data['case_id']) + 1, 9,
                                      str(res))
            # 将测试结果写入excel表中
            excel_handler.change_cell(config.data_path, "case_withdraw",
                                      int(test_data['case_id']) + 1, 10,
                                      self.result)


if __name__ == '__main__':
    unittest.main()
