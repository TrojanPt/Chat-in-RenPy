

"""renpy
init python:
"""

import json
import hashlib
from pathlib import Path
import os

#########################
import requests
import threading

class LLM_api_connection:
    def __init__(self, url, method, data, headers):
        self.url = url
        self.method = method
        self.data = data
        self.headers = headers
        self.buffer = ""
        self._thread = None
    
    def _call_stream_llm(self):
        """流式请求工作线程"""
        response = requests.request(self.method, self.url, data=self.data, headers=self.headers, stream=True)
        response.raise_for_status()
        
        # 逐块处理响应内容
        for line in response.iter_lines():
            if line:
                # 解码并移除开头的"data: "
                decoded_line = line.decode('utf-8').lstrip('data: ').strip()
                
                if decoded_line == "[DONE]":
                    break

                try:
                    chunk = json.loads(decoded_line)
                    content = chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')
                    if content:
                        self.buffer += content
                except json.JSONDecodeError:
                    continue
                
    def start_stream(self):
        """启动流式请求"""
        self._thread = threading.Thread(target=self._call_stream_llm)
        self._thread.start()

    def is_alive(self):
        """判断请求是否结束"""
        return self._thread.is_alive() if self._thread else False

class TTS_api_connection:
    def __init__(self, url, method, data, headers):
        self.url = url
        self.method = method
        self.data = data
        self.headers = headers
        self.buffer = []
        self._thread = None

    def _call_tts(self):
        """发送请求至tts端"""
        with requests.post(self.url, data=self.data, headers=self.headers, stream=True) as response:
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    self.buffer.append(["data", chunk])
            self.buffer.append(["done", None])
            return
    
    def start_tts(self):
        """启动tts请求"""
        self._thread = threading.Thread(target=self._call_tts)
        self._thread.start()

#########################
def call_llm(messages, response_format=None):
    """发送messages到llm端，并流式返回生成的回复"""
    url = f'{preferences.llm_api_base_url}/chat/completions'
    
    payload = {
        "messages": messages,
        "model": "deepseek-chat",      #"deepseek-chat","smegmma-deluxe-9b-v1"
        "frequency_penalty": 0,
        "max_tokens": 1024,
        "presence_penalty": 0,
        "response_format": {
            "type": "json_object"             #"json_object", "text"
        },
        "stop": None,
        "stream": True,                                 # 开启流式传输
        "stream_options": {"include_usage": True},      # 如果设置为 true，在流式消息最后的 data: [DONE] 之前将会传输一个额外的块。此块上的 usage 字段显示整个请求的 token 使用统计信息
        "temperature": 1,
        "top_p": 1,
        "tools": None,
        "tool_choice": "none",
        "logprobs": False,
        "top_logprobs": None
    }
    payload = json.dumps(payload).encode("utf-8")
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {preferences.llm_api_key}'
    }
    response = LLM_api_connection(url, "POST", payload, headers)
    response.start_stream()
    while response.is_alive():
        yield response.buffer                            #response.buffer存储已生成的对话内容
    yield response.buffer
    return

def call_tts(params):
    """发送请求参数至tts端，并返回生成的音频"""
    url = f'{preferences.tts_api_base_url}/v1/audio/speech'
    
    headers = {
        "Authorization": f"Bearer {preferences.tts_api_key}",
        "Content-Type": "application/json"
    }

    SPEECH_DIR = str(config.basedir)+ "/game/audio/speech"
    SPEECH_DIR = os.path.normpath(SPEECH_DIR)
    os.makedirs(SPEECH_DIR, exist_ok=True)

    name = hashlib.md5(
        params["input"].encode("utf-8")
        + params["model"].encode("utf-8")
        + params["voice"].encode("utf-8")
    ).hexdigest()                                         # 文件名称
    file_path = os.path.join(SPEECH_DIR, f"{name}.mp3")   # 文件路径
    if Path(file_path).is_file():                         # 判断文件是否已经存在
        yield name
        return
    
    payload = json.dumps(params).encode("utf-8")
    response = TTS_api_connection(url, "POST", payload, headers)
    tts_queue.add(response)
    tts_queue.refresh()
    with open(file_path, "wb") as f:
        while True:
            if response.buffer:
                delta = response.buffer.pop(0)
                if delta[0] == "data":
                    f.write(delta[1])
                    f.flush()
                elif delta[0] == "done":
                    break
            else:
                yield "speechfile_generating"
    yield name
    return

def cut_response(content, cut):
    """每生成完成一句话，向TTS端发送该句话"""
    punds = {'.', ';', '?', '!', '。', '？', '！', ';'}
    for i in range(cut, len(content)):
        if content[i] in punds:
            # 排除.作为小数点的情况
            if content[i] == '.' and i > 0 and i < len(content) - 1 and content[i - 1].isdigit() and content[i + 1].isdigit():
                continue
            else:
                next_cut = i + 1
                return next_cut
    return

class TTS_Queue:
    """tts请求队列"""
    def __init__(self):
        self.queue = []

    def add(self, response):
        self.queue.append([response, 0])  #0:未处理, 1:正在处理

    def next(self):
        if self.queue:
            self.queue.pop(0)
        if self.queue:
            self.queue[0][0].start_tts()
            self.queue[0][1] = 1

    def refresh(self):
        if self.queue[0][1] == 0:
            self.queue[0][0].start_tts()
            self.queue[0][1] = 1

def parse_response(response):
    '''处理llm的结构化输出,输出为一个list
    
    list = [
        {mood是否生成完毕: bool}, 
        {mood的值,若mood未生成完毕则返回已经生成了的部分},
        {saying_ja是否生成完毕: bool},
        {saying_ja的值,若saying_ja未生成完毕则返回已经生成了的部分},
        {saying_zh是否生成完毕: bool},
        {saying_zh的值,若saying_zh未生成完毕则返回已经生成了的部分}
        ]
        '''
    import re
    def process_key(key, s):
        # 检查键是否存在
        key_pattern = re.compile(r'"{}"\s*:'.format(re.escape(key)), re.DOTALL)
        key_match = key_pattern.search(s)
        if not key_match:
            return (False, '')
        
        # 查找值的开始双引号
        start_quote = s.find('"', key_match.end())
        if start_quote == -1:
            return (False, '')
        
        # 查找结束双引号
        end_quote = s.find('"', start_quote + 1)
        if end_quote == -1:
            # 未闭合，提取到字符串末尾
            value = s[start_quote + 1:]
            return (False, value)
        else:
            # 闭合，提取中间的值
            value = s[start_quote + 1:end_quote]
            return (True, value)
    
    mood_completed, mood_value = process_key('mood', response)
    saying_ja_completed, saying_ja_value = process_key('saying_ja', response)
    saying_zh_completed, saying_zh_value = process_key('saying_zh', response)

    return [mood_completed, mood_value, saying_ja_completed, saying_ja_value, saying_zh_completed, saying_zh_value]
