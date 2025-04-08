

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

    # 将 preference object 下与该次对话相关的 value 存入对话界面下的变量中，以保证存档时存入该次对话的参数配置
    # 请注意与LLM、TTS API接口相关的参数不作存档
    python:
        set_chat_character = preferences.chat_character
        set_chat_character_dict = preferences.chat_characters_dict[preferences.chat_character]
        set_tts_model = preferences.tts_model
        set_tts_voice = preferences.tts_voice

    # 人物定义
    $ ai = Character(set_chat_character_dict["name"])
    $ ai_nvl = Character(set_chat_character_dict["name"], kind=nvl)

    define user = Character("User")

    scene expression set_chat_character_dict['bg_scene']['path'] at show_bg_scene(set_chat_character_dict['bg_scene']['zoom'])
    
    $ renpy.run(Preference("auto-forward", "disable"))

    $ _history = True

    $ renpy.show(
        f'{set_chat_character} normal', 
        what=Image(set_chat_character_dict['fgimages']['normal']['path']), 
        at_list=[show_role(z=set_chat_character_dict['fgimages']['normal']['zoom'])]
    )

    ai "您已创建一个新的 Ren'Py 程序。"

    ai "当您完善了故事、图片和音乐之后，您就可以向全世界发布了！"
    
    #初始化 llm_messages, tts_params, tts_queue
    python:
        tts_queue = TTS_Queue()
        
        mood_list = list(set_chat_character_dict['fgimages'].keys())

        roleplay_prompt_file = open(str(config.basedir)+ f"\\game\\llm_prompt\\roleplay_prompt\\{set_chat_character_dict['id']}.txt")
        roleplay_prompt = roleplay_prompt_file.read()
        roleplay_prompt_file.close()
        roleplay_prompt_file = None
        
        json_format_prompt_file = open(str(config.basedir)+ f"\\game\\llm_prompt\\json_format_prompt.txt")
        json_format_prompt = json_format_prompt_file.read()
        json_format_prompt = json_format_prompt.replace('%(mood_list)', str(mood_list))
        json_format_prompt_file.close()
        json_format_prompt_file = None

        system_prompt = roleplay_prompt + json_format_prompt

        messages = [
            {
                "content": system_prompt,
                "role": "system"
            }
        ]
        
        params = {
            "model": set_tts_model,
            "input": "",
            "voice": set_tts_voice
        }
    jump chat

label chat:
    $ renpy.run(Preference("auto-forward", "enable"))
    
    $ renpy.run(Preference("auto-forward time", 1))
    
    # 与角色之间的一次对话是被放在一个python块中进行的，因此需要避免在一次对话进行的过程中进行存档。
    # 这是由于存档发生在外沿(outermost)互动上下文(context)中，Ren’Py语句的开头。
    # 因此，如果加载或回滚发生在某个语句中间，而且那个语句有多次互动，所有状态都会重置为语句开始的状态。
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
        cut = [[0, None, False]]    # cut：[{标记位置}，{call_response生成器}，{是否已被播放}]
        for response in call_llm(messages):
            # 控制立绘变化
            response_list = parse_response(response)
            if response_list[0] and response_list[1] != mood:
                mood = response_list[1]
                mood = mood.strip()
                if mood in mood_list:
                    renpy.show(
                        f'{set_chat_character} {mood}', 
                        what=Image(set_chat_character_dict['fgimages'][mood]['path']), 
                        at_list=[show_role(z=set_chat_character_dict['fgimages'][mood]['zoom'])]
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
        # RenPy无法pickle generator对象，因此需要在语音播放完成后重置cut
        cut = [[0, None, False]]

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