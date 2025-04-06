characters.json用于存储对话角色的信息。characters.json中内容应遵循如下架构

```json
{
  "type": "object",
  "description": "角色资源配置文件架构",
  "patternProperties": {
    "^[A-Za-z_]+$": {
      "type": "object",
      "properties": {
        "id": {
          "type": "string",
          "description": "角色标识符"
        },
        "name": {
          "type": "string",
          "description": "角色的显示名称"
        },
        "bg_scene": {
          "type": "object",
          "properties": {
            "path": {
              "type": "string",
              "description": "背景图片文件相对路径",
              "examples": [
                "images/background/bg1000a1.png"
              ]
            },
            "zoom": {
              "type": "number",
              "description": "背景缩放比例",
              "examples": [
                1.2
              ]
            }
          },
          "required": ["path", "zoom"]
        },
        "fgimages": {
          "type": "object",
          "description": "必须包含normal状态，其他表情状态可自由扩展",
          "properties": {
            "normal": {
              "type": "object",
              "properties": {
                "path": {
                  "type": "string",
                  "description": "立绘图片文件路径"
                },
                "zoom": {
                  "type": "number",
                  "description": "立绘图片缩放比例"
                }
              },
              "required": ["path", "zoom"]
            }
          },
          "required": ["normal"],
          "additionalProperties": {
            "type": "object",
            "properties": {
              "path": {
                "type": "string",
                "description": "立绘图片文件路径"
              },
              "zoom": {
                "type": "number",
                "description": "立绘图片缩放比例"
              }
            },
            "required": ["path", "zoom"],
          }
        }
      },
      "required": ["id", "name", "bg_scene", "fgimages"],
    }
  },
}
```
以下是一个characters.json的示例
```json
{
    "Natsume_Ai":{
        "id":"Natsume_Ai",
        "name":"夏目藍",
        "bg_scene":{
            "path": "images/background/bg1000a1.png",
            "zoom": 1.5
        },
        "fgimages":{
            "well":{
                "path":"images/fgimage/Natsume Ai/ai2001ca.png",
                "zoom":1.2
            },
            "laugh":{
                "path":"images/fgimage/Natsume Ai/ai2003ca.png",
                "zoom":1.2
            },
            "normal":{
                "path":"images/fgimage/Natsume Ai/ai2007ba.png",
                "zoom":1.2
            },
            "shocked":{
                "path":"images/fgimage/Natsume Ai/ai2013ca.png",
                "zoom":1.2
            },
            "a bit down":{
                "path":"images/fgimage/Natsume Ai/ai2009ba.png",
                "zoom":1.2
            },
            "snicker":{
                "path":"images/fgimage/Natsume Ai/ai2015ba.png",
                "zoom":1.2
            },
            "angry":{
                "path":"images/fgimage/Natsume Ai/ai2120ab.png",
                "zoom":1.2
            }
        }
    },
    "Otonashi_Ayana":{
        "id":"Otonashi_Ayana",
        "name":"音無彩名",
        "bg_scene":{
            "path": "images/background/bg1015d.png",
            "zoom": 1.5
        },
        "fgimages":{
            "well":{
                "path":"images/fgimage/Otonashi Ayana/ay2001ca.png",
                "zoom":1.2
            },
            "laugh":{
                "path":"images/fgimage/Otonashi Ayana/ay2003ca.png",
                "zoom":1.2
            },
            "normal":{
                "path":"images/fgimage/Otonashi Ayana/ay2007ba.png",
                "zoom":1.2
            }
        }
    }
}
```