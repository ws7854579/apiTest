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
from flask_restful import Api
import json
import views,mock_server

mylogger = Logger('Flask').getlog()
#configuration
DATABASE_IP = '192.168.100.35:3306'
DATABASE = 'test'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = '123'

#全局变量
g_list_id = ''

app = Flask(__name__)
app.config.from_object(__name__)
api = Api(app)



def connect_db():
    return MySQLdb.connect('192.168.100.35','wangjia','wangjia123',DATABASE,charset = 'utf8')


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


@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

if __name__ == '__main__':
    app.add_url_rule('/data-service/<path:path>',view_func=mock_server.get_url,methods=['GET','POST'])
    app.add_url_rule('/add',view_func=views.add_entry,methods=['GET','POST'])
    app.add_url_rule('/add_mock_list',view_func=views.add_mock_list,methods=['GET','POST'])
    app.add_url_rule('/update_mock_list',view_func=views.update_mock_list,methods=['POST'])
    app.add_url_rule('/login',view_func=views.login,methods = ['GET','POST'])
    app.add_url_rule('/main',view_func=views.main,methods = ['GET','POST'])
    app.add_url_rule('/test_history',view_func=views.test_history,methods=['POST','GET'])
    app.add_url_rule('/start_test',view_func=views.start_test,methods=['POST','GET'])
    app.add_url_rule('/add_api',view_func=views.add_api,methods = ['GET','POST'])
    app.add_url_rule('/logout',view_func=views.logout)
    app.add_url_rule('/mock_test',view_func=views.mock_test,methods=['GET','POST'])
    app.run('0.0.0.0',port=10057,debug=True)
