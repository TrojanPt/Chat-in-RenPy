
# 函数定义

init python:
    
    import json
    import hashlib
    from pathlib import Path
    import os

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

        response = renpy.fetch(url=url, method="POST", headers=headers, data=payload, function="call_stream_llm")
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

        response = renpy.fetch(url=url, method="POST", headers=headers, data=payload, function="call_tts")
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
            {mood是否生成完毕:bool}, 
            {mood的值,若mood未生成完毕则返回已经生成了的部分},
            {saying是否生成完毕:bool},
            {saying的值,若saying未生成完毕则返回已经生成了的部分}
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

label start:

    $ renpy.run(Preference("auto-forward", "enable"))
    $ renpy.run(Preference("auto-forward time", 1))

    show screen loading_pray

    # 检查
    nvl_narrator "正在进行初始化..."

    nvl_narrator "正在加载对话角色信息..."
    $ refresh_list("chat_character")

    if not preferences.chat_characters_dict:
        $ renpy.run(Preference("auto-forward", "disable"))
        nvl_narrator "获取对话角色信息失败！请检查game\characters\characters.json文件 (Click to continue)"
        return
    if not preferences.chat_character:
        $ renpy.run(Preference("auto-forward", "disable"))
        nvl_narrator "未选择对话角色 (Click to continue)"
        call screen parm_choice("chat_character", 'chat_characters_dict', "选择对话角色", True)
        while not preferences.chat_character:
            if _return == 'refresh':
                call screen parm_choice("chat_character", 'chat_characters_dict', "选择对话角色", True)
            elif _return == 'return':
                return
            elif _return == 'confirm' and not preferences.chat_character:
                return
    elif not preferences.chat_characters_dict.get(preferences.chat_character):
        $ renpy.run(Preference("auto-forward", "disable"))
        nvl_narrator "对话角色不存在，请重新选择对话角色或检查game\characters\characters.json文件 (Click to continue)"
        call screen parm_choice("chat_character", 'chat_characters_dict', "选择对话角色", True)
        while not preferences.chat_characters_dict.get(preferences.chat_character):
            if _return == 'refresh':
                call screen parm_choice("chat_character", 'chat_characters_dict', "选择对话角色", True)
            elif _return == 'return':
                return
            elif _return == 'confirm' and not preferences.chat_characters_dict.get(preferences.chat_character):
                return
    else:
        nvl_narrator " {b}=>{/b} 当前对话角色为 {b}[preferences.chat_characters_dict[preferences.chat_character]['name']]{/b}"
    $ renpy.run(Preference("auto-forward", "enable"))
    $ renpy.run(Preference("auto-forward time", 1))

    nvl_narrator "正在加载大语言模型设置..."
    if not preferences.llm_api_base_url:
        $ renpy.run(Preference("auto-forward", "disable"))
        nvl_narrator "未设置大语言模型api接口base_url (Click to continue)"
        call screen parm_edit("llm_api_base_url", "设置llm_api_base_url", True)
        if not preferences.llm_api_base_url:
            return
    $ renpy.run(Preference("auto-forward", "enable"))
    $ renpy.run(Preference("auto-forward time", 1))
    if not preferences.llm_api_key:
        $ renpy.run(Preference("auto-forward", "disable"))
        nvl_narrator "未设置大语言模型api接口密匙 (Click to continue)"
        call screen parm_edit("llm_api_key", "设置llm_api_key", True)
        if not preferences.llm_api_key:
            return
    $ renpy.run(Preference("auto-forward", "enable"))
    $ renpy.run(Preference("auto-forward time", 1))

    nvl_narrator "正在加载文本转语音模型设置..."
    if not preferences.tts_api_base_url:
        $ renpy.run(Preference("auto-forward", "disable"))
        nvl_narrator "未设置文本转语音模型api接口base_url (Click to continue)"
        call screen parm_edit("tts_api_base_url", "设置tts_api_base_url", True)
        if not preferences.tts_api_base_url:
            return
    $ renpy.run(Preference("auto-forward", "enable"))
    $ renpy.run(Preference("auto-forward time", 1))
    if not preferences.tts_api_key:
        $ renpy.run(Preference("auto-forward", "disable"))
        nvl_narrator "未设置文本转语音模型api接口密匙 (Click to continue)"
        call screen parm_edit("tts_api_key", "设置tts_api_key", True)
        if not preferences.tts_api_key:
            return
    $ renpy.run(Preference("auto-forward", "enable"))
    $ renpy.run(Preference("auto-forward time", 1))
    if not preferences.tts_model:
        $ renpy.run(Preference("auto-forward", "disable"))
        nvl_narrator "未选择文本转语音模型 (Click to continue)"
        call screen parm_choice("tts_model", 'tts_model_list', "选择tts_model", True)
        while not preferences.tts_model:
            if _return == 'refresh':
                call screen parm_choice("tts_model", 'tts_model_list', "选择tts_model", True)
            elif _return == 'return':
                return
            elif _return == 'confirm' and not preferences.tts_model:
                return
    else:
        nvl_narrator " {b}=>{/b} 当前文本转语音模型为 {b}[preferences.tts_model]{/b}"
    $ renpy.run(Preference("auto-forward", "enable"))
    $ renpy.run(Preference("auto-forward time", 1))
    if not preferences.tts_voice:
        $ renpy.run(Preference("auto-forward", "disable"))
        nvl_narrator "未选择文本转语音模型所用的语音 (Click to continue)"
        call screen parm_choice("tts_voice", 'tts_voice_list', "选择tts_voice", True)
        while not preferences.tts_voice:
            if _return == 'refresh':
                call screen parm_choice("tts_voice", 'tts_voice_list', "选择tts_voice", True)
            elif _return == 'return':
                return
            elif _return == 'confirm' and not preferences.tts_voice:
                return
    else:
        nvl_narrator " {b}=>{/b} 当前文本转语音模型所用的语音为 {b}[preferences.tts_voice]{/b}"
    $ renpy.run(Preference("auto-forward", "enable"))
    $ renpy.run(Preference("auto-forward time", 1))
    pause 0.5

    hide screen loading_pray

    # 人物定义
    $ ai = Character(preferences.chat_characters_dict[preferences.chat_character]["name"])
    $ ai_nvl = Character(preferences.chat_characters_dict[preferences.chat_character]["name"], kind=nvl)

    define user = Character("User")

    scene expression preferences.chat_characters_dict[preferences.chat_character]['bg_scene']['path'] at show_bg_scene(preferences.chat_characters_dict[preferences.chat_character]['bg_scene']['zoom'])
    
    $ renpy.run(Preference("auto-forward", "disable"))

    $ _history = True

    $ renpy.show(
        f'{preferences.chat_character} normal', 
        what=Image(preferences.chat_characters_dict[preferences.chat_character]['fgimages']['normal']['path']), 
        at_list=[show_role(z=preferences.chat_characters_dict[preferences.chat_character]['fgimages']['normal']['zoom'])]
    )

    ai "您已创建一个新的 Ren'Py 程序。"

    ai "当您完善了故事、图片和音乐之后，您就可以向全世界发布了！"
    
    #初始化 llm_messages, tts_params, tts_queue
    python:
        tts_queue = TTS_Queue()
        
        mood_list = list(preferences.chat_characters_dict[preferences.chat_character]['fgimages'].keys())

        roleplay_prompt_file = open(str(config.basedir)+ f"\\game\\llm_prompt\\roleplay_prompt\\{preferences.chat_characters_dict[preferences.chat_character]['id']}.txt")
        roleplay_prompt = roleplay_prompt_file.read()
        roleplay_prompt_file.close()
        
        json_format_prompt_file = open(str(config.basedir)+ f"\\game\\llm_prompt\\json_format_prompt.txt")
        json_format_prompt = json_format_prompt_file.read()
        json_format_prompt = json_format_prompt.replace('%(mood_list)', str(mood_list))
        json_format_prompt_file.close()

        system_prompt = roleplay_prompt + json_format_prompt

        messages = [
            {
                "content": system_prompt,
                "role": "system"
            }
        ]
        
        params = {
            "model": preferences.tts_model,
            "input": "",
            "voice": preferences.tts_voice
        }
    jump chat

label chat:
    $ renpy.run(Preference("auto-forward", "enable"))
    
    $ renpy.run(Preference("auto-forward time", 1))
    
    python:
        content = renpy.input(prompt="prompt:")
        user(content)
        messages.append(
            {
                "content": content, 
                "role": "user"
            }
        )

        _history = False

        full_response_ja = ""   # 存放已生成的回复部分（日语）
        full_response = ""   # 存放已生成的回复翻译部分
        mood = 'normal'
        cut = [[0, None, False]]    # cut：[{cut index}，{call_response generator}，{is played}]
        for response in call_llm(messages):
            # 控制立绘变化
            response_list = parse_response(response)
            if response_list[0] and response_list[1] != mood:
                mood = response_list[1]
                mood = mood.strip()
                if mood in mood_list:
                    renpy.show(
                        f'{preferences.chat_character} {mood}', 
                        what=Image(preferences.chat_characters_dict[preferences.chat_character]['fgimages'][mood]['path']), 
                        at_list=[show_role(z=preferences.chat_characters_dict[preferences.chat_character]['fgimages'][mood]['zoom'])]
                    )
            
            # 调用tts文本转语音
            if response_list[3]:
                full_response_ja = response_list[3]
                if full_response_ja:
                    next_cut = cut_response(full_response_ja, cut[-1][0])
                    if next_cut:
                        cut.append([next_cut, None, False])
                        params["input"] = full_response_ja[cut[-2][0] : cut[-1][0]]
                        cut[-1][1] = call_tts(params)
                    for i in range(1, len(cut)):
                        if not cut[i][2]:
                            r = next(cut[i][1])
                            if r != "speechfile_generating":
                                cut[i][2] = True
                                renpy.music.queue(f'audio/speech/{r}.mp3', channel="voice", clear_queue=False)
                                tts_queue.next()
            
            # 显示文本
            if response_list[5] == "":
                ai("......")

            else:
                full_response = response_list[5]
                ai(full_response)
        
        if not full_response_ja:
            renpy.block_rollback()
            renpy.run(Preference("auto-forward", "disable"))
            ai("LLM ERROR : 返回空内容")
            renpy.jump("whether_continue")

        if full_response_ja[-1] not in {'.', ';', '?', '!', '。', '？', '！', ';'} :
            full_response_ja += "。"

        # 对剩余未按句分割的回复进行分割
        while cut[-1][0] != len(full_response_ja):
            next_cut = cut_response(full_response_ja, cut[-1][0])
            cut.append([next_cut, None, False])
            params["input"] = full_response_ja[cut[-2][0] : cut[-1][0]]
            cut[-1][1] = call_tts(params)
            for i in range(1, len(cut)):
                if not cut[i][2]:
                    r = next(cut[i][1])
                    if r != "speechfile_generating":
                        cut[i][2] = True
                        renpy.music.queue(f'audio/speech/{r}.mp3', channel="voice", clear_queue=False)
                        tts_queue.next()

        # 对剩余未进行tts的回复进行tts请求
        for i in range(1, len(cut)):
            if not cut[i][2]:
                r = next(cut[i][1])
                while r == "speechfile_generating":
                    ai(full_response)
                    r = next(cut[i][1])
                renpy.music.queue(f'audio/speech/{r}.mp3', channel="voice", clear_queue=False)
                cut[i][2] = True
                tts_queue.next()

        messages.append(
            {
                "content": full_response, 
                "role": "assistant"
            }
        )
        renpy.block_rollback()
        renpy.run(Preference("auto-forward", "disable"))
        _history = True

        ai(full_response)

    jump whether_continue

label whether_continue:    
    menu:
        "继续":
            $ renpy.music.stop(channel='voice')
            jump chat
        "退出":
            pass
    ai "再见！"
    return