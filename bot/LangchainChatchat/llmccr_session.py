from bot.session_manager import Session
from common.log import logger


class LlmccrSession(Session):
    def __init__(self, session_id, system_prompt=None, model="azure-api", max_ctx_len=1024):
        super().__init__(session_id, system_prompt)
        self.model = model
        
        print('LlmccrSession: ', session_id, system_prompt, model, max_ctx_len)
        self.max_ctx_len = max_ctx_len
        self.reset()
        
        self.query = ''

    def __str__(self):
        # 构造对话模型的输入
        """
        e.g.  Q: xxx
              A: xxx
              Q: xxx
        """
        prompt = ""
        for item in self.messages:
            if item["role"] == "system":
                prompt += item["content"] + "<|endoftext|>\n\n\n"
            elif item["role"] == "user":
                prompt += "Q: " + item["content"] + "\n"
            elif item["role"] == "assistant":
                prompt += "\n\nA: " + item["content"] + "<|endoftext|>\n"

        if len(self.messages) > 0 and self.messages[-1]["role"] == "user":
            prompt += "A: "
        return prompt
    

    def add_query(self, query):
        if len(self.messages) >= self.max_ctx_len:
            print("add_query: 已经超过了最大的 上下文记忆量，超过则舍弃前面部分的对话 session_id={}, query={}".format(self.session_id, query))
            self.messages.pop(0)
        
        self.query = query
        
        # user_item = {"role": "user", "content": query}
        # self.messages.append(user_item)

    def add_reply(self, reply):
        
        # if self.messages[-1]["role"] == "assistant":
        super().add_query(self.query) # 为什么这里要加上query？ 因为 llmcc的特殊性, 不能污染history， 
        
        if len(self.messages) >= self.max_ctx_len:
            print("add_reply: 已经超过了最大的 上下文记忆量，超过则舍弃前面部分的对话 session_id={}, reply={}".format(self.session_id, reply))
            self.messages.pop(0)
        assistant_item = {"role": "assistant", "content": reply}
        self.messages.append(assistant_item)

    def discard_exceeding(self, max_tokens, cur_tokens=None):
        precise = True
        try:
            cur_tokens = self.calc_tokens()
        except Exception as e:
            precise = False
            if cur_tokens is None:
                raise e
            logger.debug("Exception when counting tokens precisely for query: {}".format(e))
        while cur_tokens > max_tokens:
            if len(self.messages) > 1:
                self.messages.pop(0)
            elif len(self.messages) == 1 and self.messages[0]["role"] == "assistant":
                self.messages.pop(0)
                if precise:
                    cur_tokens = self.calc_tokens()
                else:
                    cur_tokens = len(str(self))
                break
            elif len(self.messages) == 1 and self.messages[0]["role"] == "user":
                logger.warn("user question exceed max_tokens. total_tokens={}".format(cur_tokens))
                break
            else:
                logger.debug("max_tokens={}, total_tokens={}, len(conversation)={}".format(max_tokens, cur_tokens, len(self.messages)))
                break
            if precise:
                cur_tokens = self.calc_tokens()
            else:
                cur_tokens = len(str(self))
        return cur_tokens

    def calc_tokens(self):
        return num_tokens_from_string(str(self), self.model)


# refer to https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
def num_tokens_from_string(string: str, model: str) -> int:
    """Returns the number of tokens in a text string."""
    import tiktoken

    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(string, disallowed_special=()))
    return num_tokens
