# encoding:utf-8

import os
import signal
import sys

from channel import channel_factory
from common import const
from config import load_config
from plugins import *
from multiprocessing import Process



def sigterm_handler_wrap(_signo):
    old_handler = signal.getsignal(_signo)

    def func(_signo, _stack_frame):
        logger.info("signal {} received, exiting...".format(_signo))
        conf().save_user_datas()
        if callable(old_handler):  #  check old_handler
            return old_handler(_signo, _stack_frame)
        sys.exit(0)

    signal.signal(_signo, func)


def run(model_type=''):
    print('run 1111111111 ', model_type)
    try:
        # load config
        load_config()
        # ctrl + c
        sigterm_handler_wrap(signal.SIGINT)
        # kill signal
        sigterm_handler_wrap(signal.SIGTERM)

        # create channel
        channel_name = conf().get("channel_type", "wx")

        if "--cmd" in sys.argv:
            channel_name = "terminal"

        if channel_name == "wxy":
            os.environ["WECHATY_LOG"] = "warn"
            # os.environ['WECHATY_PUPPET_SERVICE_ENDPOINT'] = '127.0.0.1:9001'

        channel = channel_factory.create_channel(channel_name, model_type=model_type)
        if channel_name in ["wx", "wxy", "terminal", "wechatmp", "wechatmp_service", "wechatcom_app", "wework", const.FEISHU]:
            # PluginManager().load_plugins()
            pass

        # startup channel
        channel.startup(model_type=model_type, callback=qrCallback)
    except Exception as e:
        logger.error("App startup failed!")
        logger.exception(e)

def qrCallback(uuid, status, qrcode):
    print(f"uuid: {uuid}, status: {status}, qrcode: {1}")
    if status == 'Scan':
        print('Please scan the QR code to log in')
        print(f'qrcode: {qrcode}')
    elif status == 'Confirm':
        print('Please press the confirm button')
    elif status == 'Login':
        print('Login successfully')
    elif status == 'Logout':
        print('Logout successfully')
    elif status == 'Error':
        print('Error')
    elif status == 'Wait':
        print('Waiting...')
    elif status == 'Unknown':
        print('Unknown status')
        
    url = f"https://login.weixin.qq.com/l/{uuid}"
    qr_api1 = "https://api.isoyu.com/qr/?m=1&e=L&p=20&url={}".format(url)
    qr_api2 = "https://api.qrserver.com/v1/create-qr-code/?size=400×400&data={}".format(url)
    print("You can also scan QRCode in any website below:")
    print(qr_api1)
    print(qr_api2) # url失效
    
    return uuid, status, qrcode
    
def test12():
    print(111)
    pass

def test12():
    param = {
      "chat_id": "1936351d-45b0-4488-a037-9cbad617e06e",
      "user_id": "848805ca-1633-417b-a575-0f8b9584986b",
    "model": "gpt-4",
    "temperature": 0,
    "max_tokens2": 2048,
      "creation_time": "2023-11-30T12:03:54.034668",
      "chat_name": "1+2+3+...+99+1000"
    }
    
    demoReq = {
    "question2": "how many states does Korea have, anwser in 10 words",
    "question1": "how many states in world, anwser in 10 words",
    "question": "1/0",
    "max_tokens": 204,
    "brain_id": "22eca0ed-f0a9-4c14-9473-815808b207d9" 
    }
    import requests
    email = 'hnczlk@sina.com'
    chat_id = param['chat_id']
    brain_id = demoReq['brain_id']
    url = f'http://localhost:5050/chat/{chat_id}/question'
    url = f'http://localhost:5050/chat/{chat_id}/question2?brain_id={brain_id}'
    cookies = {}
    proxy = {}
    params = {}
    headers = {
        'accept': 'application/json',
        "Content-Type": "application/json"
    }
    response = requests.post(url, cookies=cookies,proxies=proxy, json=demoReq ) # params=demoReq, headers=headers, 
    print(response.status_code) #输出请求状态码
    print(response.content.decode('utf-8')) #输出请求结果
    
def f(name):
    print('hello', name)

def start_app(model_type):
    p = Process(target=run, args=(model_type,))
    p.start()
    p.join()
    
def start_app2(model_type):
    # 通过创建新进程的方式启动服务
    pid = os.fork()
    if pid == 0:
        run(model_type)
    else:
        # 将当前进程的id写入文件
        with open('run.pid', 'w') as f:
            f.write(str(pid))
            f.close()
        # 等待子进程结束
        os.waitpid(pid, 0)
        # 删除pid文件
        os.remove('run.pid')
        print('app exit')

if __name__ == "__main__":
    # run()
    start_app('llmcc-1')
    # test12()
    # 将当前进程的id写入文件
    with open('run.pid', 'w') as f:
        f.write(str(os.getpid()))
        f.close()
    
    from bot.LangchainChatchat import fastapi_main
    fastapi_main.startHttpServer()
    
    # find . -type f -exec sed -i 's/openai/openai/g' {} + 
    # docker pull ghcr.io/stangirard/quivr:v0.0.161
    
    
# class ChatQuestion( ):
#     question: str
#     model: str
#     temperature: float
#     max_tokens: int
#     brain_id: UUID
#     prompt_id: UUID
