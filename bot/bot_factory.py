"""
channel factory
"""
from common import const
from bot.LangchainChatchat.llmccr_bot import LlmccBot
# from bot.LangchainChatchat.bot_service import selectById
from bot.LangchainChatchat import bot_service


def create_bot(bot_type, **kwargs):
    """
    create a bot_type instance
    :param bot_type: bot type code
    :return: bot instance
    """
    print('kwargs: ', kwargs)
    kwModel = kwargs.get("model_type")
    print('kwModel: ', kwModel)
    if  kwModel:
        bot_type = kwModel
    
    if bot_type == const.BAIDU:
        # 替换Baidu Unit为Baidu文心千帆对话接口
        # from bot.baidu.baidu_unit_bot import BaiduUnitBot
        # return BaiduUnitBot()
        from bot.baidu.baidu_wenxin import BaiduWenxinBot
        return BaiduWenxinBot()

    elif bot_type == const.CHATGPT:
        # ChatGPT 网页端web接口
        from bot.chatgpt.chat_gpt_bot import ChatGPTBot
        return ChatGPTBot()

    elif bot_type == const.OPEN_AI:
        # OpenAI 官方对话模型API
        from bot.openai.open_ai_bot import OpenAIBot
        return OpenAIBot()

    # elif bot_type == const.LLMCC:
    elif bot_type.startswith("llmcc-"):
        # LangchainChatchat 官方对话模型API
        botId = bot_type.split('-')[-1]
        if not botId:
            raise RuntimeError
        # bot = selectById(botId)
        bot = bot_service.selectById(botId)
        print('bot: ', bot)
        kwargs = bot.__dict__
        print('kwargs: ', kwargs)
        sadf = {'max_ctx_len': 1234567,
            'model_name': kwargs.get("model", 'openai-api'), 
            'role': kwargs.get("role", 'assistant'), 
            'temperature': kwargs.get("temperature", 0.5), 
            'max_tokens': kwargs.get("max_tokens", 10240), 
            'top_k': kwargs.get("top_k", 3),
            'score_threshold': kwargs.get("score_threshold", 1),
            'max_ctx_len': kwargs.get("max_ctx_len", 1000), 
            'knowledge_base_name': kwargs.get("knowledge_base_name", 'test'), 
            'prompt_name': kwargs.get("prompt_name", 'default'),
            
            'post': kwargs.get("post", 'sales'), 
            'speed': kwargs.get("speed", 100), 
            'init_reply': kwargs.get("init_reply", 'hello aiii'), 
            'user_info_collector': kwargs.get("user_info_collector", '你好， 可以告诉我您的手机号吗'), 
            'avatar': kwargs.get("avatar", 'https://www.baidu.com/img/bd_logo1.png'), 
            'name': kwargs.get("name", 'aiii'), 
            
            'reply_delay': kwargs.get("reply_delay", 111), 
            'rate_limit_duration': kwargs.get("rate_limit_duration", 111), 
            'rate_limit_prompt': kwargs.get("rate_limit_prompt", 111), 
            'rate_limit_questions': kwargs.get("rate_limit_questions", 111), 
        }
        return LlmccBot(**sadf)
    

    elif bot_type == const.QUIVR:
        # OpenAI 官方对话模型API
        from bot.quivr.quivr_bot import QuivrBot
        return QuivrBot()

    elif bot_type == const.CHATGPTONAZURE:
        # Azure chatgpt service https://azure.microsoft.com/en-in/products/cognitive-services/openai-service/
        from bot.chatgpt.chat_gpt_bot import AzureChatGPTBot
        return AzureChatGPTBot()

    elif bot_type == const.XUNFEI:
        from bot.xunfei.xunfei_spark_bot import XunFeiBot
        return XunFeiBot()

    elif bot_type == const.LINKAI:
        from bot.linkai.link_ai_bot import LinkAIBot
        return LinkAIBot()

    elif bot_type == const.CLAUDEAI:
        from bot.claude.claude_ai_bot import ClaudeAIBot
        return ClaudeAIBot()
    raise RuntimeError
