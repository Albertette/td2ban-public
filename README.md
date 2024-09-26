
# 全境封锁2黑名单kook机器人
## 前期准备
首先请先下载 -[正式版](https://github.com/Albertette/td2ban-private/releases)-任意版本  
将其放置在一个某个文件夹内例如`*:\td2banbot\td2banbot-v*.*.exe`  
在同一文件夹内新建名为config与log的文件夹，在config文件夹内新建一个名为config的json文件  
例如`*:\td2banbot\log\` 此文件夹将存放每次提交的日志  
　　`*:\td2banbot\config\config.json` 此文件为配置文件需要进行编辑
## 如何使用
首先让我们打开刚刚创建的config.json文件   
<details>
<summary> <em>用什么打开? </em></summary>
Windows 自带的记事本或者其他文本编辑器  
</details> 

```
{
  "token": "你的kook机器人token",
  "rootid": ["机器人管理员kook-id（你的kook-id）", "机器人管理员2", "..."],
  "root_id": "机器人拥有者kook-id（你的kook-id）",
  "db_host": "数据库ip",
  "db_user": "数据库用户名",
  "db_pass": "数据库密码",
  "db_name": "数据库名称",
  "UBISOFT_EMAIL": "育碧账户",
  "UBISOFT_PASSW": "育碧密码",
  "channel_id_public": ["公共信息频道-ID", "公共信息频道2-ID", "..."],
  "channel_id_private": "特定权限的信息频道",
  "using_ws": true

}
``` 
按照此格式将内容填写完整  
***
### "token" 如何获取  

*如果没有则无法使用机器人**全部功能***  

进入[开发者后台-应用](https://developer.kookapp.cn/app/index)，点击右上角**创建应用**，即可创建一个新的机器人  

![image-20230525225030524](https://khl-py.eu.org/assets/img/image-20230525225030524.76fee368.png)  

填入应用名称（即机器人名称，后续还可以更改），点击**确定**，创建机器人  

![image-20230525225157075](https://khl-py.eu.org/assets/img/image-20230525225157075.6addb17b.png)  

![image-20230525225252746](https://khl-py.eu.org/assets/img/image-20230525225252746.4648518c.png)  

点击左侧  **机器人**  按钮，即可进入机器人 **token** 的页面。  

在此页面，你可以  
  
-   修改机器人的连接方式  
-   **获取机器人的token**  
-   是否开启公共机器人（若不开启，则只有机器人开发者可以邀请机器人到其他服务器）  

![image-20230525225334570](https://khl-py.eu.org/assets/img/image-20230525225334570.a84d3d9d.png)

***
### "rootid", "root_id" 如何获取  

*如果没有则无法使用机器人 **添加黑名单 && 拥有者独立拉黑(作案类型：个人) 功能***  
  
在kook客户端/网页版设置中，开启  `高级设置-开发者模式`  

![image-20230527214308521](https://khl-py.eu.org/assets/img/image-20230527214308521.cd459f00.png)

在公共频道聊天框，或者服务器用户列表，右键用户头像，复制ID  

### "channel_id_public", "channel_id_private" 如何获取  
*如果没有则无法使用机器人 **黑名单新增人员后自动公示的功能***  
`channel_id_public"`为`作案类型: 任意`的权限  
`channel_id_private`为`作案类型: 个人`的权限  
开启  `高级设置-开发者模式`  
右键频道，复制ID  
***
### "db_host",  "db_user", "db_pass", "db_name" 如何获取  
*如果没有则无法使用机器人 **数据库相关的所有功能***  
作者使用的是**mysql**数据库  

**db_host**数据库ip 如果是本机则填写**localhost**  
**db_user**数据库用户名 登录的用户名可以填**root**  
**db_pass**数据库密码   
**db_name**数据库名称  

**数据库字段**  
![enter image description here](https://github.com/Albertette/td2ban-private/blob/main/img/mysql-td2bantable.png)
***
### "UBISOFT_EMAIL",  "UBISOFT_PASSW 如何获取  
*如果没有则无法使用机器人 查询最新ID与查询uuid的功能*   
  
**UBISOFT_EMAIL** 为你的育碧登录邮箱  
**UBISOFT_PASSW** 为你的育碧登录密码  
*这边建议重新注册一个新的育碧账户，使用新账户来进行登录*  
因为使用此[siegeapi](https://github.com/CNDRD/siegeapi)需要您登录账户，并且作者**不保证是否会出现安全隐患**所以您建议使用**全新**的育碧账户  

***  
填写完成后双击`td2banbot-v*.*.exe`  
下面让我们来测试一下命令，看看是否成功启用了机器人  
 **记得先把机器人邀请至服务器哦**  
## 命令
**输入：/查询+{空格}+UUID**   
 `/查询 xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`   
 即可查询该玩家是否在黑名单里。  
   
  _不知道该玩家的UUID？_     
    
 **输入  ：/UUID+{空格}+当前游戏ID**    
   `/uuid *****` 即可查询该玩家的UUID以及是否在黑名单里。  
   
   *PS：黑名单的数据仅查询者可见，并在一定时间后消失* 
   
  至于其他功能慢慢摸索吧。
## 关于
本机器人基于[khl.py](https://github.com/TWT233/khl.py)与[siegeapi](https://github.com/CNDRD/siegeapi)开发
