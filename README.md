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
增加了查询上游数据源的功能，api_list表添加了一个缓存表有效期字段：expire_date </br>
增加了查看测试历史的功能，新增test_history表
### 2018/7/5--sunsuwei
1、更改了页面布局--将接口list单独展示，新增准备开始界面</br>
2、添加测试IP和测试时间选项（页面布局），下次更新后台功能。
### 2018/7/6--sunsuwei
1、更改了mock测试页面</br>
2、新增了mock测试，功能还未写完
### 2018/7/13--sunsuwei
1、实现了mock功能（暂时只支持get）</br>
2、后续添加各个页面的搜索功能。
