import json
import re
import pymysql
import asyncio
import logging
from typing import Union
from datetime import datetime
from khl import *
from khl import Bot, Message, Event, ChannelPrivacyTypes
from khl.card import Card, CardMessage, Module, Types, Element, Struct
from khl import PrivateMessage, PublicMessage
from siegeapi import Auth, player


with open('.\\config\\config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)


# 创建新的事件循环
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

image_path = 'https://img.kookapp.cn/assets/2024-09/22/sEDwT4c2lU01c01c.png'
#备注.ico
bot = Bot(token=config['token'])
#bot_token注册


#--------管理员注册----------
rootid = config['rootid'] #管理员权限账户
root_id = config['root_id'] #机器人拥有者
#--------管理员注册----------

#---------数据库声明----------
DBHOST = config['db_host']
DBUSER = config['db_user']
DBPASS = config['db_pass']
DBNAME = config['db_name']
#---------数据库声明----------

last_checked_data = None

#---------日期声明----------
now = datetime.now()
date_only = now.date()
formatted_time = now.strftime('%Y-%m-%d %H:%M')
#---------日期声明----------

#---------临时变量声明----------
temp_uuid_msg_id = ''
temp_uuid_name = ''
temp_uuid_profile_pic_url = ''
temp_uuid_msg_author_id = ''
temp_uuid_uuid = ''
temp_uuid_tf = ''
temp_uuid_tf_tf = 'f'
temp_td2ban_msg_id = ''
#---------临时变量声明----------



# 封装数据库查询操作
def query_data_from_td2ban(guid):
    try:
        with pymysql.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME) as db:
            with db.cursor() as cur:
                cur.execute("use td2ban")
                sqlQuery = "SELECT * FROM td2ban WHERE uuid = %s"
                cur.execute(sqlQuery, (guid,))
                results = cur.fetchall()
                return results
    except pymysql.Error as e:
        print("数据库连接失败: " + str(e))
        return None

# 检查数据库是否有新数据插入
async def check_for_new_data():
    global last_checked_data
    while True:
        try:
            with pymysql.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME) as db:
                with db.cursor() as cur:
                    cur.execute("use td2ban")
                    cur.execute("SELECT * FROM td2ban")
                    current_data = cur.fetchall()
                    if last_checked_data is None:
                        last_checked_data = current_data
                    else:
                        new_data = [row for row in current_data if row not in last_checked_data]
                        if new_data:
                            for row in new_data:
                                name = row[0]
                                uuid = row[1]
                                type = row[2]
                                date = row[3]
                                remark = row[4]
                                img_ban1 = f'https://ubisoft-avatars.akamaized.net/{uuid}/default_256_256.png'
                                if type == '个人':
                                    newBAN = Card(
                                        Module.Header("欢迎新成员加入黑名单"),
                                        Module.Section(
                                            Element.Text(f"**(font)游戏ID(font)[warning]**\n(font){name}(font)[success]\n**(font)作案类型(font)[warning]**\n(font){type}(font)[success]", type=Types.Text.KMD),
                                            Element.Image(src=img_ban1, size=Types.Size.SM, circle=True),
                                            mode=Types.SectionMode.RIGHT
                                        ),
                                        Module.Section(Element.Text("**(font)育碧标识符(font)[warning]**", type=Types.Text.KMD), ),
                                        Module.Section(f"(font){uuid}(font)[success]"),
                                        Module.Section(Element.Text("**(font)登记日期(font)[warning]**", type=Types.Text.KMD), ),
                                        Module.Section(f"(font){date}(font)[success]"),
                                        Module.Section(Element.Text("**(font)备注(font)[warning]**", type=Types.Text.KMD), ),
                                        Module.Section(f"(font){remark}(font)[success]"),
                                        Module.Divider(),
                                        Module.Context(
                                            Element.Text(f"打印时间:{date_only} By Td2ban (QGE.)",type=Types.Text.KMD),
                                            Element.Image(src=image_path),
                                        ),
                                    )
                                    # 假设你有一个正确的方式来获取频道 ID，这里只是一个示例
                                    channel_id = config['channel_id_private']
                                    channel = await bot.client.fetch_public_channel(channel_id)
                                    await bot.client.send(channel, CardMessage(newBAN),)
                                else:
                                    newBAN1 = Card(
                                        Module.Header("欢迎新成员加入黑名单"),
                                        Module.Section(
                                            Element.Text(f"**(font)游戏ID(font)[warning]**\n(font){name}(font)[success]\n**(font)作案类型(font)[warning]**\n(font){type}(font)[success]", type=Types.Text.KMD),
                                            Element.Image(src=img_ban1, size=Types.Size.SM, circle=True),
                                            mode=Types.SectionMode.RIGHT
                                        ),
                                        Module.Section(Element.Text("**(font)育碧标识符(font)[warning]**", type=Types.Text.KMD),),
                                        Module.Section(f"(font){uuid}(font)[success]"),
                                        Module.Section(Element.Text("**(font)登记日期(font)[warning]**", type=Types.Text.KMD),),
                                        Module.Section(f"(font){date}(font)[success]"),
                                        Module.Section(Element.Text("**(font)备注(font)[warning]**", type=Types.Text.KMD),),
                                        Module.Section(f"(font){remark}(font)[success]"),
                                        Module.Divider(),
                                        Module.Context(
                                            Element.Text(f"打印时间:{date_only} By Td2ban (QGE.)",type=Types.Text.KMD),
                                            Element.Image(src=image_path),
                                        ),
                                    )
                                    # 假设你有一个正确的方式来获取频道 ID，这里只是一个示例
                                    for channel_id in config['channel_id_public']:
                                        channel = await bot.client.fetch_public_channel(channel_id)
                                        await bot.client.send(channel, CardMessage(newBAN1))
                            last_checked_data = current_data
        except pymysql.Error as e:
            print(f"数据库查询错误：{str(e)}")
        await asyncio.sleep(10)  # 每隔 10 秒检查一次，可以根据实际情况调整时间间隔

async def sample(gameid):
    UBISOFT_EMAIL = config['UBISOFT_EMAIL']
    UBISOFT_PASSW = config['UBISOFT_PASSW']
    auth = Auth(UBISOFT_EMAIL, UBISOFT_PASSW)
    player = await auth.get_player(name=gameid)
    await auth.close()
    return player.id, player.profile_pic_url, player.name

async def sample_uid(profileid):
    UBISOFT_EMAIL = config['UBISOFT_EMAIL']
    UBISOFT_PASSW = config['UBISOFT_PASSW']
    auth = Auth(UBISOFT_EMAIL, UBISOFT_PASSW)
    player = await auth.get_player(uid=profileid)
    await auth.close()
    return player.name

@bot.command(name='查询', aliases=['查詢'], case_sensitive=False)
async def search(msg: Message, guid: str):
    # 判断 guid 是否符合 GUID 标准
    if not re.match(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', guid):
        await msg.ctx.channel.send("输入的 UID 不符合标准格式\n请按照如下格式输入\n/查询 xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", temp_target_id=msg.author.id)
        return

    if isinstance(msg, PublicMessage):
        results = query_data_from_td2ban(guid)
        latest_name = await sample_uid(guid)
        if results:
            for row in results:
                name = row[0]
                uuid = row[1]
                type = row[2]
                date = row[3]
                remark = row[4]
                img_ban = f'https://ubisoft-avatars.akamaized.net/{uuid}/default_256_256.png'
                if type == '个人':
                    if root_id == msg.author.id:
                        searchBAN1 = Card(
                            Module.Header("查询内容如下"),
                            Module.Section(
                                Element.Text(f"**(font)登记ID(font)[warning]**\n(font){name}(font)[success]\n**(font)最新ID(font)[warning]**\n(font){latest_name}(font)[success]", type=Types.Text.KMD),
                                Element.Image(src=img_ban, size=Types.Size.SM, circle=True),
                                mode=Types.SectionMode.RIGHT
                            ),
                            Module.Section(Element.Text("**(font)育碧标识符(font)[warning]**", type=Types.Text.KMD), ),
                            Module.Section(f"(font){uuid}(font)[success]"),
                            Module.Section(Element.Text("**(font)作案类型(font)[warning]**", type=Types.Text.KMD), ),
                            Module.Section(f"(font){type}(font)[success]"),
                            Module.Section(Element.Text("**(font)登记日期(font)[warning]**", type=Types.Text.KMD), ),
                            Module.Section(f"(font){date}(font)[success]"),
                            Module.Section(Element.Text("**(font)备注(font)[warning]**", type=Types.Text.KMD), ),
                            Module.Section(f"(font){remark}(font)[success]"),
                            Module.Divider(),
                            Module.Context(
                                Element.Text(f"查询时间:{formatted_time} Search by Td2ban (QGE.)", type=Types.Text.KMD),
                                Element.Image(src=image_path),
                            ),
                            color='#B22222'
                        )
                        await msg.add_reaction('✅')
                        await msg.ctx.channel.send(CardMessage(searchBAN1), temp_target_id=msg.author.id)
                    else:
                        await msg.add_reaction('❌')
                        await msg.ctx.channel.send("未找到对应数据-ERR-NO.2", temp_target_id=msg.author.id)
                else:
                    searchBAN = Card(
                        Module.Header("查询内容如下"),
                        Module.Section(
                            Element.Text(f"**(font)登记ID(font)[warning]**\n(font){name}(font)[success]\n**(font)最新ID(font)[warning]**\n(font){latest_name}(font)[success]", type=Types.Text.KMD),
                            Element.Image(src=img_ban, size=Types.Size.SM, circle=True),
                            mode=Types.SectionMode.RIGHT
                        ),
                        Module.Section(Element.Text("**(font)育碧标识符(font)[warning]**", type=Types.Text.KMD), ),
                        Module.Section(f"(font){uuid}(font)[success]"),
                        Module.Section(Element.Text("**(font)作案类型(font)[warning]**", type=Types.Text.KMD), ),
                        Module.Section(f"(font){type}(font)[success]"),
                        Module.Section(Element.Text("**(font)登记日期(font)[warning]**", type=Types.Text.KMD), ),
                        Module.Section(f"(font){date}(font)[success]"),
                        Module.Section(Element.Text("**(font)备注(font)[warning]**", type=Types.Text.KMD), ),
                        Module.Section(f"(font){remark}(font)[success]"),
                        Module.Divider(),
                        Module.Context(
                            Element.Text(f"查询时间:{formatted_time} Search by Td2ban (QGE.)", type=Types.Text.KMD),
                            Element.Image(src=image_path),
                        ),
                        color = '#B22222'
                    )
                    await msg.add_reaction('✅')
                    await msg.ctx.channel.send(CardMessage(searchBAN), temp_target_id=msg.author.id)
        else:
            await msg.add_reaction('❌')
            await msg.ctx.channel.send("未找到对应数据ERR-NO.1", temp_target_id=msg.author.id)

@bot.command(name='uuid', aliases=['guid'], case_sensitive=False)
async def searchGuid(msg: Message, gameid: str):
    global temp_uuid_tf, temp_uuid_profile_pic_url, temp_uuid_name, temp_uuid_uuid, temp_uuid_msg_author_id
    if isinstance(msg, PublicMessage):
        tf = '数据异常'
        ty = '黑名单里有此玩家(font)[pink]'
        tn = '此玩家不在黑名单内(font)[success]'

        extracted_string, profile_pic_url, profile_ID = await sample(gameid)
        results = query_data_from_td2ban(extracted_string)

        if results:
            for row in results:
                type = row[2]
            if type == '个人':
                if root_id == msg.author.id:
                    tf = '黑名单里有此玩家(font)[pink]'
                else:
                    tf = '此玩家不在黑名单内(font)[success]'
            else:
                tf = '黑名单里有此玩家(font)[pink]'
        else:
            tf = '此玩家不在黑名单内(font)[success]'

        print(f"Extracted string: {extracted_string}")
        print(f"Profile pic URL: {profile_pic_url}")
        temp_uuid_tf = tf

        if tf == tn:
            if msg.author.id in rootid:
                uuidup = Card(
                    Module.Header("查询结果如下"),
                    Module.Section(
                        Element.Text(f"**(font)游戏ID(font)[warning]**\n(font){profile_ID}(font)[success]\n**(font)当前状态(font)[warning]**\n(font){tf}\n",type=Types.Text.KMD),
                        Element.Image(src=profile_pic_url, size=Types.Size.SM, circle=True), mode=Types.SectionMode.RIGHT),
                    Module.Section(
                        Element.Text(f"**(font)UUID(font)[warning]**\n(font){extracted_string}(font)[success]", type=Types.Text.KMD),
                        Element.Button("黑名单登记", value='黑名单登记', click=Types.Click.RETURN_VAL, theme=Types.Theme.INFO),

                    ),
                    Module.Divider(),
                    Module.Context(
                        Element.Text(f"查询时间:{formatted_time}", type=Types.Text.KMD),
                        Element.Image(src=image_path),
                    ),
                    color='#98FB98'
                )
                uuidup02 = Card(
                    Module.Header("查询结果如下"),
                    Module.Section(
                        Element.Text(f"**(font)游戏ID(font)[warning]**\n(font){profile_ID}(font)[success]\n**(font)当前状态(font)[warning]**\n(font){tf}\n", type=Types.Text.KMD),
                        Element.Image(src=profile_pic_url, size=Types.Size.SM, circle=True),
                        mode=Types.SectionMode.RIGHT),
                    Module.Section(
                        Element.Text(f"**(font)UUID(font)[warning]**\n(font){extracted_string}(font)[success]", type=Types.Text.KMD),
                        Element.Button("请重新获取", value='已失效', click=Types.Click.RETURN_VAL, theme=Types.Theme.SECONDARY),
                    ),
                    Module.Divider(),
                    Module.Context(
                        Element.Text(f"查询时间:{formatted_time}", type=Types.Text.KMD),
                        Element.Image(src=image_path),
                    ),
                    color='#98FB98'
                )
                temp_uuid_msg_author_id = msg.author.id
                temp_uuid_profile_pic_url = profile_pic_url
                temp_uuid_name = profile_ID
                temp_uuid_uuid = extracted_string

                res = await msg.reply(CardMessage(uuidup))
                await msg.add_reaction('✅')
                await asyncio.sleep(3600)
                await upd_msg(res['msg_id'], CardMessage(uuidup02), channel_type=ChannelPrivacyTypes.GROUP, bot=bot)
            else:
                uuidup1 = Card(
                    Module.Header("查询结果如下"),
                    Module.Section(
                        Element.Text(f"**(font)游戏ID(font)[warning]**\n(font){profile_ID}(font)[success]\n**(font)当前状态(font)[warning]**\n(font){tf}\n", type=Types.Text.KMD),
                        Element.Image(src=profile_pic_url, size=Types.Size.SM, circle=True), mode=Types.SectionMode.RIGHT),
                    Module.Section(
                        Element.Text(f"**(font)UUID(font)[warning]**\n(font){extracted_string}(font)[success]", type=Types.Text.KMD),
                        Element.Button("黑名单登记", value="暂无权限", click=Types.Click.RETURN_VAL, theme=Types.Theme.SECONDARY),
                    ),
                    Module.Divider(),
                    Module.Context(
                        Element.Text(f"查询时间:{formatted_time}", type=Types.Text.KMD),
                        Element.Image(src=image_path),
                    ),
                    color='#98FB98'
                )
                temp_uuid_msg_author_id = msg.author.id
                temp_uuid_profile_pic_url = profile_pic_url
                temp_uuid_name = profile_ID
                temp_uuid_uuid = extracted_string
                await msg.add_reaction('✅')
                await msg.reply(CardMessage(uuidup1))




        if tf == ty:
            for row in results:
                name = row[0]
                uuid = row[1]
                type = row[2]
                date = row[3]
                remark = row[4]
                img_ban2 = f'https://ubisoft-avatars.akamaized.net/{uuid}/default_256_256.png'
                uuidC = Card(
                    Module.Header("查询结果如下"),
                    Module.Section(
                        Element.Text(
                            f"**(font)游戏ID(font)[warning]**\n(font){profile_ID}(font)[success]\n**(font)当前状态(font)[warning]**\n(font){tf}\n",
                            type=Types.Text.KMD),
                        Element.Image(src=profile_pic_url, size=Types.Size.SM, circle=True),
                        mode=Types.SectionMode.RIGHT
                    ),
                    Module.Section("**(font)UUID(font)[warning]**"),
                    Module.Section(f"(font){extracted_string}(font)[success]"),
                    Module.Divider(),
                    Module.Context(
                        Element.Text(f"查询时间:{formatted_time}", type=Types.Text.KMD),
                        Element.Image(src=image_path),
                    ),
                    color='#8A2BE2'
                )
                await msg.add_reaction('✅')
                await msg.reply(CardMessage(uuidC))

                if type == '个人':
                    if msg.author.id == root_id:
                        searchBAN3 = Card(
                            Module.Section(Element.Text("**(font)登记ID(font)[warning]**", type=Types.Text.KMD), ),
                            Module.Section(f"(font){name}(font)[success]"),
                            Module.Section(Element.Text("**(font)育碧标识符(font)[warning]**", type=Types.Text.KMD), ),
                            Module.Section(f"(font){uuid}(font)[success]"),
                            Module.Section(Element.Text("**(font)作案类型(font)[warning]**", type=Types.Text.KMD), ),
                            Module.Section(f"(font){type}(font)[success]"),
                            Module.Section(Element.Text("**(font)登记日期(font)[warning]**", type=Types.Text.KMD), ),
                            Module.Section(f"(font){date}(font)[success]"),
                            Module.Section(Element.Text("**(font)备注(font)[warning]**", type=Types.Text.KMD), ),
                            Module.Section(f"(font){remark}(font)[success]"),
                            Module.Divider(),
                            Module.Context(
                                Element.Text(f"查询时间:{formatted_time} Search by Td2ban (QGE.)", type=Types.Text.KMD),
                                Element.Image(src=image_path),
                            ),
                            color='#B22222'
                        )
                        await msg.ctx.channel.send(CardMessage(searchBAN3), temp_target_id=msg.author.id)

                else:
                    searchBAN2 = Card(
                        Module.Section(Element.Text("**(font)登记ID(font)[warning]**", type=Types.Text.KMD), ),
                        Module.Section(f"(font){name}(font)[success]"),
                        Module.Section(Element.Text("**(font)育碧标识符(font)[warning]**", type=Types.Text.KMD), ),
                        Module.Section(f"(font){uuid}(font)[success]"),
                        Module.Section(Element.Text("**(font)作案类型(font)[warning]**", type=Types.Text.KMD), ),
                        Module.Section(f"(font){type}(font)[success]"),
                        Module.Section(Element.Text("**(font)登记日期(font)[warning]**", type=Types.Text.KMD), ),
                        Module.Section(f"(font){date}(font)[success]"),
                        Module.Section(Element.Text("**(font)备注(font)[warning]**", type=Types.Text.KMD), ),
                        Module.Section(f"(font){remark}(font)[success]"),
                        Module.Divider(),
                        Module.Context(
                            Element.Text(f"查询时间:{formatted_time} Search by Td2ban (QGE.)", type=Types.Text.KMD),
                            Element.Image(src=image_path),
                        ),
                        color='#B22222'
                    )
                    await msg.ctx.channel.send(CardMessage(searchBAN2), temp_target_id=msg.author.id)



@bot.command(name='登记', aliases=['登記'], case_sensitive=False)
async def dj(msg: Message, dj_type: str, *args):
    global temp_uuid_name, temp_uuid_uuid, temp_uuid_tf_tf, temp_uuid_tf, temp_uuid_profile_pic_url, temp_uuid_msg_id, temp_td2ban_msg_id
    if temp_uuid_tf_tf == 't':
        temp_uuid_tf_tf = 'f'
        name = temp_uuid_name
        uuid_str = temp_uuid_uuid
        type_value = dj_type
        date_str = date_only
        dj_remark =  "".join(args)
        if dj_remark == "":
            dj_remark=None

        try:
            with pymysql.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME) as db:
                with db.cursor() as cur:
                    cur.execute("INSERT INTO td2ban (Name, Uuid, Type, Remark, Date) VALUES (%s, %s, %s, %s, %s)",
                                (name, uuid_str, type_value, dj_remark, date_str))
                    db.commit()
            tdban02 = Card(
                Module.Header("查询结果如下"),
                Module.Section(
                    Element.Text(
                        f"**(font)游戏ID(font)[warning]**\n(font){temp_uuid_name}(font)[success]\n**(font)当前状态(font)[warning]**\n(font)已添加至黑名单(font)[purple]\n",
                        type=Types.Text.KMD),
                    Element.Image(src=temp_uuid_profile_pic_url, size=Types.Size.SM, circle=True),
                    mode=Types.SectionMode.RIGHT),
                Module.Section(
                    Element.Text(f"**(font)UUID(font)[warning]**\n(font){temp_uuid_uuid}(font)[success]",
                                 type=Types.Text.KMD),
                    Element.Button("登记成功", value="登记成功", theme=Types.Theme.SUCCESS),
                ),
                Module.Divider(),
                Module.Context(
                    Element.Text(f"查询时间:{formatted_time}", type=Types.Text.KMD),
                    Element.Image(src=image_path),
                ),
                color='#B22222'
            )
            await upd_msg(temp_uuid_msg_id, CardMessage(tdban02), channel_type=ChannelPrivacyTypes.GROUP, bot=bot)
            await del_msg(temp_td2ban_msg_id['msg_id'])
            temp_td2ban_msg_id = ''
            await msg.add_reaction('✅')

            current_time = datetime.now().strftime('%Y%m%d%H%M%S')
            log_filename = f'.\\logs\\{msg.author.nickname}_{temp_uuid_uuid}_{current_time}.log'

            # 设置日志记录器
            logger = logging.getLogger()
            file_handler = logging.FileHandler(log_filename)
            formatter = logging.Formatter(f'{formatted_time} - %(message)s')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.setLevel(logging.INFO)

            # 记录信息到日志文件
            logger.info(f'KOOK用户 ID：{msg.author.id}，KOOK用户名：{msg.author.username}')
            logger.info(f'KOOK服务器内昵称 ID：{msg.author.nickname}，举报游戏ID：{temp_uuid_name}')
            logger.info(f'举报UUID：{temp_uuid_uuid}')
            logger.info(f'作案类型：{type_value}，备注：{dj_remark}')

            # 移除日志处理器以结束日志记录
            logger.removeHandler(file_handler)

            await asyncio.sleep(30)
            await del_msg(msg.id)


        except pymysql.Error as e:
            tdban03 = Card(
                Module.Header("查询结果如下"),
                Module.Section(
                    Element.Text(
                        f"**(font)游戏ID(font)[warning]**\n(font){temp_uuid_name}(font)[success]\n**(font)当前状态(font)[warning]**\n(font){temp_uuid_tf}\n",
                        type=Types.Text.KMD),
                    Element.Image(src=temp_uuid_profile_pic_url, size=Types.Size.SM, circle=True),
                    mode=Types.SectionMode.RIGHT),
                Module.Section(
                    Element.Text(f"**(font)UUID(font)[warning]**\n(font){temp_uuid_uuid}(font)[success]",
                                 type=Types.Text.KMD),
                    Element.Button("登记失败", value="登记失败", theme=Types.Theme.DANGER),
                ),
                Module.Divider(),
                Module.Context(
                    Element.Text(f"查询时间:{formatted_time}", type=Types.Text.KMD),
                    Element.Image(src=image_path),
                ),
                color='#98FB98'
            )
            await msg.add_reaction('❌')
            await upd_msg(temp_uuid_msg_id, CardMessage(tdban03), channel_type=ChannelPrivacyTypes.GROUP, bot=bot)
            # 处理数据库连接或插入数据时的错误
            print(f"数据库错误：{str(e)}")

        finally:
            # 无论是否发生错误，都可以在这里进行一些清理操作，比如关闭游标（如果需要的话）
            cur.close()


    else:
        await msg.add_reaction('❌')
        await msg.ctx.channel.send('非法操作', temp_target_id=msg.author.id)
        temp_uuid_tf_tf = 'f'




async def upd_msg(msg_id: str, content: Union[CardMessage, str], target_id=None,
channel_type: Union[ChannelPrivacyTypes, str] = 'public', bot=bot):
    """
    异步函数，用于更新消息内容。

    参数：
    - msg_id (str)：要更新的消息的 ID。
    - content (Union[CardMessage, str])：更新的内容，可以是卡片消息对象或字符串。
    - target_id：目标 ID，可选参数，具体用途可能根据上下文确定。
    - channel_type (Union[ChannelPrivacyTypes, str])：频道类型，可以是字符串表示的公共频道（'public'）或群组类型，也可以是特定的枚举类型。默认是'public'。
    - bot：具体的 bot 对象，可能用于执行请求操作。

    返回值：
    - 返回更新消息操作的结果。
    """
    # 如果内容是卡片消息对象，将其转换为 JSON 字符串
    if isinstance(content, CardMessage):
        content = json.dumps(content)
    data = {'msg_id': msg_id, 'content': content}
    # 如果目标 ID 不为 None，则添加到数据字典中
    if target_id is not None:
        data['temp_target_id'] = target_id
    # 根据频道类型执行不同的请求
    if channel_type == 'public' or channel_type == ChannelPrivacyTypes.GROUP:
        result = await bot.client.gate.request('POST', 'message/update', data=data)
    else:
        result = await bot.client.gate.request('POST', 'direct-message/update', data=data)
    return result


async def del_msg(msg_id: str, bot=bot):
    """
    异步函数，用于删除指定消息 ID 的频道聊天消息。

    参数：
    - msg_id (str)：要删除的消息的 ID。
    - bot：具体的 bot 对象，可能用于执行请求操作。

    返回值：
    - 无返回参数，但执行成功后会删除指定消息。
    """
    data = {'msg_id': msg_id}
    await bot.client.gate.request('POST', 'message/delete', data=data)


@bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
async def btn_click_event(b: Bot, e: Event):
    global temp_uuid_tf, temp_uuid_profile_pic_url, temp_uuid_name, temp_uuid_uuid, temp_uuid_msg_id, temp_uuid_msg_author_id, temp_td2ban_msg_id

    """按钮点击事件"""
    buttondata = e.body

    value = buttondata['value']
    msg_id = buttondata['msg_id']
    user_id = buttondata['user_id']
    target_id = buttondata['target_id']
    user_info_id = buttondata['user_info']['id']
    joined_at = buttondata['user_info']['joined_at']
    active_time = buttondata['user_info']['active_time']
    guild_id = buttondata['guild_id']
    temp_uuid_msg_id = msg_id
    zwqx = '暂无权限'
    djcg = '登记成功'
    ysx = '已失效'


    if user_id == temp_uuid_msg_author_id:
        if value == zwqx:
            ch = await bot.client.fetch_public_channel(target_id)
            qxbz001 = Card(
                Module.Header("查询结果如下"),
                Module.Section(
                    Element.Text(f"**(font)游戏ID(font)[warning]**\n(font){temp_uuid_name}(font)[success]\n**(font)当前状态(font)[warning]**\n(font){temp_uuid_tf}\n", type=Types.Text.KMD),
                    Element.Image(src=temp_uuid_profile_pic_url, size=Types.Size.SM, circle=True), mode=Types.SectionMode.RIGHT),
                Module.Section(
                    Element.Text(f"**(font)UUID(font)[warning]**\n(font){temp_uuid_uuid}(font)[success]", type=Types.Text.KMD),
                    Element.Button("权限不足", value='权限不足', theme=Types.Theme.SECONDARY),
                ),
                Module.Divider(),
                Module.Context(
                    Element.Text(f"查询时间:{formatted_time}", type=Types.Text.KMD),
                    Element.Image(src=image_path),
                ),
                color='#98FB98'
            )
            await bot.client.send(ch, '权限不足，请联系管理员 QGE.', temp_target_id=user_id)
            await upd_msg(temp_uuid_msg_id, CardMessage(qxbz001), channel_type=ChannelPrivacyTypes.GROUP, bot=bot)

        if value == djcg:
            ch = await bot.client.fetch_public_channel(target_id)
            results = query_data_from_td2ban(temp_uuid_uuid)
            latest_name = await sample_uid(temp_uuid_uuid)
            if results:
                for row in results:
                    name = row[0]
                    uuid = row[1]
                    type = row[2]
                    date = row[3]
                    remark = row[4]
                    img_ban = f'https://ubisoft-avatars.akamaized.net/{uuid}/default_256_256.png'
                    if type == '个人':
                        if root_id == user_id:
                            searchBAN04 = Card(
                                Module.Header("查询内容如下"),
                                Module.Section(
                                    Element.Text(
                                        f"**(font)登记ID(font)[warning]**\n(font){name}(font)[success]\n**(font)最新ID(font)[warning]**\n(font){latest_name}(font)[success]",
                                        type=Types.Text.KMD),
                                    Element.Image(src=img_ban, size=Types.Size.SM, circle=True),
                                    mode=Types.SectionMode.RIGHT
                                ),
                                Module.Section(
                                    Element.Text("**(font)育碧标识符(font)[warning]**", type=Types.Text.KMD), ),
                                Module.Section(f"(font){uuid}(font)[success]"),
                                Module.Section(
                                    Element.Text("**(font)作案类型(font)[warning]**", type=Types.Text.KMD), ),
                                Module.Section(f"(font){type}(font)[success]"),
                                Module.Section(
                                    Element.Text("**(font)登记日期(font)[warning]**", type=Types.Text.KMD), ),
                                Module.Section(f"(font){date}(font)[success]"),
                                Module.Section(Element.Text("**(font)备注(font)[warning]**", type=Types.Text.KMD), ),
                                Module.Section(f"(font){remark}(font)[success]"),
                                Module.Divider(),
                                Module.Context(
                                    Element.Text(f"查询时间:{formatted_time} Search by Td2ban (QGE.)",
                                                 type=Types.Text.KMD),
                                    Element.Image(src=image_path),
                                ),
                                color='#B22222'
                            )
                            await bot.client.send(ch, CardMessage(searchBAN04), temp_target_id=temp_uuid_msg_author_id)
                    else:
                        searchBAN03 = Card(
                            Module.Header("查询内容如下"),
                            Module.Section(
                                Element.Text(
                                    f"**(font)登记ID(font)[warning]**\n(font){name}(font)[success]\n**(font)最新ID(font)[warning]**\n(font){latest_name}(font)[success]",
                                    type=Types.Text.KMD),
                                Element.Image(src=img_ban, size=Types.Size.SM, circle=True),
                                mode=Types.SectionMode.RIGHT
                            ),
                            Module.Section(Element.Text("**(font)育碧标识符(font)[warning]**", type=Types.Text.KMD), ),
                            Module.Section(f"(font){uuid}(font)[success]"),
                            Module.Section(Element.Text("**(font)作案类型(font)[warning]**", type=Types.Text.KMD), ),
                            Module.Section(f"(font){type}(font)[success]"),
                            Module.Section(Element.Text("**(font)登记日期(font)[warning]**", type=Types.Text.KMD), ),
                            Module.Section(f"(font){date}(font)[success]"),
                            Module.Section(Element.Text("**(font)备注(font)[warning]**", type=Types.Text.KMD), ),
                            Module.Section(f"(font){remark}(font)[success]"),
                            Module.Divider(),
                            Module.Context(
                                Element.Text(f"查询时间:{formatted_time} Search by Td2ban (QGE.)", type=Types.Text.KMD),
                                Element.Image(src=image_path),
                            ),
                            color='#B22222'
                        )
                        await bot.client.send(ch, CardMessage(searchBAN03), temp_target_id=temp_uuid_msg_author_id)

            tdban02 = Card(
                Module.Header("查询结果如下"),
                Module.Section(
                    Element.Text(
                        f"**(font)游戏ID(font)[warning]**\n(font){temp_uuid_name}(font)[success]\n**(font)当前状态(font)[warning]**\n(font){temp_uuid_tf}\n",
                        type=Types.Text.KMD),
                    Element.Image(src=temp_uuid_profile_pic_url, size=Types.Size.SM, circle=True),
                    mode=Types.SectionMode.RIGHT),
                Module.Section(
                    Element.Text(f"**(font)UUID(font)[warning]**\n(font){temp_uuid_uuid}(font)[success]",
                                 type=Types.Text.KMD),
                    Element.Button("登记成功", value="已点击", theme=Types.Theme.SECONDARY),
                ),
                Module.Divider(),
                Module.Context(
                    Element.Text(f"查询时间:{formatted_time}", type=Types.Text.KMD),
                    Element.Image(src=image_path),
                ),
                color='#98FB98'
            )
            await upd_msg(msg_id, CardMessage(tdban02), channel_type=ChannelPrivacyTypes.GROUP, bot=bot)

        if user_id in rootid and value == '黑名单登记':
            ch = await bot.client.fetch_public_channel(target_id)

            tdban = Card(
                Module.Section(Element.Text("**(font)请输入按照要求填写信息(备注可以为空)(font)[warning]**",
                                            type=Types.Text.KMD), ),
                Module.Section("`/登记 {作案类型} {备注}`"),
            )
            temp_td2ban_msg_id = await bot.client.send(ch, CardMessage(tdban))

            tdban01 = Card(
                Module.Header("查询结果如下"),
                Module.Section(
                    Element.Text(
                        f"**(font)游戏ID(font)[warning]**\n(font){temp_uuid_name}(font)[success]\n**(font)当前状态(font)[warning]**\n(font){temp_uuid_tf}\n",
                        type=Types.Text.KMD),
                    Element.Image(src=temp_uuid_profile_pic_url, size=Types.Size.SM, circle=True),
                    mode=Types.SectionMode.RIGHT),
                Module.Section(
                    Element.Text(f"**(font)UUID(font)[warning]**\n(font){temp_uuid_uuid}(font)[success]",
                                 type=Types.Text.KMD),
                    Element.Button("正在登记中", value="正在登记中", theme=Types.Theme.SECONDARY),
                ),
                Module.Divider(),
                Module.Context(
                    Element.Text(f"查询时间:{formatted_time}", type=Types.Text.KMD),
                    Element.Image(src=image_path),
                ),
                color='#98FB98'
            )
            await upd_msg(msg_id, CardMessage(tdban01), channel_type=ChannelPrivacyTypes.GROUP, bot=bot)
            global temp_uuid_tf_tf
            temp_uuid_tf_tf = 't'
    else:
        if value !='已失效':
            ch = await bot.client.fetch_public_channel(target_id)
            await bot.client.send(ch, '请勿使用他人查询卡片登记', temp_target_id=user_id)
            trkp = Card(
                Module.Header("查询结果如下"),
                Module.Section(
                    Element.Text(f"**(font)游戏ID(font)[warning]**\n(font){temp_uuid_name}(font)[success]\n**(font)当前状态(font)[warning]**\n(font){temp_uuid_tf}\n", type=Types.Text.KMD),
                    Element.Image(src=temp_uuid_profile_pic_url, size=Types.Size.SM, circle=True), mode=Types.SectionMode.RIGHT),
                Module.Section(
                    Element.Text(f"**(font)UUID(font)[warning]**\n(font){temp_uuid_uuid}(font)[success]", type=Types.Text.KMD),
                    Element.Button("黑名单登记", value='已失效', click=Types.Click.RETURN_VAL, theme=Types.Theme.SECONDARY),
                ),
                Module.Divider(),
                Module.Context(
                    Element.Text(f"查询时间:{formatted_time}", type=Types.Text.KMD),
                    Element.Image(src=image_path),
                ),
                color='#98FB98'
            )
            await upd_msg(msg_id, CardMessage(trkp), channel_type=ChannelPrivacyTypes.GROUP, bot=bot)



async def main():
    asyncio.create_task(check_for_new_data())
    platfrom = SoftwareTypes.QQ_MUSIC
    await bot.client.update_listening_music("友谊之光", "Maria", platfrom)
    await bot.start()


loop.run_until_complete(main())

#2024年9月27日09:01:49


