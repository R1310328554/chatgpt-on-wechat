# encoding:utf-8

import time,os

# import quivr.error

from bot.bot import Bot
# from bot.quivr.quivr_image import QuivrImage
from bot.quivr.quivr_session import QuivrSession
from bot.session_manager import SessionManager
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from config import conf
import requests,json

user_session = dict()


# Quivr对话模型API (可用)
class QuivrBot(Bot):
    def __init__(self):
        super().__init__()
        self.email = conf().get("email")
        self.chat_id = self.email

        self.sessions = SessionManager(QuivrSession, model=conf().get("model") or "text-davinci-003")
        self.args = {
            "model": conf().get("model") or "text-davinci-003",  # 对话模型的名称
            "temperature": conf().get("temperature", 0.9),  # 值在[0,1]之间，越大表示回复越具有不确定性
            "max_tokens": 1200,  # 回复最大的字符数
            "top_p": 1,
            "frequency_penalty": conf().get("frequency_penalty", 0.0),  # [-2,2]之间，该值越大则更倾向于产生不同的内容
            "presence_penalty": conf().get("presence_penalty", 0.0),  # [-2,2]之间，该值越大则更倾向于产生不同的内容
            "request_timeout": conf().get("request_timeout", None),  # 请求超时时间，quivr接口默认设置为600，对于难问题一般需要较长时间
            "timeout": conf().get("request_timeout", None),  # 重试超时时间，在这个时间内，将会自动重试
            "stop": ["\n\n\n"],
        }

    def reply(self, query, context=None):
        # acquire reply content
        if context and context.type:
            if context.type == ContextType.TEXT:
                logger.info("[quivr] query={}".format(query))
                session_id = context["session_id"]
                reply = None
                if query == "#清除记忆":
                    self.sessions.clear_session(session_id)
                    reply = Reply(ReplyType.INFO, "记忆已清除")
                elif query == "#清除所有":
                    self.sessions.clear_all_session()
                    reply = Reply(ReplyType.INFO, "所有人记忆已清除")
                else:
                    session = self.sessions.session_query(query, session_id)
                    result = self.reply_text(session,0 , query)
                    total_tokens, completion_tokens, reply_content = (
                        result["total_tokens"],
                        result["completion_tokens"],
                        result["content"],
                    )
                    logger.debug(
                        "[quivr] new_query={}, session_id={}, reply_cont={}, completion_tokens={}".format(str(session), session_id, reply_content, completion_tokens)
                    )

                    if total_tokens == 0:
                        reply = Reply(ReplyType.ERROR, reply_content)
                    else:
                        self.sessions.session_reply(reply_content, session_id, total_tokens)
                        reply = Reply(ReplyType.TEXT, reply_content)
                return reply
            elif context.type == ContextType.IMAGE_CREATE:
                ok, retstring = self.create_img(query, 0)
                reply = None
                if ok:
                    reply = Reply(ReplyType.IMAGE_URL, retstring)
                else:
                    reply = Reply(ReplyType.ERROR, retstring)
                return reply

    def reply_text(self, session: QuivrSession, retry_count=0, question=''):
        try:
            
            brain_id = os.getenv('brain_id')
            if not brain_id:
                brain_id = '1b0657cf-60a4-4531-be23-99af3733e2b3'
            print('brain_id: ', brain_id)
                  
            demoReq = {
            "question": question,
            # "model": "gpt-4",
            "max_tokens": 204,
            "brain_id": brain_id
            }
            # email = 'hnczlk@sina.com'
            chat_id = self.chat_id
            brain_id = demoReq['brain_id']
            
            quivr_host = os.getenv('quivr_host')
            if not quivr_host:
                quivr_host = 'localhost'
            print('quivr_host: ', quivr_host)
            url = f'http://{quivr_host}:5050/chat/{chat_id}/question2?brain_id={brain_id}'
            headers = {
                'accept': 'application/json',
                "Content-Type": "application/json"
            }
            response = requests.post(url, headers=headers, json=demoReq ) # params=demoReq,
            print(response.status_code) # 输出请求状态码
            if response.status_code == 429:
                #  429 Too Many Requests
                print(' 429 Too Many Requests ')
                result = {"completion_tokens": 0, "total_tokens": 0, "content": "提问太快啦，请休息一下再问我吧"}
                return result
                
            print(response.text)
            print('response.++++++++++++++++  ') # str(response.content,encoding='utf-8')
            # print(response.content)
            # resStr = response.content.decode('utf-8')  # 可以直接 response.json() 
            resJson = json.loads(response.text)
            return {
                "total_tokens": len(question),
                "completion_tokens": len(resJson),
                "content": resJson.get('assistant'),
            }
        except Exception as e:
            need_retry = retry_count < 2
            result = {"completion_tokens": 0, "total_tokens": 0, "content": "请求异常~"}
            import openai
            if isinstance(e, openai.error.RateLimitError):
                logger.warn("[OPEN_AI] RateLimitError: {}".format(e))
                result["content"] = "提问太快啦，请休息一下再问我吧"
                if need_retry:
                    time.sleep(20)
            elif isinstance(e, openai.Timeout):
                logger.warn("[OPEN_AI] Timeout: {}".format(e))
                result["content"] = "我没有收到你的消息"
                if need_retry:
                    time.sleep(5)
            elif isinstance(e, openai.APIConnectionError):
                logger.warn("[OPEN_AI] APIConnectionError: {}".format(e))
                need_retry = False
                result["content"] = "我连接不到你的网络"
            else:
                logger.warn("[OPEN_AI] Exception: {}".format(e))
                need_retry = False
                self.sessions.clear_session(session.session_id)

            if need_retry:
                logger.warn("[OPEN_AI] 第{}次重试".format(retry_count + 1))
                return self.reply_text(session, retry_count + 1)
            else:
                return result
            
def ass():
    #使用请求头
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 ',
            'Host': 'movie.douban.com',
            'Referer': 'https://movie.douban.com/typerank?', 
    }
    #携带cookies
    cookies = {'Cookie':' bid=vcLghJHKdzE; __utmz=30149280.1608554450.1.1.utmcsr=(direct)|utmccn='}
    #携带请求参数
    params = {
                'type':'11',
                'interval_id':'100:90',
                'action':'unwatched+playable',
                'start':str(i*20),
                'limit':'20',
        }
    #设置代理池 ip
    proxy = {
        'http':'101.236.155.89:8899',
        'https':'101.236.155.89:7799'
    }
    url = 'https://movie.douban.com/j/chart/top_list?'

    res=requests.get(url,headers=headers,params=params,cookies=cookies,proxies=proxy)
    print(response.status_code) #输出请求状态码
    print(response.content.decode('utf-8')) #输出请求结果 

# class ChatQuestion(BaseModel):
#     question: str
#     model: Optional[str]
#     temperature: Optional[float]
#     max_tokens: Optional[int]
#     brain_id: Optional[UUID]
#     prompt_id: Optional[UUID]

# class GetChatHistoryOutput(BaseModel):
#     chat_id: UUID
#     message_id: UUID
#     user_message: str
#     assistant: str
#     message_time: str
#     prompt_title: Optional[str] | None
#     brain_name: Optional[str] | None
    

#     return GetChatHistoryOutput(
#         **{
#             "chat_id": chat_id,
#             "user_message": question.question,
#             "assistant": answer,
#             "message_time": new_chat.message_time,
#             "prompt_title": self.prompt_to_use.title
#             if self.prompt_to_use
#             else None,
#             "brain_name": brain.name if brain else None,
#             "message_id": new_chat.message_id,
#         }
#     )