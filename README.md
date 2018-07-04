# apiTest
2018/07/02--sunsuwei</br>
1、前端使用了bootstrap，后端使用了python的flask框架，接口测试使用了requests</br>
2、数据库使用的mysql，每个缓存表都不一样，单独建了一个api_list表

### The first commit
1、点击开始测试可以产生测试报告并发送邮件</br>
2、可以查看已存在的接口list</br>
3、可以添加新的接口用例</br>
### 下个版本update:</br>
1、可以查看测试历史记录</br>
2、支持测试上游数据源</br>
2018/07/02--sunsuwei
### 2018/7/4--sunsuwei
修复了之前的一些bug导致用例无法执行</br>
### 2018/7/4--sunsuwei
增加了查询上游数据源的功能，api_list表添加了一个缓存表有效期字段：expire_date
