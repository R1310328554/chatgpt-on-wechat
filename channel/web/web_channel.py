# encoding:utf-8

"""
web channel
"""

import io
import json
import os
import threading
import time

import requests

from plugins import *
from bridge.context import *
from bridge.reply import *
from channel.chat_channel import ChatChannel, check_prefix
from channel.web.web_message import *
from common.expired_dict import ExpiredDict
from common.log import logger
from common.singleton import singleton
from common.time_check import time_checker
from config import conf, get_appdata_dir

from common.dequeue import Dequeue
from common import memory

# @itchat.msg_register([TEXT, VOICE, PICTURE, NOTE, ATTACHMENT, SHARING])
def handler_single_msg(msg):
    try:
        cmsg = WebMessage(msg, False)
    except NotImplementedError as e:
        logger.debug("[WX]single message {} skipped: {}".format(msg["MsgId"], e))
        return None
    WebChannel().handle_single(cmsg)
    return None


# @itchat.msg_register([TEXT, VOICE, PICTURE, NOTE, ATTACHMENT, SHARING], isGroupChat=True)
def handler_group_msg(msg):
    try:
        cmsg = WebMessage(msg, True)
    except NotImplementedError as e:
        logger.debug("[WX]group message {} skipped: {}".format(msg["MsgId"], e))
        return None
    WebChannel().handle_group(cmsg)
    return None


def _check(func):
    def wrapper(self, cmsg: ChatMessage):
        msgId = cmsg.msg_id
        if msgId in self.receivedMsgs:
            logger.info("Web message {} already received, ignore".format(msgId))
            return
        self.receivedMsgs[msgId] = True
        create_time = cmsg.create_time  # 消息时间戳
        if conf().get("hot_reload") == True and int(create_time) < int(time.time()) - 60:  # 跳过1分钟前的历史消息
            logger.debug("[WX]history message {} skipped".format(msgId))
            return
        if cmsg.my_msg and not cmsg.is_group:
            logger.debug("[WX]my message {} skipped".format(msgId))
            return
        return func(self, cmsg)

    return wrapper


# 可用的二维码生成接口
# https://api.qrserver.com/v1/create-qr-code/?size=400×400&data=https://www.abc.com
# https://api.isoyu.com/qr/?m=1&e=L&p=20&url=https://www.abc.com
def qrCallback(uuid, status, qrcode):
    # logger.debug("qrCallback: {} {}".format(uuid,status))
    if status == "0":
        # print( 'qrcode', qrcode)
        # try:
        #     from PIL import Image

        #     img = Image.open(io.BytesIO(qrcode))
        #     _thread = threading.Thread(target=img.show, args=("QRCode",))
        #     _thread.setDaemon(True)
        #     _thread.start()
        # except Exception as e:
        #     pass

        url = f"https://login.weixin.qq.com/l/{uuid}"

        qr_api1 = "https://api.isoyu.com/qr/?m=1&e=L&p=20&url={}".format(url)
        qr_api2 = "https://api.qrserver.com/v1/create-qr-code/?size=400×400&data={}".format(url)
        qr_api3 = "https://api.pwmqr.com/qrcode/create/?url={}".format(url)
        qr_api4 = "https://my.tv.sohu.com/user/a/wvideo/getQRCode.do?text={}".format(url)
        print("You can also scan QRCode in any website below:")
        print(qr_api3)
        print(qr_api4) # url失效
        print(qr_api2) # url失效
        print(qr_api1)

        import qrcode
        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)


@singleton
class WebChannel(ChatChannel):
    NOT_SUPPORT_REPLYTYPE = []

    def __init__(self):
        super().__init__()
        self.receivedMsgs = ExpiredDict(60 * 60)
        self.nick_name_black_list = conf().get("nick_name_black_list", [])

    def startup(self, *args, **kwargs):
        logger.info("Web login success, user_id: {}, nickname: {}".format(self.user_id, self.name))
        

    # handle_* 系列函数处理收到的消息后构造Context，然后传入produce函数中处理Context和发送回复
    # Context包含了消息的所有信息，包括以下属性
    #   type 消息类型, 包括TEXT、VOICE、IMAGE_CREATE
    #   content 消息内容，如果是TEXT类型，content就是文本内容，如果是VOICE类型，content就是语音文件名，如果是IMAGE_CREATE类型，content就是图片生成命令
    #   kwargs 附加参数字典，包含以下的key：
    #        session_id: 会话id
    #        isgroup: 是否是群聊
    #        receiver: 需要回复的对象
    #        msg: ChatMessage消息对象
    #        origin_ctype: 原始消息类型，语音转文字后，私聊时如果匹配前缀失败，会根据初始消息是否是语音来放宽触发规则
    #        desire_rtype: 希望回复类型，默认是文本回复，设置为ReplyType.VOICE是语音回复

    # @time_checker # 不能加这个， 加上则返回的是None， 非常奇怪！
    # @_check
    def handle_single(self, cmsg: ChatMessage, tenantId, botId):
        # filter system message
        if cmsg.other_user_id in ["weixin"]: # ？？ 
            return None
        if cmsg.ctype == ContextType.VOICE:
            if conf().get("speech_recognition") != True:
                return None
            logger.debug("[WX]receive voice msg: {}".format(cmsg.content))
        elif cmsg.ctype == ContextType.IMAGE:
            logger.debug("[WX]receive image msg: {}".format(cmsg.content))
        elif cmsg.ctype == ContextType.PATPAT:
            logger.debug("[WX]receive patpat msg: {}".format(cmsg.content))
        elif cmsg.ctype == ContextType.TEXT:
            logger.debug("[WX]receive text msg: {}, cmsg={}".format(json.dumps(cmsg._rawmsg, ensure_ascii=False), cmsg))
        else:
            logger.debug("[WX]receive msg: {}, cmsg={}".format(cmsg.content, cmsg))
            
        # self.create_time = itchat_msg["CreateTime"]
        # self.from_user_id = itchat_msg["FromUserName"]
        # self.to_user_id = itchat_msg["ToUserName"]
        
        model_type = 'llmcc-' + str(botId) # test
        context = self._compose_context(cmsg.ctype, cmsg.content, isgroup=False, msg=cmsg, from_user_id=tenantId, from_user_nickname='web', )
        self.produce(context)
        rr = self.consume(context["session_id"], model_type)
        # print('after consume 22 ', rr)
        return rr

    # 根据消息构造context，消息内容相关的触发项写在这里
    def _compose_context(self, ctype: ContextType, content, **kwargs):
        context = Context(ctype, content)
        context.kwargs = kwargs
        
        context["session_id"] = kwargs.get("from_user_id", "web")
        context["receiver"] = 'web'
        
        nick_name = context["msg"].from_user_nickname # fixme 
        if nick_name and nick_name in self.nick_name_black_list:
            # 黑名单过滤
            logger.warning(f"[WX] Nickname '{nick_name}' in In BlackList, ignore")
            return None

        match_prefix = check_prefix(content, conf().get("single_chat_prefix", [""]))
        if match_prefix is not None:  # 判断如果匹配到自定义前缀，则返回过滤掉前缀+空格后的内容
            content = content.replace(match_prefix, "", 1).strip()
        elif context["origin_ctype"] == ContextType.VOICE:  # 如果源消息是私聊的语音消息，允许不匹配前缀，放宽条件
            pass
        else:
            return None
        return context
        
        
    def produce(self, context: Context):
        session_id = context["session_id"]
        # with self.lock:
        if session_id not in self.sessions:
            self.sessions[session_id] = [
                Dequeue(),
                # [],
                threading.BoundedSemaphore(conf().get("concurrency_in_session", 4)),
            ]
        if context.type == ContextType.TEXT and context.content.startswith("#"):
            self.sessions[session_id][0].putleft(context)  # 优先处理管理命令
        else:
            self.sessions[session_id][0].put(context)
            # [].append

    def _handle(self, context: Context, model_type=None):
        if context is None or not context.content:
            return
        logger.debug("[WX] ready to handle context: {}".format(context))
        # reply的构建步骤
        reply = self._generate_reply(context, model_type=model_type)

        logger.debug("[WX] ready to decorate reply: {}".format(reply))
        # reply的包装步骤
        reply = self._decorate_reply(context, reply)
        # print('after _decorate_reply ', reply)
        if reply and reply.type:
            e_context = PluginManager().emit_event(
                EventContext(
                    Event.ON_SEND_REPLY,
                    {"channel": self, "context": context, "reply": reply},
                )
            )
            reply2 = e_context["reply"]
            if not reply2:
                pass
            if not e_context.is_pass() and reply and reply.type:
                logger.error("[WX] ready to send reply: {}, context: {}".format(reply, context))
                # self._send(reply, context)
                return reply
        return reply

    def _send(self, reply: Reply, context: Context, retry_cnt=0):
        try:
            self.send(reply, context)
        except Exception as e:
            logger.error("[WX] sendMsg error: {}".format(str(e)))
            if isinstance(e, NotImplementedError):
                return
            logger.exception(e)
            if retry_cnt < 2:
                time.sleep(3 + 3 * retry_cnt)
                self._send(reply, context, retry_cnt + 1)
                
                
    # 消费者函数，单独线程，用于从消息队列中取出消息并处理
    def consume(self, session_id, model_type): 
        context_queue, semaphore = self.sessions[session_id]
        if not context_queue.empty():
            # context = context_queue.get()
            context = context_queue.get_nowait()
            logger.error("[WX] consume context: {}".format(context))
            
            try:
                reply = self._handle(context, model_type=model_type)
                
                if not reply:
                    self._fail_callback(session_id, exception='consume err', asa=1)
                else:
                    self._success_callback(session_id, asa=1)
            # except CancelledError as e:
                # logger.info("Worker cancelled, session_id = {}".format(session_id))
            except Exception as e:
                logger.exception("Worker raise exception: {}".format(e))
                print('after ExceptionException ', reply)
            return reply
        return 'err'
            
    # @time_checker
    # @_check
    def handle_group(self, cmsg: ChatMessage):
        if cmsg.ctype == ContextType.VOICE:
            if conf().get("group_speech_recognition") != True:
                return
            logger.debug("[WX]receive voice for group msg: {}".format(cmsg.content))
        elif cmsg.ctype == ContextType.IMAGE:
            logger.debug("[WX]receive image for group msg: {}".format(cmsg.content))
        elif cmsg.ctype in [ContextType.JOIN_GROUP, ContextType.PATPAT, ContextType.ACCEPT_FRIEND]:
            logger.debug("[WX]receive note msg: {}".format(cmsg.content))
        elif cmsg.ctype == ContextType.TEXT:
            # logger.debug("[WX]receive group msg: {}, cmsg={}".format(json.dumps(cmsg._rawmsg, ensure_ascii=False), cmsg))
            pass
        elif cmsg.ctype == ContextType.FILE:
            logger.debug(f"[WX]receive attachment msg, file_name={cmsg.content}")
        else:
            logger.debug("[WX]receive group msg: {}".format(cmsg.content))
        context = self._compose_context(cmsg.ctype, cmsg.content, isgroup=True, msg=cmsg)
        if context:
            self.produce(context)

    # 统一的发送函数，每个Channel自行实现，根据reply的type字段发送不同类型的消息
    def send(self, reply: Reply, context: Context):
        receiver = context["receiver"]
        if reply.type == ReplyType.TEXT:
            itchat.send(reply.content, toUserName=receiver)
            logger.info("[WX] sendMsg={}, receiver={}".format(reply, receiver))
        elif reply.type == ReplyType.ERROR or reply.type == ReplyType.INFO:
            itchat.send(reply.content, toUserName=receiver)
            logger.info("[WX] sendMsg={}, receiver={}".format(reply, receiver))
        elif reply.type == ReplyType.VOICE:
            itchat.send_file(reply.content, toUserName=receiver)
            logger.info("[WX] sendFile={}, receiver={}".format(reply.content, receiver))
        elif reply.type == ReplyType.IMAGE_URL:  # 从网络下载图片
            img_url = reply.content
            logger.debug(f"[WX] start download image, img_url={img_url}")
            pic_res = requests.get(img_url, stream=True)
            image_storage = io.BytesIO()
            size = 0
            for block in pic_res.iter_content(1024):
                size += len(block)
                image_storage.write(block)
            logger.info(f"[WX] download image success, size={size}, img_url={img_url}")
            image_storage.seek(0)
            itchat.send_image(image_storage, toUserName=receiver)
            logger.info("[WX] sendImage url={}, receiver={}".format(img_url, receiver))
        elif reply.type == ReplyType.IMAGE:  # 从文件读取图片
            image_storage = reply.content
            image_storage.seek(0)
            itchat.send_image(image_storage, toUserName=receiver)
            logger.info("[WX] sendImage, receiver={}".format(receiver))
        elif reply.type == ReplyType.FILE:  # 新增文件回复类型
            file_storage = reply.content
            itchat.send_file(file_storage, toUserName=receiver)
            logger.info("[WX] sendFile, receiver={}".format(receiver))
        elif reply.type == ReplyType.VIDEO:  # 新增视频回复类型
            video_storage = reply.content
            itchat.send_video(video_storage, toUserName=receiver)
            logger.info("[WX] sendFile, receiver={}".format(receiver))
        elif reply.type == ReplyType.VIDEO_URL:  # 新增视频URL回复类型
            video_url = reply.content
            logger.debug(f"[WX] start download video, video_url={video_url}")
            video_res = requests.get(video_url, stream=True)
            video_storage = io.BytesIO()
            size = 0
            for block in video_res.iter_content(1024):
                size += len(block)
                video_storage.write(block)
            logger.info(f"[WX] download video success, size={size}, video_url={video_url}")
            video_storage.seek(0)
            itchat.send_video(video_storage, toUserName=receiver)
            logger.info("[WX] sendVideo url={}, receiver={}".format(video_url, receiver))
