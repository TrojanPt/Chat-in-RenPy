# Chat in RenPy 

> 基于 Ren'Py 引擎的 AI Chatbot 框架。

让你的自定义角色陪着你聊天吧，就像是在推 Galgame 一样！

**简体中文** | [**English**](./docs/en/README.md)


## 主要功能

- 💬 **对话交互**
  - 支持OpenAI API兼容的LLM服务（如DeepSeek等）
  - 支持中文输入与输出
  - 使用Ren'Py原生的存档系统进行历史对话管理

- 📢 **语音合成**
  - 支持OpenAI TTS API兼容的TTS服务
  - 按句切分进行语音合成，兼顾语义连贯与低滞后性

- 🎭 **对话中立绘控制系统**
  - 根据对话内容切换角色表情差分

- ⚙️ **高度可配置**
  - 通过JSON文件管理对话人物配置
  - 在OPTION界面设置LLM与TTS连接，并选择对话人物

## 快速开始
1. 下载发行版本
   
2. 编辑文件 `game\characters\characters.json` 以配置对话人物信息。JSON FORMAT架构说明请参照同目录下的[readme](./game/characters/readme.md)文件
   
3. 根据 `characters.json` 中填入的配置信息完善人物立绘与背景图片。注意图片相对路径应与 `characters.json` 中的对应参数一致
   
4. 为每一个人物创建用于指导大语言模型角色扮演的提示词文本文件，并保存至目录 `game\llm_prompt\roleplay_prompt` 下。注意文件名称应当与该角色的 `ID` 一致，并以 `.txt` 作为后缀
   
5. 运行 `ChatinRenPy.exe`
   
6. 点击 **START CHAT** 开始对话。程序会检查对话人物、LLM、TTS的配置状态，并在必要时提示你进行完善。你可以在 **OPTION** 界面更改这些配置

## 贡献指南

1. 开发环境

   - [Ren'Py](https://www.renpy.org/) SDK 8.3.6
   - [Python](https://www.python.org/) 3.10.11

    *其它版本亦可，但请检查它们的差别*

2. 克隆仓库至Ren'Py项目仓库：
   ```bash
   cd D:\Path\to\RenPy\Projects\Directory
   git clone https://github.com/TrojanPt/Chat-in-RenPy.git
   ```


## 特别提醒
  由于 **OWNER** 并非专业相关人士，代码中可能出现令人眼前一黑的操作，请在感到身体不适时迅速移除该项目 o(TヘTo) 
