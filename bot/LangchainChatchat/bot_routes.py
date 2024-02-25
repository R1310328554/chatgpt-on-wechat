import time
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Query
# from middlewares.auth.auth_bearer import AuthBearer, get_current_user
from bot.LangchainChatchat import bot_service
from bot.bot_factory import create_bot
from channel.chat_channel import ChatChannel
from bot.LangchainChatchat.llmccr_bot import LlmccBot
from channel.web.web_channel import WebChannel
from channel.web.web_message import WebMessage

from plugins import *
from bridge.context import *
from bridge.reply import *
from lib.itchat.content import *

brain_router = APIRouter()

@brain_router.get("/startBot/{tenantId}/{botId}/{chatType}"
                #   , dependencies=[Depends(AuthBearer())]
                  , tags=["bot management"])
async def startBot(
    tenantId: str,
    botId: str,
    chatType: str,
    # current_user: UserIdentity = Depends(get_current_user),
    # knowledge_id: str = Query(..., description="The ID of the brain"),
    query: str = Query(..., description="Hi"),
):
    """ 创建对应的聊天机器人，并返回初始信息 .  下次进入则可以直接进行聊天对话， 不需要再次创建。"""
    # current_user = await get_current_user()
    bot:LlmccBot = create_bot('llmcc-' + botId)
    
    botEntity = bot.args
    if query == 'hello':
        # return {"reply": botEntity.init_reply}
        return {"reply": botEntity.get("init_reply")}
    # bot = await get_bot(botId)
    # bot = await get_bot('llmcc-' + botId)
    return {"reply": botEntity.get("init_reply")}


webChannel = WebChannel()

@brain_router.get("/botchat/{tenantId}/{botId}"
                #   , dependencies=[Depends(AuthBearer())]
                  , tags=["bot chat"])
async def botchat(
    botId: str,
    tenantId: str,
    # chatType: str,
    query: str,
):
    """  直接进行聊天对话， 不需要再次创建。"""
    # current_user = await get_current_user()
    if not query:
        raise HTTPException(status_code=400, detail="query is empty")
    
    chatType = ''
    if chatType == "wechat":
        # ChatChannel
        pass
    itchat_msg = {"FromUserName": 'web', "ToUserName": 'filehelper', "Content": query, "Text": query, 'IsAt': 'llmcc'
                  , "Type": TEXT, "MsgId": tenantId, "CreateTime": time.time()}
    # self.from_user_id = itchat_msg["FromUserName"]
    # self.to_user_id = itchat_msg["ToUserName"]
    # LlmccBot, ContextType.TEXT
    msg = WebMessage(itchat_msg, tenantId, botId, is_group=False)
    reply = webChannel.handle_single(msg, tenantId, botId)
    print('replyreplyreply ', reply)
    return {"reply": reply}



async def get_bot(botId):
    # 通过 botId 从mysql 查询对应的bot
    bot = bot_service.selectById(botId)
    return bot
    pass