import re
import pymysql
import asyncio
import logging
import requests
import json
from typing import Union
from datetime import datetime, timedelta
from khl import *
from khl import Bot, Message, Event, ChannelPrivacyTypes
from khl.card import Card, CardMessage, Module, Types, Element
from khl import PublicMessage, PrivateMessage
from siegeapi import Auth, InvalidRequest

# ---------读取config文件-----------
with open('.\\config\\config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)


# ---------创建新的事件循环---------
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


# ---------全局变量-----------
# -全境封锁2-图标
td2_image_path = 'https://img.kookapp.cn/assets/2024-09/22/sEDwT4c2lU01c01c.png'

# -bot注册
bot = Bot(token=config['token'])

# -拥有者ID，管理员ID注册
root = config['root']       # --管理员权限账户
root_id = config['root_id']     # --机器人拥有者

# -判断
tt = '已添加至黑名单(font)[purple]'
yn = '正在登记中(font)[secondary]'
ty = '黑名单里有此玩家(font)[danger]'
tn = '此玩家不在黑名单内(font)[primary]'

# -育碧账户
UBISOFT_EMAIL = config['UBISOFT_EMAIL']
UBISOFT_PASSW = config['UBISOFT_PASSW']

# -数据库相关
DB_HOST = config['db_host']     # --数据库地址
DB_USER = config['db_user']     # --数据库用户名
DB_PASS = config['db_pass']     # --数据库密码
DB_NAME = config['db_name']     # --数据库名称Z
DB_PORT = config['db_port']     # --数据库端口
last_checked_data = None        # --上一次检查数据库时的数据状态

# -其他变量
xb_kg = '新八开挂'
lb_kg = '老八开挂'
yx = '爷新'
yy = '演员'
gr = '个人'
ts = '特殊'
temp_account_img = 'https://img.kookapp.cn/attachments/2024-10/10/zactjBoA44074074.png'
temp_uuid_msg_id = ''
temp_uuid_name = ''
temp_uuid_msg_author_id = ''
temp_uuid_uuid = ''
temp_uuid_tf_tf = 'f'
temp_td2ban_msg_id = ''


# ---------获取最新日期-----------
def get_current_time():
    now = datetime.now()
    date_only = now.date()
    formatted_time = now.strftime('%Y-%m-%d %H:%M')
    return date_only, formatted_time


# ---------卡片消息-----------
async def card_message(name=None, type=None, uuid=None, date=None, remark=None, card_status=None, latest_name=None, message_status=None, tf=None, uuid_status=None, ph_tf=None):
    date_only, formatted_time = get_current_time()
    global temp_account_img

    account_img = temp_account_img

    if uuid_status == 'Y' and (ph_tf != 'n' or ph_tf is None):
        save_path = await download_image(uuid, name)
        account_img = await upload(save_path)
        temp_account_img = account_img
    elif uuid_status == 'C':
        account_img = 'https://img.kookapp.cn/attachments/2024-10/10/zactjBoA44074074.png'
    elif uuid_status == 'D':
        account_img = f'https://ubisoft-avatars.akamaized.net/{uuid}/default_146_146.png'

    if card_status == '更新':
        if type == yx:
            type_status = f"**(font)游戏ID(font)[warning]**\n(font){name}(font)[success]\n**(font)作案类型(font)[warning]**\n(font){type}(font)[purple]"
        elif type == xb_kg or type == lb_kg:
            type_status = f"**(font)游戏ID(font)[warning]**\n(font){name}(font)[success]\n**(font)作案类型(font)[warning]**\n(font){type}(font)[danger]"
        elif type == yy:
            type_status = f"**(font)游戏ID(font)[warning]**\n(font){name}(font)[success]\n**(font)作案类型(font)[warning]**\n(font){type}(font)[pink]"
        elif type == gr:
            type_status = f"**(font)游戏ID(font)[warning]**\n(font){name}(font)[success]\n**(font)作案类型(font)[warning]**\n(font){type}(font)[secondary]"
        else:
            type_status = f"**(font)游戏ID(font)[warning]**\n(font){name}(font)[success]\n**(font)作案类型(font)[warning]**\n(font){type}(font)[info]"


        new_ban_card = Card(
            Module.Header("欢迎新成员加入黑名单"),
            Module.Section(
                Element.Text(type_status, type=Types.Text.KMD),
                Element.Image(src=account_img, size=Types.Size.SM, circle=True),
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
                Element.Text(f"打印时间:{date_only} By Td2ban (QGE.)", type=Types.Text.KMD),
                Element.Image(src=td2_image_path),
            ),
            color='#B22222' if type == xb_kg or type == lb_kg else '#F9C6CF' if type == yy else '#FFFFFF' if type == ts else '#9370DB' if type == yx else '#828282' if type == gr else None
        )
        return new_ban_card

    if card_status == '查询':
        if type == yx:
            type_status1 = f"(font){type}(font)[purple]"
        elif type == xb_kg or type == lb_kg:
            type_status1 = f"(font){type}(font)[danger]"
        elif type == yy:
            type_status1 = f"(font){type}(font)[pink]"
        elif type == gr:
            type_status1 = f"(font){type}(font)[secondary]"
        else:
            type_status1 = f"(font){type}(font)[info]"
        search_card = Card(
            Module.Header("查询内容如下"),
            Module.Section(
                Element.Text(
                    f"**(font)登记ID(font)[warning]**\n(font){name}(font)[success]\n**(font)最新ID(font)[warning]**\n(font){latest_name}(font)[purple]",
                    type=Types.Text.KMD),
                *([] if tf else [Element.Image(src=account_img, size=Types.Size.SM, circle=True)]),
                mode=Types.SectionMode.RIGHT
            ),
            Module.Section(Element.Text("**(font)育碧标识符(font)[warning]**", type=Types.Text.KMD), ),
            Module.Section(f"(font){uuid}(font)[success]"),
            Module.Section(Element.Text("**(font)作案类型(font)[warning]**", type=Types.Text.KMD), ),
            Module.Section(type_status1),
            Module.Section(Element.Text("**(font)登记日期(font)[warning]**", type=Types.Text.KMD), ),
            Module.Section(f"(font){date}(font)[success]"),
            Module.Section(Element.Text("**(font)备注(font)[warning]**", type=Types.Text.KMD), ),
            Module.Section(f"(font){remark}(font)[success]"),
            Module.Divider(),
            Module.Context(
                Element.Text(f"查询时间:{formatted_time} Search by Td2ban (QGE.)", type=Types.Text.KMD),
                Element.Image(src=td2_image_path),
            ),
            color='#B22222' if type == xb_kg or type == lb_kg else '#F9C6CF' if type == yy else '#FFFFFF' if type == ts else '#9370DB' if type == yx else '#828282' if type == gr else None
        )
        return search_card

    if card_status == 'uuid':
        search_uuid = Card(
            Module.Header("查询结果如下"),
            Module.Section(
                Element.Text(f"**(font)游戏ID(font)[warning]**\n(font){name}(font)[success]\n**(font)当前状态(font)[warning]**\n(font){tf}\n", type=Types.Text.KMD),
                *([Element.Image(src='https://img.kookapp.cn/attachments/2024-10/10/zactjBoA44074074.png', size=Types.Size.SM, circle=True)] if ph_tf == "n" else [Element.Image(src=account_img, size=Types.Size.SM, circle=True)]), mode=Types.SectionMode.RIGHT),
            Module.Section(
                Element.Text(f"**(font)UUID(font)[warning]**\n(font){uuid}(font)[success]",
                             type=Types.Text.KMD),
                *([Element.Button("黑名单登记", value='黑名单登记', click=Types.Click.RETURN_VAL,
                                  theme=Types.Theme.INFO), ] if message_status == "t" else []),
                *([Element.Button("请重新获取", value='已失效', click=Types.Click.RETURN_VAL,
                                  theme=Types.Theme.SECONDARY), ] if message_status == "f" else []),
                *([Element.Button("黑名单登记", value='暂无权限', click=Types.Click.RETURN_VAL,
                                  theme=Types.Theme.SECONDARY), ] if message_status == "tf" else []),
                *([Element.Button("登记成功", value='登记成功', click=Types.Click.RETURN_VAL,
                                  theme=Types.Theme.SUCCESS), ] if message_status == "cg" else []),
                *([Element.Button("权限不足", value='权限不足',
                                  theme=Types.Theme.SECONDARY), ] if message_status == "mqx" else []),
                *([Element.Button("登记成功", value='已点击',
                                  theme=Types.Theme.SECONDARY)] if message_status == "ydj" else []),
                *([Element.Button("正在登记中", value='正在登记中',
                                  theme=Types.Theme.SECONDARY)] if message_status == "zdj" else []),
                *([Element.Button("黑名单登记", value='已失效',
                                  theme=Types.Theme.SECONDARY)] if message_status == "ysx" else []),
                *([Element.Button("登记失败", value='登记失败',
                                  theme=Types.Theme.SECONDARY)] if message_status == "sb" else []),
            ),
            Module.Divider(),
            Module.Context(
                Element.Text(f"查询时间:{formatted_time}", type=Types.Text.KMD),
                Element.Image(src=td2_image_path),
            ),
            color='#B22222' if tf == ty else '#8A2BE2' if tf == tt else '#98FB98' if tf == tn else '#FFA500' if tf == yn else None
        )
        return search_uuid

    if card_status == '登记':
        dj_card = Card(
            Module.Section(Element.Text("**(font)请输入按照要求填写信息(备注可以为空)(font)[warning]**", type=Types.Text.KMD), ),
            Module.Section("`/登记 {作案类型} {备注}`"),
        )
        return dj_card

    if card_status == '倒计时':
        djs_card = Card(
            Module.Section("(font)请稍后。。。 。。。 。。 。(font)[success]"),
            Module.Countdown(datetime.now() + timedelta(seconds=60), mode=Types.CountdownMode.SECOND),
        )
        return djs_card


# ------黑名单公示更新--------
async def check_for_new_data():
    global last_checked_data
    while True:
        try:
            with pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME, port=int(DB_PORT)) as db:
                with db.cursor() as cur:
                    cur.execute("use td2ban")
                    cur.execute("SELECT * FROM td2ban")
                    current_data = cur.fetchall()
                    if last_checked_data is None:
                        last_checked_data = current_data
                    else:
                        new_data = [row for row in current_data if row not in last_checked_data]
                        if new_data:
                            card_status = '更新'
                            for row in new_data:
                                name = row[0]
                                uuid = row[1]
                                type = row[2]
                                date = row[3]
                                remark = row[4]
                                new_ban_card = await card_message(name=name, type=type, uuid=uuid, date=date, remark=remark, card_status=card_status, uuid_status = 'D')
                                if type == '个人':
                                    try:
                                        channel_id = config['channel_id_private']
                                        private_channel = await bot.client.fetch_public_channel(channel_id)
                                        await bot.client.send(private_channel, CardMessage(new_ban_card))
                                        status = 'ture'
                                    except Exception as e:
                                        new_ban_card_r = await card_message(name=name, type=type, uuid=uuid, date=date, remark=remark, card_status=card_status, uuid_status='Y')
                                        channel_id = config['channel_id_private']
                                        private_channel = await bot.client.fetch_public_channel(channel_id)
                                        await bot.client.send(private_channel, CardMessage(new_ban_card_r))
                                        status = 'false'
                                else:
                                    try:
                                        for channel_id in config['channel_id_public']:
                                            public_channel = await bot.client.fetch_public_channel(channel_id)
                                            await bot.client.send(public_channel, CardMessage(new_ban_card))
                                            status = 'ture'
                                    except Exception as e:
                                        for channel_id in config['channel_id_public']:
                                            new_ban_card_r = await card_message(name=name, type=type, uuid=uuid, date=date, remark=remark, card_status=card_status, uuid_status='Y')
                                            private_channel = await bot.client.fetch_public_channel(channel_id)
                                            await bot.client.send(private_channel, CardMessage(new_ban_card_r))
                                            status = 'false'
                                date_only, formatted_time = get_current_time()
                                print(f"有新成员加入，卡片打印状态{status}，时间：{formatted_time}")
                            last_checked_data = current_data
        except pymysql.Error as e:
            print(f"数据库查询错误：{str(e)}，时间：{formatted_time}")
        finally:
            # 确保数据库连接和游标被正确关闭
            cur.close()
        await asyncio.sleep(10)  # 每隔 10 秒检查一次，可以根据实际情况调整时间间隔


# ---------数据库查询-----------
def query_data_from_td2ban(guid):
    try:
        with pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME, port=int(DB_PORT)) as db:
            with db.cursor() as cur:
                cur.execute("use td2ban")
                sqlquery = "SELECT * FROM td2ban WHERE uuid = %s"
                cur.execute(sqlquery, (guid,))
                results = cur.fetchall()
                return results
    except pymysql.Error as e:
        print("数据库连接失败: " + str(e))
        return None


# ---------更新消息-----------
async def upd_msg(msg_id: str, content: Union[CardMessage, str], target_id=None, channel_type: Union[ChannelPrivacyTypes, str] = 'public', my_bot: Bot = bot):
    """
    异步函数，用于更新消息内容。

    参数：
    - msg_id (str)：要更新的消息的 ID。
    - content (Union[CardMessage, str])：更新的内容，可以是卡片消息对象或字符串。
    - target_id：目标 ID，可选参数，具体用途可能根据上下文确定。
    - channel_type (Union[ChannelPrivacyTypes, str])：频道类型，可以是字符串表示的公共频道（'public'）或群组类型，也可以是特定的枚举类型。默认是'public'。
    - my_bot (Bot)：具体的 bot 对象，可能用于执行请求操作。

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
        result = await my_bot.client.gate.request('POST', 'message/update', data=data)
    else:
        result = await my_bot.client.gate.request('POST', 'direct-message/update', data=data)
    return result


# ---------刪除消息-----------
async def del_msg(msg_id: str, my_bot: Bot = bot):
    """
    异步函数，用于删除指定消息 ID 的频道聊天消息。

    参数：
    - msg_id (str)：要删除的消息的 ID。
    - bot：具体的 bot 对象，可能用于执行请求操作。

    返回值：
    - 无返回参数，但执行成功后会删除指定消息。
    """
    data = {'msg_id': msg_id}
    await my_bot.client.gate.request('POST', 'message/delete', data=data)


# ---------通过用户最新ID查询用户头像，uuid-----------
async def sample(game_id):
    auth = Auth(UBISOFT_EMAIL, UBISOFT_PASSW)
    try:
        player_status = await auth.get_player(name=game_id)
        return player_status.id, player_status.name
    except (InvalidRequest, ValueError) as e:
        search_error = "ERROR"
        return search_error, e
    finally:
        await auth.close()



# ---------通过用户uuid查询用户最新ID-----------
async def sample_uid(profile_id):
    auth = Auth(UBISOFT_EMAIL, UBISOFT_PASSW)
    player_status = await auth.get_player(uid=profile_id)
    await auth.close()
    return player_status.name


# ---------从配置文件中读取openId-----------
def get_openid_from_config():
    with open('.\\config\\config.json', 'r', encoding='utf-8') as fi:
        id_config = json.load(fi)
        open_ids = id_config.get('openId')
        if isinstance(open_ids, str):
            return [open_ids]
        return open_ids


# ---------从配置文件中读取template_id-----------
def get_timetable_template_id_from_config():
    with open('.\\config\\config.json', 'r', encoding='utf-8') as ft:
        template = json.load(ft)
        return template.get('timetable_template_id')


# ---------微信推送函数中遍历openId列表进行发送-----------
def send_blacklist_notification(access_token, name, uuid, type_value, open_ids, author_id, author_username, author_identify_num):
    template_id = get_timetable_template_id_from_config()
    for openId in open_ids:
        body = {
            "touser": openId,
            "template_id": template_id.strip(),
            "url": "https://weixin.qq.com",
            "data": {
                "name": {
                    "value": name
                },
                "uuid": {
                    "value": uuid
                },
                "type": {
                    "value": type_value
                },
                "date": {
                    "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                "author_id": {
                    "value": author_id
                },
                "author_username": {
                    "value": author_username
                },
                "author_identify_num": {
                    "value": author_identify_num
                }
            }
        }
        url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(access_token)
        print(requests.post(url, json.dumps(body)).text)


# ---------获取access_token-----------
def get_access_token():
    # 从配置文件中读取 appID 和 appSecret
    with open('.\\config\\config.json', 'r', encoding='utf-8') as fa:
        access = json.load(fa)
        app_id = access.get('appID')
        app_secret = access.get('appSecret')
    # 检查是否成功读取到了 appID 和 appSecret
    if app_id is None or app_secret is None:
        raise ValueError("无法从配置文件中正确读取 appID 或 appSecret。")
    # 获取access token的url
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id.strip()}&secret={app_secret.strip()}'
    response = requests.get(url).json()
    print(response)
    access_token = response.get('access_token')
    return access_token


# ---------下载头像-----------
async def download_image(uuid, name):
    print(f'正在尝试下载,{name}的头像')
    image_url = f'https://ubisoft-avatars.akamaized.net/{uuid}/default_146_146.png'
    save_path = './image/account_image.png'
    bad_path = './image/bad_image.png'
    retries = 7  # 设置重试次数
    for attempt in range(retries):
        try:
            response = requests.get(image_url, timeout=5)  # 设置超时时间为 5 秒
            if response.status_code == 200:
                with open(save_path, 'wb') as fm:
                    fm.write(response.content)
                print(f"{name}的用户头像已保存至： {save_path}")
                return save_path
            else:
                print(f"{name}的用户头像下载失败， 错误代码: {response.status_code}。正在进行第 {attempt + 1} 次重试。")
        except requests.exceptions.Timeout:
            print(f"下载超时。正在进行第 {attempt + 1} 次重试。")
        except Exception as e:
            print(f"发生未知错误：{e}。正在进行第 {attempt + 1} 次重试。")
        await asyncio.sleep(2)  # 每次重试前等待 2 秒
    print("多次尝试下载失败，放弃下载。")
    return bad_path


# ---------上传头像-----------
async def upload(save_path):
    img_url = await bot.client.create_asset(save_path)
    print("头像已上传：",img_url)
    return img_url


# ---------监听按钮事件-----------
@bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
async def btn_click_event(b: Bot, e: Event):
    global temp_td2ban_msg_id, temp_uuid_msg_id
    card_status = 'uuid'
    uuid_status = 'D'
    button_data = e.body

    value = button_data['value']
    msg_id = button_data['msg_id']
    user_id = button_data['user_id']
    target_id = button_data['target_id']
#    user_info_id = button_data['user_info']['id']
#    joined_at = button_data['user_info']['joined_at']
#    active_time = button_data['user_info']['active_time']
#    guild_id = button_data['guild_id']
    temp_uuid_msg_id = msg_id
    zw_qx = '暂无权限'
    dj_cg = '登记成功'
    ch = await bot.client.fetch_public_channel(target_id)

    if value == zw_qx:
        message_status = 'mqx'
        await bot.client.send(ch, '权限不足，请联系管理员 QGE.', temp_target_id=user_id)
        try:
            search_uuid = await card_message(name=temp_uuid_name, uuid=temp_uuid_uuid, card_status=card_status, message_status=message_status, tf=tn, uuid_status=uuid_status)
            await upd_msg(msg_id, CardMessage(search_uuid), channel_type=ChannelPrivacyTypes.GROUP, my_bot=bot)
        except Exception as e:
            search_uuid = await card_message(name=temp_uuid_name, uuid=temp_uuid_uuid, card_status=card_status, message_status=message_status, tf=tn, uuid_status='Y')
            await upd_msg(msg_id, CardMessage(search_uuid), channel_type=ChannelPrivacyTypes.GROUP, my_bot=bot)

    if value == dj_cg:
        results = query_data_from_td2ban(temp_uuid_uuid)
        latest_name = await sample_uid(temp_uuid_uuid)
        if results:
            for row in results:
                name = row[0]
                uuid = row[1]
                type = row[2]
                date = row[3]
                remark = row[4]
                search_card = await card_message(name=name, type=type, uuid=uuid, date=date, remark=remark, card_status='查询', latest_name=latest_name, uuid_status=uuid_status)
                if type == '个人':
                    if root_id == user_id:
                        await bot.client.send(ch, CardMessage(search_card), temp_target_id=user_id)
                else:
                    await bot.client.send(ch, CardMessage(search_card), temp_target_id=user_id)
        message_status = 'ydj'
        try:
            search_uuid = await card_message(name=temp_uuid_name, uuid=temp_uuid_uuid, card_status=card_status, message_status=message_status, tf=tt, uuid_status=uuid_status)
            await upd_msg(msg_id, CardMessage(search_uuid), channel_type=ChannelPrivacyTypes.GROUP, my_bot=bot)
        except Exception as e:
            search_uuid = await card_message(name=temp_uuid_name, uuid=temp_uuid_uuid, card_status=card_status, message_status=message_status, tf=tt, uuid_status='Y')
            await upd_msg(msg_id, CardMessage(search_uuid), channel_type=ChannelPrivacyTypes.GROUP, my_bot=bot)


    if user_id in root and value == '黑名单登记':
        if user_id == temp_uuid_msg_author_id:
            dj_card = await card_message(card_status='登记')
            temp_td2ban_msg_id = await bot.client.send(ch, CardMessage(dj_card))
            message_status = 'zdj'
            try:
                search_uuid = await card_message(name=temp_uuid_name, uuid=temp_uuid_uuid, card_status=card_status, message_status=message_status, tf=yn, uuid_status=uuid_status)
                await upd_msg(msg_id, CardMessage(search_uuid), channel_type=ChannelPrivacyTypes.GROUP, my_bot=bot)
            except Exception as e:
                search_uuid = await card_message(name=temp_uuid_name, uuid=temp_uuid_uuid, card_status=card_status, message_status=message_status, tf=yn, uuid_status='Y')
                await upd_msg(msg_id, CardMessage(search_uuid), channel_type=ChannelPrivacyTypes.GROUP, my_bot=bot)
            global temp_uuid_tf_tf
            temp_uuid_tf_tf = 't'
        else:
            if value != '已失效':
                ch = await bot.client.fetch_public_channel(target_id)
                await bot.client.send(ch, '请勿使用他人查询卡片登记', temp_target_id=user_id)
                message_status = 'ysx'
                search_uuid = await card_message(name=temp_uuid_name, uuid=temp_uuid_uuid, card_status=card_status, message_status=message_status, tf=tn, uuid_status=uuid_status)
                await upd_msg(msg_id, CardMessage(search_uuid), channel_type=ChannelPrivacyTypes.GROUP, my_bot=bot)


# ---------查询是否被ban命令-----------
@bot.command(name='查询', aliases=['查詢'], case_sensitive=False)
async def search(msg: Message, guid: str):
    if isinstance(msg, PublicMessage):
        # 判断 guid 是否符合 GUID 标准
        if not re.match(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', guid):
            await msg.ctx.channel.send("输入的 UID 不符合标准格式\n请按照如下格式输入\n/查询 xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", temp_target_id=msg.author.id)
            return
        results = query_data_from_td2ban(guid)
        latest_name = await sample_uid(guid)
        if results:
            card_status = '查询'
            for row in results:
                name = row[0]
                uuid = row[1]
                type = row[2]
                date = row[3]
                remark = row[4]
                search_card = await card_message(name=name, type=type, uuid=uuid, date=date, remark=remark, card_status=card_status, latest_name=latest_name, uuid_status='D')
                if type == '个人':
                    if root_id == msg.author.id:
                        try:
                            await msg.ctx.channel.send(CardMessage(search_card), temp_target_id=msg.author.id)
                            await msg.add_reaction('✅')
                        except Exception as e:
                            search_card_r = await card_message(name=name, type=type, uuid=uuid, date=date, remark=remark, card_status=card_status, latest_name=latest_name, uuid_status='Y')
                            await msg.ctx.channel.send(CardMessage(search_card_r), temp_target_id=msg.author.id)
                            await msg.add_reaction('✅')


                    else:
                        await msg.add_reaction('❌')
                        await msg.ctx.channel.send("未找到对应数据-ERR-NO.2", temp_target_id=msg.author.id)
                else:
                    try:
                        await msg.ctx.channel.send(CardMessage(search_card), temp_target_id=msg.author.id)
                        await msg.add_reaction('✅')
                    except Exception as e:
                        search_card_r = await card_message(name=name, type=type, uuid=uuid, date=date, remark=remark, card_status=card_status, latest_name=latest_name, uuid_status='Y')
                        await msg.ctx.channel.send(CardMessage(search_card_r), temp_target_id=msg.author.id)
                        await msg.add_reaction('✅')
        else:
            await msg.add_reaction('❌')
            await msg.ctx.channel.send("未找到对应数据ERR-NO.1", temp_target_id=msg.author.id)


# ---------查询UUID命令-----------
@bot.command(name='uuid', aliases=['guid'], case_sensitive=False)
async def search_guid(msg: Message, game_id: str,  *args):
    global temp_uuid_name, temp_uuid_uuid, temp_uuid_msg_author_id
    tf = ''
    if isinstance(msg, PublicMessage):
        if "".join(args) == 'n':
            ph_tf = "".join(args)
        else:
            ph_tf = None
        uuid_status = 'Y'
        uuid, name = await sample(game_id)
        if uuid == 'ERROR':
            print(f"用戶{msg.author.username}#{msg.author.identify_num}输入了不存在的用户ID, 错误码:{name}")
            await msg.add_reaction('❌')
            await msg.ctx.channel.send("您所查找的用戶不存在。(ID并不区分大小写)\n请检查用户ID（注意辨别：o/0/i/L）", temp_target_id=msg.author.id)
            return
        latest_name = await sample_uid(uuid)
        results = query_data_from_td2ban(uuid)
        card_status = 'uuid'
        if results:
            for row in results:
                type = row[2]
                if type == '个人':
                    if root_id == msg.author.id:
                        tf = '黑名单里有此玩家(font)[danger]'
                    else:
                        tf = '此玩家不在黑名单内(font)[primary]'
                else:
                    tf = '黑名单里有此玩家(font)[danger]'
        else:
            tf = '此玩家不在黑名单内(font)[primary]'

        djs_card = await card_message(card_status='倒计时')
        djs = await msg.reply(CardMessage(djs_card))

        if tf == tn:
            if msg.author.id in root:
                message_status = 't'
                try:
                    search_uuid = await card_message(name=name, uuid=uuid, card_status=card_status, message_status=message_status, tf=tf, uuid_status='D')
                    await upd_msg(djs['msg_id'], CardMessage(search_uuid), channel_type=ChannelPrivacyTypes.GROUP, my_bot=bot)
                    await msg.add_reaction('✅')
                except Exception as e:
                    search_uuid = await card_message(name=name, uuid=uuid, card_status=card_status, message_status=message_status, tf=tf, uuid_status=uuid_status, ph_tf=ph_tf)
                    await upd_msg(djs['msg_id'], CardMessage(search_uuid), channel_type=ChannelPrivacyTypes.GROUP, my_bot=bot)
                    await msg.add_reaction('✅')
            else:
                message_status = 'tf'
                try:
                    search_uuid = await card_message(name=name, uuid=uuid, card_status=card_status, message_status=message_status, tf=tf, uuid_status='D')
                    await upd_msg(djs['msg_id'], CardMessage(search_uuid), channel_type=ChannelPrivacyTypes.GROUP, my_bot=bot)
                    await msg.add_reaction('✅')
                except Exception as e:
                    search_uuid = await card_message(name=name, uuid=uuid, card_status=card_status, message_status=message_status, tf=tf, uuid_status=uuid_status, ph_tf=ph_tf)
                    await upd_msg(djs['msg_id'], CardMessage(search_uuid), channel_type=ChannelPrivacyTypes.GROUP, my_bot=bot)
                    await msg.add_reaction('✅')
            temp_uuid_msg_author_id = msg.author.id
            temp_uuid_name = name
            temp_uuid_uuid = uuid
            add_root_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f'{msg.author.username}#{msg.author.identify_num}于{add_root_time}查询了一名玩家:{name}')
            await asyncio.sleep(600)
            message_status = 'f'
            search_uuid = await card_message(name=name, uuid=uuid, card_status=card_status, message_status=message_status, tf=tf, uuid_status='C', ph_tf=ph_tf)
            await upd_msg(djs['msg_id'], CardMessage(search_uuid), channel_type=ChannelPrivacyTypes.GROUP, my_bot=bot)

        if tf == ty:
            for row in results:
                name = row[0]
                uuid = row[1]
                type = row[2]
                date = row[3]
                remark = row[4]
                try:
                    search_uuid = await card_message(name=name, uuid=uuid, card_status=card_status, tf=tf, uuid_status='D')
                    await upd_msg(djs['msg_id'], CardMessage(search_uuid), channel_type=ChannelPrivacyTypes.GROUP, my_bot=bot)
                    await msg.add_reaction('✅')
                except Exception as e:
                    search_uuid = await card_message(name=name, uuid=uuid, card_status=card_status, tf=tf, uuid_status='Y')
                    await upd_msg(djs['msg_id'], CardMessage(search_uuid), channel_type=ChannelPrivacyTypes.GROUP, my_bot=bot)
                    await msg.add_reaction('✅')
                search_card = await card_message(name=name, type=type, uuid=uuid, date=date, remark=remark, card_status='查询', latest_name=latest_name, tf=tf)
                await msg.ctx.channel.send(CardMessage(search_card), temp_target_id=msg.author.id)
                add_root_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f'{msg.author.username}#{msg.author.identify_num}于{add_root_time}查询了一名黑名单内的玩家:{name}')


# ---------登记黑名单命令-----------
@bot.command(name='登记', aliases=['登記'], case_sensitive=False)
async def dj(msg: Message, dj_type: str, *args):
    global temp_uuid_name, temp_uuid_uuid, temp_uuid_tf_tf, temp_uuid_msg_id, temp_td2ban_msg_id
    if isinstance(msg, PublicMessage):
        card_status = 'uuid'
        date_only, formatted_time = get_current_time()
        if temp_uuid_tf_tf == 't':
            message_status = 'cg'
            temp_uuid_tf_tf = 'f'
            name = temp_uuid_name
            uuid_str = temp_uuid_uuid
            type_value = dj_type
            date_str = date_only
            dj_remark = "".join(args)
            if dj_remark == "":
                dj_remark = None

            try:
                with pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME) as db:
                    with db.cursor() as cur:
                        cur.execute("INSERT INTO td2ban (Name, Uuid, Type, Remark, Date) VALUES (%s, %s, %s, %s, %s)",
                                    (name, uuid_str, type_value, dj_remark, date_str))
                        db.commit()
                try:
                    search_uuid = await card_message(name=temp_uuid_name, uuid=temp_uuid_uuid, card_status=card_status, message_status=message_status, tf=tt, uuid_status='D')
                    await upd_msg(temp_uuid_msg_id, CardMessage(search_uuid), channel_type=ChannelPrivacyTypes.GROUP, my_bot=bot)
                except Exception as e:
                    search_uuid = await card_message(name=temp_uuid_name, uuid=temp_uuid_uuid, card_status=card_status, message_status=message_status, tf=tt, uuid_status='Y')
                    await upd_msg(temp_uuid_msg_id, CardMessage(search_uuid), channel_type=ChannelPrivacyTypes.GROUP, my_bot=bot)
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
                logger.info(f'KOOK用户 ID：{msg.author.id}，KOOK用户名：{msg.author.username}#{msg.author.identify_num}')
                logger.info(f'KOOK服务器内昵称 ID：{msg.author.nickname}，举报游戏ID：{temp_uuid_name}')
                logger.info(f'举报UUID：{temp_uuid_uuid}')
                logger.info(f'作案类型：{type_value}，备注：{dj_remark}')

                # 移除日志处理器以结束日志记录
                logger.removeHandler(file_handler)

                if config["wechat"] == "Y":
                    access_token = get_access_token()
                    open_ids = get_openid_from_config()
                    send_blacklist_notification(access_token, name, uuid_str, type_value, open_ids, msg.author.id, msg.author.username, msg.author.identify_num)
                else:
                    pass
                add_root_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f'{msg.author.username}#{msg.author.identify_num}于{add_root_time}登记了一名玩家:{name}')
                print('↓----------黑名单----------↓')
                print(f'玩家ID：{name}\t作案类型：{type_value}\nuuid：{uuid_str}\n备注：{dj_remark}')
                print('↑----------黑名单----------↑')
                await asyncio.sleep(30)
                await del_msg(msg.id)


            except pymysql.Error as e:
                message_status = 'sb'
                search_uuid = await card_message(name=temp_uuid_name, uuid=temp_uuid_uuid, card_status=card_status, message_status=message_status, tf=tn)
                await msg.add_reaction('❌')
                await upd_msg(temp_uuid_msg_id, CardMessage(search_uuid), channel_type=ChannelPrivacyTypes.GROUP, my_bot=bot)
                # 处理数据库连接或插入数据时的错误
                print(f"数据库错误：{str(e)}")

            finally:
                # 无论是否发生错误，都可以在这里进行一些清理操作，比如关闭游标（如果需要的话）
                cur.close()

        else:
            await msg.add_reaction('❌')
            await msg.ctx.channel.send('非法操作', temp_target_id=msg.author.id)
            temp_uuid_tf_tf = 'f'


# ---------打印整个列表-----------
@bot.command(name='打印列表', aliases=['打印'], case_sensitive=False)
async def dy(msg: Message):
    if isinstance(msg, PublicMessage):
        card_status = '更新'
        i=0
        try:
            # 连接数据库
            with pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME, port=int(DB_PORT)) as db:
                with db.cursor() as cur:
                    cur.execute("use td2ban")
                    cur.execute("SELECT * FROM td2ban")
                    results = cur.fetchall()

                    for row in results:
                        name = row[0]
                        uuid = row[1]
                        type = row[2]
                        date = row[3]
                        remark = row[4]
                        if type != '个人':
                            new_ban_card = await card_message(name=name, uuid=uuid, type=type, date=date, remark=remark, card_status=card_status, uuid_status = 'Y')
                            ch = await bot.client.fetch_public_channel(msg.target_id)
                            await bot.client.send(ch, CardMessage(new_ban_card))
                            i=i+1
                            await asyncio.sleep(2)

            print(f"打印完成，共打印：{int(i)}条数据")
        except pymysql.Error as e:
            print(f"数据库错误：{str(e)}")


# ---------添加管理员-----------
@bot.command(name='root', aliases=['添加管理员'], case_sensitive=False)
async def dy(msg: Message, roots: str):
    global root
    if isinstance(msg, PrivateMessage):
        if msg.author.id == root_id:
            with open('.\\config\\config.json', 'r', encoding='utf-8') as file:
                config_file = json.load(file)
                config_file['root'].append(roots)
            with open('.\\config\\config.json', 'w', encoding='utf-8') as file:
                json.dump(config_file, file, indent=4)
                await msg.add_reaction('✅')
                await msg.reply('成功添加')
                root = config_file['root']
            add_root_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f'{msg.author.username}#{msg.author.identify_num}于{add_root_time}添加了一名管理员-ID:{roots}')


# ---------添加公示频道-----------
@bot.command(name='public', aliases=['添加频道'], case_sensitive=False)
async def dy(msg: Message, public: str):
    global config
    if isinstance(msg, PrivateMessage):
        if msg.author.id in root:
            with open('.\\config\\config.json', 'r', encoding='utf-8') as file:
                config = json.load(file)
                config['channel_id_public'].append(public)
            with open('.\\config\\config.json', 'w', encoding='utf-8') as file:
                json.dump(config, file, indent=4)
                await msg.add_reaction('✅')
                await msg.reply('成功添加')
            add_public_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f'管理员{msg.author.username}#{msg.author.identify_num}于{add_public_time}添加了个黑名单公示频道-ID:{public}')


@bot.command(name='reload', case_sensitive=False)
async def reload(msg: Message):
    global config, bot, root,root_id, UBISOFT_EMAIL, UBISOFT_PASSW, DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME
    with open('.\\config\\config.json', 'r', encoding='utf-8') as fr:
        config = json.load(fr)
        bot = Bot(token=config['token'])
        root = config['root']  # --管理员权限账户
        root_id = config['root_id']
        UBISOFT_EMAIL = config['UBISOFT_EMAIL']
        UBISOFT_PASSW = config['UBISOFT_PASSW']
        DB_HOST = config['db_host']  # --数据库地址
        DB_USER = config['db_user']  # --数据库用户名
        DB_PASS = config['db_pass']  # --数据库密码
        DB_NAME = config['db_name']  # --数据库名称
        DB_PORT = config['db_port']  # --数据库端口
    await msg.reply("已重置配置文件")
    add_reload_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'管理员{msg.author.username}#{msg.author.identify_num}于{add_reload_time}重载了配置文件')

# ---------主函数-----------
async def main():
    asyncio.create_task(check_for_new_data())
    plat_from = SoftwareTypes.QQ_MUSIC
    await bot.client.update_listening_music("友谊之光", "Maria", plat_from)
    await bot.start()

loop.run_until_complete(main())


#2024年10月27日01:27:11
