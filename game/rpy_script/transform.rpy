
# transform.rpy
# 该文件用于预先定义游戏中需要用到的变换效果

# 具体操作可参阅 https://doc.renpy.cn/zh-CN/transforms.html#transform


transform show_role(x = 0.5, z = 1.2):
    xcenter x
    yanchor 1.0
    ypos 1.0
    zoom z

transform show_bg_scene(z = 1.0):
    zoom z