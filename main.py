# _*_ coding: utf-8 _*_
import unittest
from logger import Logger
import method
import requests
from ddt import ddt,data,unpack

#file_path =  os.path.dirname(os.getcwd()) + '/api_flask/excel/test.xlsx'
#data_path = 'D:/python/apitest0413/excel/data.xlsx'

#dict_cache_sheet = {'学历':'pccredit.zx_user_history'}

mylogger = Logger('testlog').getlog()

dataTest = method.get_api_list()
mylogger.info(dataTest)
@ddt
class MyTestSuite(unittest.TestCase):
    def setUp(self):
        mylogger.info('正在初始化当前测试用例')
        self.account = 'apisunsuwei'
        self.privatekey = '9355d0e7b4c67233'
        self.reqTid = '1234'
        self.reqId = '1234'
        self.md5_base_dict = {'account':self.account,'reqTid':self.reqTid,'reqId':self.reqId}
        mylogger.info(self.md5_base_dict)

    @data(*dataTest)
    @unpack
    def test_cache(self,id,url_name,url,request_method,params_from_sql,type,md5_params,url_params,cache_table):
        mylogger.info('正在执行的是第%s个接口:%s，查询缓存'%(id,url_name))
        #flag = 0
        if cache_table:
            sql_data = method.get_cache(cache_table,params_from_sql)
        else:
            mylogger.info('无缓存表。。。')
        md5_fn_dict = {}
        md5List = md5_params.split(',')
        md5_dict = dict(self.md5_base_dict.items()+sql_data.items())
        for k,v in md5_dict.items():
            if k in md5List:
                md5_fn_dict[k] = v
        md5_dict_bf_sort = sorted(md5_fn_dict.items())
        md5_str = ''
        for i in range(len(md5_dict_bf_sort)):
            for j in range(len(md5_dict_bf_sort[i])):
                md5_str = md5_str + md5_dict_bf_sort[i][j]
        mylogger.info("md5排序后的值为：=============%s"%md5_str)
        md5_str = md5_str + self.privatekey
        sign = method.md5(md5_str)
        urlParamsList = url_params.split(',')
        requests_dict = {'sign':sign}
        for k,v in md5_dict.items():
            if k in urlParamsList:
                requests_dict[k] = v
        if request_method == 'get':
            mylogger.info('正在发送get请求:%s'%url)
            url = 'http://192.168.100.35:7180'+url
            r = requests.get(url,requests_dict)
        elif self.request_method == 'post':
            r = requests.post(url,requests_dict)
        else:
            mylogger.info('只支持get和post方法！')
        statusCode = r.status_code
        mylogger.info('返回码statusCode为：================%s'%statusCode)
        self.assertEqual(200,statusCode,'验证失败......返回码不对')

    #测试访问上游数据源
    @data(*dataTest)
    @unpack
    def test_data_source(self,id,url_name,url,request_method,params_from_sql,type,md5_params,url_params,cache_table):
        mylogger.info('正在执行的是第%s个接口:%s，查询上游数据源' % (id, url_name))
        # flag = 0
        if cache_table:
            #从cache_table拿取已过期的数据，暂时未写该功能
            sql_data = method.get_noCache(cache_table, params_from_sql,cache_date='2018-03-01')
        else:
            mylogger.info('无缓存表。。。')
        md5_fn_dict = {}
        md5List = md5_params.split(',')
        md5_dict = dict(self.md5_base_dict.items() + sql_data.items())
        for k, v in md5_dict.items():
            if k in md5List:
                md5_fn_dict[k] = v
        md5_dict_bf_sort = sorted(md5_fn_dict.items())
        md5_str = ''
        for i in range(len(md5_dict_bf_sort)):
            for j in range(len(md5_dict_bf_sort[i])):
                md5_str = md5_str + md5_dict_bf_sort[i][j]
        mylogger.info("md5排序后的值为：=============%s" % md5_str)
        md5_str = md5_str + self.privatekey
        sign = method.md5(md5_str)
        urlParamsList = url_params.split(',')
        requests_dict = {'sign': sign}
        for k, v in md5_dict.items():
            if k in urlParamsList:
                requests_dict[k] = v
        if request_method == 'get':
            mylogger.info('正在发送get请求:%s' % url)
            url = 'http://192.168.100.35:7180' + url
            r = requests.get(url, requests_dict)
        elif self.request_method == 'post':
            r = requests.post(url, requests_dict)
        else:
            mylogger.info('只支持get和post方法！')
        statusCode = r.status_code
        mylogger.info('返回码statusCode为：================%s' % statusCode)
        self.assertEqual(200, statusCode, '验证失败......返回码不对')



    def tearDown(self):
        pass

