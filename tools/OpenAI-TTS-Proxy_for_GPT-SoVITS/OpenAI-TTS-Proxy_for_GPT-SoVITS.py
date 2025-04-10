import sys
import json
import threading
import subprocess
import time

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import requests
from pydantic import BaseModel

from fastapi.responses import StreamingResponse

import time


app = FastAPI()

def start_api(stdin: str) -> subprocess.Popen:
    """启动GPT-SoVITS API子进程
    
    Args:
        command (str): 要执行的命令
        
    Returns:
        subprocess.Popen: 启动的子进程对象
        
    Raises:
        RuntimeError: 当子进程启动超时时
    """
    proc = subprocess.Popen(
        stdin,
        cwd=r"D:\GPT-SoVITS\GPT-SoVITS-v3-20250212\GPT-SoVITS-v3-20250212",  # 指定GPT-SoVITS目录
        stdout=subprocess.PIPE,    # 捕获标准输出
        stderr=subprocess.STDOUT,  # 合并错误流到标准输出
        bufsize=1,                 # 行缓冲
        text=True,
        shell=True
    )
    # 创建事件标志用于同步
    startup_event = threading.Event()
    
    # API启动完成后持续打印输出到终端
    def print_output():
        for line in iter(proc.stdout.readline, ''):
            print(line.strip())  # 实时打印

    # 定义检测API启动完成条件函数
    def monitor_output():
        for line in iter(proc.stdout.readline, ''):
            print(line.strip())
            if "Application startup complete." in line:
                print("GPT-SoVITS API服务启动完成,继续主程序...")
                startup_event.set()
                break

    # 启动监控线程
    print_thread = threading.Thread(target=print_output)
    monitor_thread = threading.Thread(target=monitor_output)

    monitor_thread.start()
    while monitor_thread.is_alive():
        time.sleep(0.1)

    print_thread.start()

    # 主线程等待事件触发或超时（30秒）
    startup_event.wait(timeout=30)
    if not startup_event.is_set():
        print("等待超时，可能服务启动失败！")
        proc.terminate()
        sys.exit(1)
    
    return proc

def terminate_process(proc: subprocess.Popen) -> None:
    """安全终止子进程
    
    Args:
        proc (subprocess.Popen): 要终止的进程对象
    """
    if proc.poll() is None:  # 检查进程是否在运行
        try:
            # 尝试通过API发送退出命令
            requests.get("http://127.0.0.1:9880/control?command=exit", timeout=5)
            print("已发送API退出指令")
            time.sleep(1)  # 等待服务清理资源
        except Exception as e:
            time.sleep(1)
            print(str(e))
            if proc.poll() is None:
                # 强制终止
                print(f"API退出失败, 启用强制终止")
                subprocess.run(f"taskkill /F /T /PID {proc.pid}", shell=True)
                print("GPT-SoVITS API进程已强制终止")
            else:
                print("GPT-SoVITS API进程已退出")
                return
    else:
        print("GPT-SoVITS API进程已自行退出")

# 加载tts voices配置
with open("voices.json", encoding="utf-8") as f:
    voice_configs = json.load(f)

voices = []
voices_cr = {}
for voice_id in [*voice_configs]:
    voices_cr[voice_id] = [False,None]
    voices.append({
        "id": voice_id,
        "name": voice_id
        }
    )

class OpenAITTSRequest(BaseModel):
    model: str
    voice: str
    input: str

# 返回tts voices列表
@app.get("/v1/audio/voices")
async def get_voices():
    return JSONResponse(content={"voices": voices})

# 返回tts models列表
@app.get("/v1/audio/models")
async def get_models() -> dict:
    """返回支持的模型列表"""
    return JSONResponse(content={
        "models": [
            {
                "id": "GPT-SoVITS-v2",
                "object": "model",
                "owned_by": "GPT-SoVITS",
                "permissions": []
            }
        ],
        "object": "list"
    })

@app.post("/v1/audio/speech")
async def tts_proxy(request: OpenAITTSRequest):
    # 获取语音配置
    voice_cfg = voice_configs.get(request.voice)
    if not voice_cfg:
        raise HTTPException(status_code=400, detail="Invalid voice")
    # 启动GPT-SoVITS进程
    if not voices_cr[request.voice][0]:
        for i in voices_cr:
            if voices_cr[i][0]:
                print(f''' = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
||   正在结束GPT-SoVITS API子进程[PID: {voices_cr[i][1].pid}]: voice={i}
  = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =''')
                terminate_process(voices_cr[i][1])
                voices_cr[i][0] = False
        
        shell_stdin = r"runtime\python.exe api_v2.py -a 127.0.0.1 -p 9880 -c "+voice_cfg["tts_infer"]
        voices_cr[request.voice][1] = start_api(shell_stdin)
        print(f''' = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
||   已创建GPT-SoVITS API子进程[PID: {voices_cr[request.voice][1].pid}]: model={request.model},voice={request.voice}
  = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =''')
        voices_cr[request.voice][0] = True
    else:
        print(f''' = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
||   GPT-SoVITS API已在运行: model={request.model},voice={request.voice}
  = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =''')

    # 构造GPT-SoVITS请求参数
    payload = {
        "text": request.input,
        "text_lang": "auto",
        "ref_audio_path": voice_cfg["ref_audio_path"],
        "prompt_lang": voice_cfg["prompt_lang"],
        "prompt_text": voice_cfg["prompt_text"],
        "aux_ref_audio_paths": voice_cfg["aux_ref_audio_paths"],    # list.(optional) auxiliary reference audio paths for multi-speaker tone fusion
        "text_split_method": "cut5",
        "fragment_interval":0.5,      # float. to control the interval of the audio fragment.
        "speed_factor": 1.0,
        "temperature": 1.0,
        "top_k": 5,
        "top_p": 1.0,
        "batch_size": 2,              # int. batch size for inference
        "batch_threshold": 0.75,      # float. threshold for batch splitting.
        "split_bucket": True,         # bool. whether to split the batch into multiple buckets.
        "streaming_mode": True,       # bool. whether to return a streaming response.
        "seed": -1,                   # int. random seed for reproducibility.
        "parallel_infer": True,       # bool. whether to use parallel inference.
        "repetition_penalty": 1.35    # float. repetition penalty for T2S model.
    }

    # 调用GPT-SoVITS API
    try:
        response = requests.post(
            "http://localhost:9880/tts",
            json = payload
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 返回音频流
    return StreamingResponse(
        response.iter_content(chunk_size=1024),
        media_type="audio/wav"
    )