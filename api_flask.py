# _*_ coding: utf-8 _*_
import MySQLdb
from flask import Flask,request,session,g,redirect,url_for,abort,render_template,flash,jsonify
from main import MyTestSuite_1,MyTestSuite_2
import unittest
from logger import Logger
import method
import send_email as se
import time,os
import HTMLTestRunner
import math
from flask_restful import Resource,Api
import json

mylogger = Logger('Flask').getlog()
#configuration
DATABASE_IP = '192.168.100.35:3306'
DATABASE = 'test'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = '123'

app = Flask(__name__)
app.config.from_object(__name__)
api = Api(app)

#restful start=========
@app.route('/data-service/<path:path>', methods=['GET','POST'])
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
            par = req.split('=')[0]
            par_data = req.split('=')[1]
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

    else:
        return u'还没写post'



#restful over==========

def connect_db():
    return MySQLdb.connect('192.168.100.35','wangjia','wangjia123',DATABASE,charset = 'utf8')


@app.route('/add',methods = ['GET','POST'])
def add_entry():
    mylogger.info('进入add_entry()方法')
    if not session.get('logged_in'):
        abort(401)
    mylogger.info('url_name:%s'%request.form['url'])
    cur = g.db.cursor()
    cur.execute("insert into test.api_list (url_name,url,method,params_from_sql,type,md5_params,url_params,cache_table) values('%s','%s','%s','%s','%s','%s','%s','%s')"%(request.form['url_name'],request.form['url'],request.form['method'],request.form['params_from_sql'],request.form['type'],request.form['md5_params'],request.form['url_params'],request.form['cache_table']))
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('start_test'))

@app.route('/add_mock_list',methods=['GET','POST'])
def add_mock_list():
    mylogger.info('进入add_mock_list')
    if not session.get('logged_in'):
        abort(401)
    date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    cur = g.db.cursor()
    d_json = request.form['res_data']
    #d_json = json.dumps(d)
    tsql =  "insert into test.mock_list (date,url_name,url,req_form,method,req_data,req_blob) values('%s','%s','%s','%s','%s','%s','{json}')" % (
        date, request.form['url_name'], request.form['url_path'], request.form['req_form'],
        request.form['req_method'], request.form['req_data'] )
    mylogger.info(tsql)
    sql = tsql.format(json=MySQLdb.escape_string(d_json))
    cur.execute(sql)
    g.db.commit()
    return redirect(url_for('mock_test'))

@app.route('/login',methods = ['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('main'))
    return render_template('login.html',error=error)

@app.route('/main',methods = ['GET','POST'])
def main():
    mylogger.info('来到了主界面===========================')
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    cur = g.db.cursor()
    cur.execute('select id,date,status,report from test_history order by id asc')
    entries = [dict(id=row[0], date=row[1], status=row[2], report=row[3]) for row in cur.fetchall()]
    return render_template('main.html',entries=entries)

@app.route('/test_history',methods=['POST','GET'])
def test_history():
    mylogger.info('来到了测试历史记录页面===================')
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    p = request.args.get('p', '1')
    limit_start = (int(p) - 1) * 10
    history = method.get_history_list(limit_start)
    testList = []
    a = 1
    for row in history:
        testList.append(dict(date=row[0], status=row[1], pass_num=row[2], fail_num=row[3], report=row[4],history_id =a))
        a += 1
    #testList = [dict(date=row[0], status=row[1], pass_num=row[2], fail_num=row[3], report=row[4]) for row in history]
    history_list = len(history)
    page_sum_bf = float(history_list) / 10
    page_sum_l = math.modf(page_sum_bf)
    mylogger.info(page_sum_l)
    pageNum = int(page_sum_l[1]) + 1
    page_dic = list(range(1, pageNum + 1))
    mylogger.info(testList)
    return render_template('test_history.html',testList=testList,page_num=page_dic,p=int(p))

@app.route('/start_test',methods=['POST','GET'])
def start_test():
    mylogger.info('来到了start_test页面=========================')
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    p = request.args.get('p','1')
    select_value = request.args.get('select_value')
    mylogger.info('获取到的select_value为：%s'%select_value)
    mylogger.info('当前展示第%s页数据'%p)
    apiNum = method.get_page()
    mylogger.info("总共有%s个api"%apiNum)
    page_sum_bf = float(apiNum)/10
    page_sum_l = math.modf(page_sum_bf)
    mylogger.info(page_sum_l)
    pageNum = int(page_sum_l[1])+1
    mylogger.info("================当前的页数为%s========="%p)
    mylogger.info("===============应分为%s页============="%pageNum)
    limit_start = (int(p)-1)*10
    page_dic = list(range(1,pageNum+1))
    cur = g.db.cursor()
    sql = 'select id,url_name,url,cache_table from api_list limit {0},10'.format(limit_start)
    #cur.execute('select url_name,url from api_list order by id desc')
    cur.execute(sql)
    listApis = [dict(id=row[0],url_name=row[1],url=row[2],cache_table=row[3]) for row in cur.fetchall()]
    mylogger.info(listApis)
    return render_template('start_test.html',listApis=listApis,page_dic=page_dic,p=int(p))

@app.route('/add_api',methods = ['GET','POST'])
def add_api():
    mylogger.info('来到了添加新接口界面=========================')
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('add_api.html')



@app.route('/start',methods=['GET'])
def start():
    mylogger.info('开始执行测试==================================')
    # suite = unittest.TestLoader().loadTestsFromTestCase(MyTestSuite)
    # suite = unittest.TestSuite([suite])
    # unittest.TextTestRunner(verbosity=2).run(suite)
    report_path = os.path.dirname(os.path.abspath('.')) + '/apiTest/report/'
    now = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    HtmlFile = report_path + now + 'HTMLtemplate.html'
    fp = file(HtmlFile, 'wb')
    suite1 = unittest.TestLoader().loadTestsFromTestCase(MyTestSuite_1)
    suite2 = unittest.TestLoader().loadTestsFromTestCase(MyTestSuite_2)
    suite = unittest.TestSuite([suite1, suite2])
    runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title=u"测试报告", description=u"用例测试情况")
    test_result = runner.run(suite)
    all_num = test_result.testsRun
    fail_num = len(test_result.failures)
    # for case, reason in test_result.failures:
    #     print case.id()
    #     print reason
    fp.close()
    report = se.new_report(report_path)
    se.send_mail(report)
    method.insert_to_table(all_num,fail_num,report)
    return redirect(url_for('test_history'))

@app.route('/ready_to_start',methods=['GET'])
def ready_to_start():
    mylogger.info('来到了准备开始测试界面=========================')
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('ready_to_start.html')

#Mock测试
@app.route('/mock_test',methods=['GET','POST'])
def mock_test():
    mylogger.info('来到了Mock测试界面=========================')
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    #分页和查库
    p = request.args.get('p', '1')
    limit_start = (int(p) - 1) * 10
    mockList_bf = method.get_mock_data(limit_start)
    testList = []
    a = 1
    for row in mockList_bf:
        testList.append(dict(url_name=row[0], url_path=row[1], req_blob=str(row[2]), history_id=a))
        a += 1
    history_list = len(mockList_bf)
    #分页
    page_sum_bf = float(history_list) / 10
    page_sum_l = math.modf(page_sum_bf)
    mylogger.info(page_sum_l)
    pageNum = int(page_sum_l[1]) + 1
    page_dic = list(range(1, pageNum + 1))
    mylogger.info(testList)
    return render_template('mock_test.html',mockList=testList,pageNum=page_dic,p=int(p))

@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    flash('You were logged out')
    return redirect(url_for('login'))

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

if __name__ == '__main__':
    app.run(debug=True)
