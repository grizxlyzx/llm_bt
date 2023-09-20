import os
import openai
from llm.prompts import *

openai.api_base = 'https://api.chatanywhere.com.cn'
# openai.api_key = 'sk-uYHTFfAmoywA6px2mVuArs0fJfqpGjmYsy6iKkDFkyh1SZOq'
# openai.api_key = "sk-bX6Q4OXQZNl1bbGD5oAP7YM6k6dsRRymgj8thx6MomELKD3h"
openai.api_key = 'sk-sz0RQYOIYoASNNxoOXmIRT2Ungeny0IC1eLr43laBCCP4ap3'

class GPT4BTChat:
    def __init__(self,
                 model_name: str = 'gpt-4-0613',
                 temperature: float = 1.,
                 max_retry: int = 10):
        self.model_name = model_name
        self.temperature = temperature
        self.chat_log = []
        self.sys_prompt = sys_prompt()
        self.max_retry = max_retry
        self.retry_cnt = 0

    def __call__(self, user_prompt):
        while self.retry_cnt < self.max_retry:
            try:
                response = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=self.make_msg(user_prompt),
                    max_token=4096,
                    n=1,
                    stop=None,
                    temperature=self.temperature
                )
                self.retry_cnt = 0
                reply = response.choices[0].message['content']
                self.chat_log.append({'role': 'user', 'content': user_prompt})
                self.chat_log.append({'role': 'assistant', 'content': reply})
                return reply

            except Exception as error:
                self.retry_cnt += 1
                print(error, f'retry: {self.retry_cnt} / {self.max_retry}')
        print('max retry reached')
        return ''

    def make_msg(self, user_prompt):
        msg = [
            {'role': 'system', 'content': self.sys_prompt},
            *self.chat_log,
            {'role': 'user', 'content': user_prompt}
        ]
        return msg

    def clear(self):
        self.chat_log = []


