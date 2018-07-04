# _*_ coding: utf-8 _*_
import xlrd,xlwt,hashlib
import MySQLdb
from logger import Logger
import datetime

mylogger = Logger('Method_Log').getlog()

#从库中读取接口的list
def get_api_list():
    mylogger.info('正在获取apilist===============================================')
    db = MySQLdb.connect('192.168.100.35', 'wangjia', 'wangjia123', 'test', charset='utf8')
    cur = db.cursor()
    cur.execute(
        'select id,url_name,url,method,params_from_sql,type,md5_params,url_params,cache_table,expire_date from api_list order by id asc')
    #entries = ((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]) for row in cur.fetchall())
    result = cur.fetchall()
    mylogger.info('已经获取到apilist并返回=========================')
    return result


'''用于在excel中读取数据，暂时无用

def get_sheet_nrows(file_path):
    workbook = xlrd.open_workbook(file_path)
    sheetname = workbook.sheet_by_index(0)
    nrows = sheetname.nrows
    return nrows


# 将该行数据放在一个list里面
def get_data(file_path,i):
    workbook = xlrd.open_workbook(file_path)
    sheet_name = workbook.sheet_by_index(0)
    rows = sheet_name.row_values(i)
    return rows


# 得到每次的url
def get_url(file_path,i):
    url_list = get_data(file_path,i)
    url = url_list[1]
    return url


def get_method(file_path,i):
    url_list = get_data(file_path,i)
    method = url_list[2]
    return method


def get_params(file_path,i):
    url_list = get_data(file_path,i)
    params = url_list[3]
    return params


def get_url_name(file_path,i):
    url_list = get_data(file_path,i)
    url_name = url_list[4]
    return url_name


def get_type(file_path,i):
    url_list = get_data(file_path,i)
    type = url_list[5]
    return type


def get_data_from(file_path,i):
    url_list = get_data(file_path,i)
    data_from = url_list[6]
    return data_from


def get_sign_base(file_path,i):
    url_list = get_data(file_path,i)
    sign_base = url_list[7]
    return sign_base


def get_request_params(file_path,i):
    url_list = get_data(file_path,i)
    requestParams = url_list[8]
    return requestParams
    
'''

#拿取在缓存期之内的数据
def get_cache(dbAndtb,data_need):
    mylogger.info('正在从数据库中获取数据.......')
    db = dbAndtb.split('.')[0]
    tb = dbAndtb.split('.')[1]
    try:
        db = MySQLdb.connect('192.168.100.35','wangjia','wangjia123',db,charset='utf8')
    except Exception as e:
        print '没有获取到缓存库信息，当前用例执行失败'
    cursor = db.cursor()
    mylogger.info('正在从%s获取数据......'%dbAndtb)
    try:
        cursor.execute(('select %s from %s order by date desc limit 1')%(data_need,tb))
    except:
        mylogger.info('正在使用idt排序查询')
        cursor.execute(('select %s from %s order by idt desc limit 1') % (data_need, tb))
    sql_result = cursor.fetchall()
    dictSql = {}
    aList = data_need.split(',')
    for i in range(len(aList)):
        dictSql[aList[i]] = sql_result[0][i]
    return dictSql

#拿取在缓存期之外的数据，用于再次查询上游数据源
def get_noCache(dbAndtb,data_need,cache_date):
    mylogger.info('正在从数据库中获取数据.......')
    db = dbAndtb.split('.')[0]
    tb = dbAndtb.split('.')[1]
    try:
        db = MySQLdb.connect('192.168.100.35','wangjia','wangjia123',db,charset='utf8')
    except Exception as e:
        print e
    cursor = db.cursor()
    mylogger.info('正在从%s获取数据......'%dbAndtb)
    try:
        cursor.execute(('select %s from %s where date < %s order by date desc limit 1')%(data_need,tb,cache_date))
    except:
        mylogger.info('正在使用idt排序查询')
        try:
            #记得给日期加引号
            sql = ('select %s from %s where idt < "%s" order by idt desc limit 1') % (data_need, tb,cache_date)
            mylogger.info(sql)
            cursor.execute(sql)
        except e:
            mylogger.info(e.message)
    sql_result = cursor.fetchall()
    mylogger.info(sql_result)
    dictSql = {}
    aList = data_need.split(',')
    mylogger.info('data_need:%s'%data_need)
    mylogger.info(aList)
    for i in range(len(aList)):
        dictSql[aList[i]] = sql_result[0][i]
    return dictSql


def md5(str):
    mylogger.info('正在进行md5加密')
    m = hashlib.md5()
    m.update(str)
    sign = m.hexdigest()
    sign = sign.upper()
    return sign

#从api_list表里查看有多少条记录然后分页
def get_page():
    sql = 'select count(*) from test.api_list'
    db = MySQLdb.connect('192.168.100.35', 'wangjia', 'wangjia123', 'test', charset='utf8')
    cur = db.cursor()
    cur.execute(sql)
    result = cur.fetchone()
    apiNum = result[0]
    return apiNum

def date_trans(date):
    today = datetime.date.today()
    today_str = str(today).split('-')
    yyyy = today_str[0]
    mm = today_str[1]
    dd = today_str[2]
    if date == u'一个月':
        if int(mm) > 1:
            mm_new = int(mm[1]) - 1
            if mm_new >=10:
                expire_date = (yyyy+'-'+str(mm_new)+'-'+dd)
                return expire_date
            elif mm_new < 10:
                mm_new = '0'+str(mm_new)
                expire_date = (yyyy+'-'+mm_new+'-'+dd)
                return expire_date
        elif int(mm) == 1:
            yyyy_new = int(yyyy) - 1
            mm_new = 12
            expire_date = (str(yyyy_new)+'-'+str(mm_new)+'-'+dd)
            return expire_date
    elif date == u'本月':
        dd_new = '01'
        expire_date = (yyyy+'-'+mm+'-'+dd_new)
        return expire_date
    elif date == u'一年':
        yyyy_new = int(yyyy)-1
        expire_date = (str(yyyy_new)+'-'+mm+'-'+dd)
        return expire_date
    elif date == u'一天':
        expire_date = today_str
        return expire_date
    else:
        mylogger.info('存的有效期无效')

