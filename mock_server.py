# _*_ coding: utf-8 _*_
import MySQLdb
import method
from logger import Logger
from flask import request,jsonify
import json

mylogger = Logger('mock_server').getlog()

def get_url(path):
    mylogger.info('进入get_url')
    mock_list_all = method.get_mock_list()
    list_req_form = []
    list_req_data = []
    list_req_blob = []
    mylogger.info('url：%s'%path)
    len_mock = len(mock_list_all)
    count = 0
    for api in mock_list_all:
        count += 1
        mylogger.info(api)
        mylogger.info(api['url'])
        if api['url'] == path:
            mylogger.info('url和path相同')
            list_req_form.append(api['req_form'])
            list_req_data.append(api['req_data'])
            list_req_blob.append(api['req_blob'])
            break
        elif count == len_mock:
            return '没有找到相匹配的url'
        mylogger.info(count)
    #暂时用‘=’分割req_data
    mylogger.info(list_req_data)
    mylogger.info(list_req_blob)
    if request.method == 'GET':
        mylogger.info('method==GET')
        count_1 = 0
        for req in list_req_data:
            len_req_data = len(list_req_data)
            count_1 += 1
            if '=' in req:
                par = req.split('=')[0]
                par_data = req.split('=')[1]
            elif ':' in req:
                par = req.split(':')[0]
                par_data = req.split(':')[1]
            else:
                return '字符串截取失败。。。'
            url_req_data = request.args.get(par)
            mylogger.info(u'获取请求参数:%s'%url_req_data)
            mylogger.info(u'获取数据库中存储的请求参数：%s'%par_data)
            if url_req_data == par_data:
                mylogger.info(u'在库中找到了相同的参数')
                for mock_info in mock_list_all:
                    mylogger.info(mock_info)
                    mylogger.info('req_data:%s' % mock_info['req_data'])
                    if str(url_req_data) in str(mock_info['req_data']):
                        #json = {"resCode":"2010","resMsg":"身份验证成功","tid":"1035005015310118542372260","sign":"A74D2BFC07EFF29A597897E0BA48D427"}
                        #return jsonify(json)
                        mylogger.info('url中请求的参数在库中找到了匹配项')
                        text_blob = json.loads(mock_info['req_blob'])
                        return jsonify(text_blob)
                    else:
                        mylogger.info('与参数数据相匹配的api不是这个，继续查找下一个')
            elif count_1 == len_req_data:
                return '参数没找到相匹配的'
            else:
                mylogger.info('参数继续找下一个')
    elif request.method == 'POST':
        mylogger.info('method==POST')
        count_1 = 0
        for req in list_req_data:
            len_req_data = len(list_req_data)
            count_1 += 1
            par = req.split(':')[0]
            par_data = req.split(':')[1]
            post_data = request.form.to_dict()
            mylogger.info(u'获取请求参数:%s' % post_data)
            mylogger.info(u'获取数据库中存储的请求参数：%s' % par_data)
            if par in post_data:
                mylogger.info('在数据库中有匹配字段')
                if post_data[par] == par_data:
                    mylogger.info('在数据库中找到匹配字段的匹配值')
                    req_data_str = par + ':' + par_data
                    count_0 = 0
                    for api_list in mock_list_all:
                        count_0 += 1
                        if api_list['req_data'] == req_data_str:
                            mylogger.info('请求数据与数据库数据完全匹配,准备返回...')
                            text_blob = json.loads(api_list['req_blob'])
                            return jsonify(text_blob)
                        elif count_0 == len(mock_list_all):
                            return '未找到与完全匹配的mock数据'
                        else:
                            mylogger.info('该请求数据string与数据库string不匹配，继续查找下一个')
                else:
                    mylogger.info('字段匹配，值不匹配，下一个')
            elif count_1 == len_req_data:
                return ('没找到匹配的字段')
            else:
                mylogger.info('数据库存的字段不在post请求里，下一个')
    else:
        return '暂时只支持post和get方法'