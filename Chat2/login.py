import kivy
from kivy.base import Builder
from kivy.uix.screenmanager import Screen
from chuix import *


Builder.load_string("""
<LoginScreen>:
    canvas:
        Color:
            rgba: .1, .5, .8, 1
        Rectangle:
            size: self.size
            pos: self.pos
    FloatLayout:
        GridLayout:  # 登陆系统
            size_hint: (.8, .6)
            pos_hint: {'x': .1, 'y': .4}
            cols: 1
            spacing: ti_user.minimum_height
            CHLabel:
            BoxLayout:
                size_hint_y: None
                height: ti_user.minimum_height
                CHLabel:
                    size_hint: .2, 1
                CHLabel:
                    text: '用户认证'                
            BoxLayout:
                size_hint_y: None
                height: self.minimum_height
                CHLabel:                    
                    text: '用户名'
                    size_hint: .2, 1
                CHTextInput:
                    id: ti_user
                    size_hint_y: None
                    text: ''
                    multiline: False
                    height: self.minimum_height
            BoxLayout:
                size_hint_y: None
                height: self.minimum_height
                CHLabel:
                    text: '密码'
                    size_hint: .2, 1
                CHTextInput:
                    size_hint_y: None
                    text: ''
                    password: True
                    multiline: False
                    height: self.minimum_height
            BoxLayout:
                size_hint_y: None
                height: ti_user.minimum_height
                CHLabel:
                    size_hint: .2, 1
                CHButton:
                    text: '登入系统'
                    on_press: l_tips.text = '登陆中'; l_login_bar.value += 5
            CHLabel:
        GridLayout:  # 登陆提示
            size_hint: (.8, .2)
            pos_hint: {'x': .1, 'y': .1}
            cols: 1
            CHLabel:
                id: l_tips
                text: '登陆成功'
            ProgressBar:
                id: l_login_bar
                max: 100
""")


class LoginScreen(Screen):
    """用户登录界面"""
    pass