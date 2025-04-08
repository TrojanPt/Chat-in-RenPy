# Chat in RenPy

> An AI Chatbot Framework Built with Ren'Py Engine.

Make your custom characters chat with you - just like playing a visual novel!

[**简体中文**](../../README.md) | **English**

## Key Features

- 💬 **Conversational Interaction**
  - Supports OpenAI API-compatible LLM services (e.g. DeepSeek)
  - Chinese input/output support
  - Native Ren'Py save system for conversation history management

- 📢 **Voice Synthesis**
  - Supports OpenAI API-compatible TTS services
  - Sentence-level synthesis balancing context coherence and low latency

- 🎭 **Character Fgimages Control System**
  - Automatic expression variations based on conversation content

- ⚙️ **High Customizability**
  - Manage character profiles via JSON configuration
  - Configure LLM/TTS connections and select characters in OPTION menu

## Quick Start
1. Download the latest release
  
2. Edit `game/characters/characters.json` to configure characters. Refer to the schema documentation in the same directory
  
3. Prepare characters' fgimages and background images according to the paths specified in `characters.json`
  
4. Create role-playing prompt files for each character in `game/llm_prompt/roleplay_prompt/`. Filename must match character ID with `.txt` extension
  
5. Run `ChatinRenPy.exe`
  
6. Click **START CHAT** to begin. The system will validate configurations and guide you through setup if needed. Modify settings in **OPTION** menu

## Contribution Guide

1. Development Environment

   - [Ren'Py](https://www.renpy.org/) SDK 8.3.6
   - [Python](https://www.python.org/) 3.10.11

   *Other versions may work but verify compatibility*

2. Clone to Ren'Py projects directory:
   ```bash
    cd D:\Path\to\RenPy\Projects\Directory
    git clone https://github.com/TrojanPt/Chat-in-RenPy.git
   ```

## Important Note
  As the **OWNER** is not a developer, you might encounter some eye-watering code. Please remove this project immediately if you experience any physical discomfort o(TヘTo)
