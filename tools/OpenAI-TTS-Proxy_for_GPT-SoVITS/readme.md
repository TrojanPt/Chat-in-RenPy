# OpenAI-TTS-Proxy for GPT-SoVITS


> 一个兼容OpenAI TTS API格式的中间层代理服务，可将请求参数转换为[GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)的API调用格式。

## 功能特性

- 动态管理GPT-SoVITS子进程
- 支持多语音模型热切换
- 实时音频流式响应
- 灵活的声音配置管理

## 快速开始

### 前置依赖

- Python 3.8+
- [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) 环境
- FastAPI及相关依赖

```bash
# 安装Python依赖
pip install fastapi uvicorn requests python-multipart
```

### 配置文件

1. 根据 `voice-config-schema.json` 提供的框架，配置 `voices.json` 文件

2. 修改代码中的GPT-SoVITS路径：
```python
# 修改此行路径为你的实际路径
cwd=r"D:\Your\GPT-SoVITS\Path" 
```

### 启动服务

- 运行 `OpenAI-TTS-Proxy_for_GPT-SoVITS.bat` 

## API 文档

### 获取可用语音列表

```bash
GET /v1/audio/voices
```

响应示例：
```json
{
  "voices": [
    {"id": "voice1", "name": "voice1"},
    {"id": "voice2", "name": "voice2"}
  ]
}
```

### 生成语音

```bash
POST /v1/audio/speech
```

请求示例：
```json
{
  "model": "GPT-SoVITS-v2",
  "voice": "voice1",
  "input": "需要合成的文本内容"
}
```

## 使用示例

### Python客户端

```python
import requests

response = requests.post(
    "http://localhost:5000/v1/audio/speech",
    json={
        "model": "GPT-SoVITS-v2",
        "voice": "voice1",
        "input": "欢迎使用智能语音合成系统"
    },
    stream=True
)

with open("output.wav", "wb") as f:
    for chunk in response.iter_content(chunk_size=1024):
        f.write(chunk)
```

### cURL

```bash
curl -X POST "http://localhost:5000/v1/audio/speech" \
-H "Content-Type: application/json" \
-d '{"model":"GPT-SoVITS-v2","voice":"voice1","input":"测试文本"}' \
--output output.wav
```

## 注意事项

1. **进程管理**：
   - 每个语音模型会启动独立的GPT-SoVITS进程
   - 切换语音时会自动终止当前进程并启动新进程
   - 服务关闭时会自动清理所有子进程

2. **性能建议**：
   - 推荐使用高性能GPU环境
   - 长文本建议分割为短段落处理
   - 并发请求需自行处理进程调度

3. **音频质量**：
   - 确保参考音频质量
   - 适当调整 `temperature` 等参数优化效果
