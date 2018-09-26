# _*_ coding: utf-8 _*_
import MySQLdb
import method
from logger import Logger
from flask import request,jsonify,session,abort,flash,url_for,redirect,g,render_template
import json,time,os,math

mylogger = Logger('views').getlog()

#添加接口到数据库
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

#添加接口页面
def add_mock_list():
    mylogger.info('进入add_mock_list')
    if not session.get('logged_in'):
        abort(401)
    date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    cur = g.db.cursor()
    d_json = request.form['res_data']
    tsql =  "insert into test.mock_list (date,url_name,url,req_form,method,req_data,req_blob) values('%s','%s','%s','%s','%s','%s','{json}')" % (
        date, request.form['url_name'], request.form['url_path'], request.form['req_form'],
        request.form['req_method'], request.form['req_data'] )
    mylogger.info(tsql)
    sql = tsql.format(json=MySQLdb.escape_string(d_json))
    cur.execute(sql)
    g.db.commit()
    return redirect(url_for('mock_test'))

#update mock详情
def update_mock_list():
    mylogger.info('进入update_mock_list方法')
    #date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    cur = g.db.cursor()
    ud_json = request.form['update_res_data']
    tsql = "update test.mock_list set url_name='%s',url='%s',req_form='%s',req_data='%s',req_blob='{json}' where id=%s"%(request.form['update_url_name'],request.form['update_url_path'],request.form['update_req_form'],request.form['update_req_data'],g_list_id)
    mylogger.info(tsql)
    sql = tsql.format(json=MySQLdb.escape_string(ud_json))
    cur.execute(sql)
    g.db.commit()
    return redirect(url_for('mock_test'))

#登录页面
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


#主页面
def main():
    mylogger.info('来到了主界面===========================')
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    cur = g.db.cursor()
    cur.execute('select id,date,status,report from test_history order by id asc')
    entries = [dict(id=row[0], date=row[1], status=row[2], report=row[3]) for row in cur.fetchall()]
    return render_template('main.html',entries=entries)


#测试历史记录
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


#开始测试页面
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


#添加新接口
def add_api():
    mylogger.info('来到了添加新接口界面=========================')
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('add_api.html')


#logout界面
def logout():
    session.pop('logged_in',None)
    flash('You were logged out')
    return redirect(url_for('login'))


#mock测试界面
def mock_test():
    mylogger.info('来到了Mock测试界面=========================')
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    #分页和查库
    p = request.args.get('p', '1')
    list_id_web = request.args.get('listId',None)
    mylogger.info('listId:%s'%list_id_web)
    limit_start = (int(p) - 1) * 10
    mockList_bf = method.get_mock_data(limit_start)
    testList = []
    a = 1
    for row in mockList_bf:
        testList.append(dict(url_name=row[0], url_path=row[1], req_blob=str(row[2]),list_id=int(row[3]),method=row[4],req_form=row[5],req_data=row[6],history_id=a))
        a += 1
    history_list = len(mockList_bf)
    #分页
    page_sum_bf = float(history_list) / 10
    page_sum_l = math.modf(page_sum_bf)
    mylogger.info(page_sum_l)
    pageNum = int(page_sum_l[1]) + 1
    page_dic = list(range(1, pageNum + 1))
    mylogger.info(testList)
    if list_id_web != None:
        mylogger.info('method==get,返回另一个界面')
        for mockApi in testList:
            mylogger.info(mockApi)
            mylogger.info('此次的list_id:%s'%mockApi['list_id'])
            if str(list_id_web) == str(mockApi['list_id']):
                global g_list_id
                g_list_id = mockApi['list_id']
                mylogger.info('找到了相同的list_id')
                json.dumps(mockApi)
                return jsonify(mockApi)
    else:
        return render_template('mock_test.html',mockList=testList,page_num=page_dic,p=int(p),list_id=list_id_web)
