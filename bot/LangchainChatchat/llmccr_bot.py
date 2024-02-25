# encoding:utf-8

import time,os

# import llmccr.error

from bot.bot import Bot
# from bot.llmccr.llmccr_image import LlmccrImage
from bot.LangchainChatchat.llmccr_session import LlmccrSession
from bot.session_manager import SessionManager
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from config import conf
import requests,json

user_session = dict()


# Llmccr对话模型API (可用)
class LlmccBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__()
        
        print('kwargs 2222 : ', kwargs)
        
        self.email = kwargs.get("email")
        model_name = kwargs.get("model")
        role = kwargs.get("role")
        temperature = kwargs.get("temperature")
        max_ctx_len = kwargs.get("max_ctx_len")
        top_k = kwargs.get("top_k", 3)
        score_threshold = kwargs.get("score_threshold", 1)
        max_ctx_len = kwargs.get("max_ctx_len")
        knowledge_base_name = kwargs.get("knowledge_base_name")
        prompt_name = kwargs.get("prompt_name", 'default')
        
        post = kwargs.get("post")
        speed = kwargs.get("speed")
        init_reply = kwargs.get("init_reply")
        speed = kwargs.get("speed")
        user_info_collector = kwargs.get("user_info_collector")
        avatar = kwargs.get("avatar")
        name = kwargs.get("name")
        
        reply_delay = kwargs.get("reply_delay")
        rate_limit_duration = kwargs.get("rate_limit_duration")
        rate_limit_prompt = kwargs.get("rate_limit_prompt")
        rate_limit_questions = kwargs.get("rate_limit_questions")
        
        llmccr_host = os.getenv('llmccr_host')
        if not llmccr_host:
            llmccr_host = conf().get("llmccr_host", 'https://home.asc-ai.cn')
        print('llmccr_host: ', llmccr_host)
        self.llmccr_host = llmccr_host
        self.chat_type = conf().get("chat_type", 'chat/knowledge_base_chat')
        if not self.chat_type:
            self.chat_type = 'chat/knowledge_base_chat'

        print('SessionManager: ', name, max_ctx_len)
        self.sessions = SessionManager(LlmccrSession, model="openai-api", max_ctx_len=max_ctx_len)
        self.args = {
            # "query": "符号占位数据类型差异方案",
            "model_name": model_name, # "openai-api",  # 对话模型的名称
            "temperature": temperature,  # 值在[0,1]之间，越大表示回复越具有不确定性
            "max_ctx_len": max_ctx_len,  # 回复最大的字符数
            "max_tokens": 2048,
            "top_k": top_k,
            "score_threshold": score_threshold,
            "knowledge_base_name": knowledge_base_name,
            "stream": False,
            "prompt_name": prompt_name,
            
            "init_reply": init_reply,
            "frequency_penalty": conf().get("frequency_penalty", 0.0),  # [-2,2]之间，该值越大则更倾向于产生不同的内容
            "presence_penalty": conf().get("presence_penalty", 0.0),  # [-2,2]之间，该值越大则更倾向于产生不同的内容
            "request_timeout": conf().get("request_timeout", None),  # 请求超时时间，llmccr接口默认设置为600，对于难问题一般需要较长时间
            "timeout": conf().get("request_timeout", None),  # 重试超时时间，在这个时间内，将会自动重试
            "stop": ["\n\n\n"],
            
            # "history": [
            #     {
            #       "role": "user",
            #       "content": "我们来玩成语接龙，我先来，生龙活虎"
            #     },
            #     {
            #       "role": "assistant",
            #       "content": "虎头虎脑"
            #     }
            #   ],
            # 
        }
        self.args2 = kwargs

    def reply(self, query, context=None):
        # acquire reply content
        if context and context.type:
            if context.type == ContextType.TEXT:
                logger.info("[llmccr] query={}".format(query))
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
                    result = self.reply_text(session, 0 , query)
                    total_tokens, completion_tokens, reply_content = (
                        result["total_tokens"],
                        result["completion_tokens"],
                        result["content"],
                    )
                    logger.debug(
                        "[llmccr] new_query={}, session_id={}, reply_cont={}, completion_tokens={}".format(str(session), session_id, reply_content, completion_tokens)
                    )

                    if total_tokens == 0:
                        reply = Reply(ReplyType.ERROR, reply_content)
                    else:
                        self.sessions.session_reply(reply_content, session_id, total_tokens)  
                        # 这个什么意思？为什么要session_reply？
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

    def reply_text0(self, session: LlmccrSession, retry_count=0):
        # try:
            response = openai.Completion.create(prompt=str(session), **self.args)
            res_content = response.choices[0]["text"].strip().replace("<|endoftext|>", "")
            
    def reply_text(self, session: LlmccrSession, retry_count=0, question=''):
        try:
            historyArr = str(session)
            print('historyArr: ', historyArr)
            
            demoReq = {
            "query": question,
            "history": session.messages
            }
            
            print('demoReq: ', demoReq)
            
            demoReq.update(self.args)
            # email = 'hnczlk@sina.com'
            
            url = f'{self.llmccr_host}/{self.chat_type}'
            headers = {
                'accept': 'application/json',
                "Content-Type": "application/json"
            }
            print('url ', url)
            # response = requests.post(url, headers=headers, json=demoReq ) # params=demoReq,
            response = {
                'status_code': 200,
                'text': '{"assistant": "我不知道你在说什么, 原样返回: ' + question +'"}'
                # 'text': f'{"assistant": "我不知道你在说什么, 原样返回: {question}"}'
            }
            
            # 把 response 这个 dict 做成可通过点操作符直接获取status_code的对象， 比如 response.status_code
            
            # 把dict对象做成可通过点操作符直接获取属性的对象， 比如 response.status_code
            
            from types import SimpleNamespace
            response = SimpleNamespace(**response)
                        
            # resJson = json.loads(response) # err
            
            print(response.status_code) # 输出请求状态码
            if response.status_code == 429:
                #  429 Too Many Requests
                print(' 429 Too Many Requests ')
                result = {"completion_tokens": 0, "total_tokens": 0, "content": "提问太快啦，请休息一下再问我吧"}
                return result
                
            if response.status_code == 422:
                print(' 422 Validation Error ')
                result = {"completion_tokens": 0, "total_tokens": 0, "content": "请求参数错误~"}
                return result
                
            if response.status_code == 405:
                print(' 405 Method Not Allowed Error ')
                result = {"completion_tokens": 0, "total_tokens": 0, "content": "请求参数错误~"}
                return result
                
            print(response.text, type(response.text))
            resJson = json.loads(response.text)
            print('response.++++++++++++++++  ', resJson) 
            
            if not resJson.get('assistant'):
                print(' not answer.. ')
                result = {"completion_tokens": 0, "total_tokens": 0, "content": "请求参数错误~"}
                return result
                # str(response.content,encoding='utf-8')
            # print(response.content)
            # resStr = response.content.decode('utf-8')  # 可以直接 response.json() 
            return {
                "total_tokens": len(question), # todo , 如何计算总的tokens
                "completion_tokens": len(resJson),
                "content": resJson.get('assistant'),
            }
        except Exception as e:
            need_retry = retry_count < 2
            result = {"completion_tokens": 0, "total_tokens": 0, "content": "请求异常~"}
            import openai
            if isinstance(e, openai.error.RateLimitError):
                logger.warn("[LangchainChatchat] RateLimitError: {}".format(e))
                result["content"] = "提问太快啦，请休息一下再问我吧"
                if need_retry:
                    time.sleep(20)
            elif isinstance(e, openai.Timeout):
                logger.warn("[LangchainChatchat] Timeout: {}".format(e))
                result["content"] = "我没有收到你的消息"
                if need_retry:
                    time.sleep(5)
            elif isinstance(e, openai.APIConnectionError):
                logger.warn("[LangchainChatchat] APIConnectionError: {}".format(e))
                need_retry = False
                result["content"] = "我连接不到你的网络"
            else:
                logger.warn("[LangchainChatchat] Exception: {}".format(e))
                need_retry = False
                self.sessions.clear_session(session.session_id)

            if need_retry:
                logger.warn("[LangchainChatchat] 第{}次重试".format(retry_count + 1))
                return self.reply_text(session, retry_count + 1)
            else:
                return result
            