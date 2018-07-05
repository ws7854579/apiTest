# _*_ coding: utf-8 _*_
import MySQLdb
from flask import Flask,request,session,g,redirect,url_for,abort,render_template,flash
from main import MyTestSuite_1,MyTestSuite_2
import unittest
from logger import Logger
import method
import send_email as se
import time,os
import HTMLTestRunner
import math


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

def connect_db():
    return MySQLdb.connect('192.168.100.35','wangjia','wangjia123',DATABASE,charset = 'utf8')


@app.route('/add',methods = ['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    cur = g.db.cursor()
    cur.execute("insert into test.api_list (url_name,url,method,params_from_sql,type,md5_params,url_params,cache_table) values('%s','%s','%s','%s','%s','%s','%s','%s')"%(request.form['url_name'],request.form['url'],request.form['method'],request.form['params_from_sql'],request.form['type'],request.form['md5_params'],request.form['url_params'],request.form['cache_table']))
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('main'))

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
    app.run()