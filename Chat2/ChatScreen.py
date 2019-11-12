# 对话界面
import kivy
from kivy.base import Builder
from kivy.uix.screenmanager import Screen
from chuix import *

Builder.load_string("""
<ChatScreen>:  # 客户端
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: None
            height: sp(52)
            CHButton:  # 打开联系人节点列表
                size_hint_x: None
                width: self.height * 2
                text: 'Contact'
            CHButton:  # 对话地址
                text: 'Client'
            CHButton: # 打开服务端
                text: 'Server'
                size_hint_x: None
                width: self.height * 2
        BoxLayout:
            size_hint_y: None
            height: sp(36)
            CHLabel:
                text: 'To '
                text_size: self.size
                halign: 'center'
                size_hint_x: None
                width: sp(104)
            CHLabel:  # 对话地址
                id: t_address
                text_size: self.size
                halign: 'left'
                text: 'All Nodes'
        RecycleView:
            id: rv_messages
        Button:  # 占位
            size_hint_y: None
            height: sp(52)
    FloatLayout:  # 信息输入
        BoxLayout:
            id: input_layout
            size_hint:(1, None)
            pos_hint: {'x': 0, 'y': 0}
            orientation: 'horizontal'
            height: sp(52)
            CHTextInput:
                id: ti_message
                font_name: 'msyh.ttc'
                hint_text: '输入信息...'
                text_language: 'zh_CN'
                on_focus: input_layout.pos_hint = ({'x': 0, 'y': .5} if self.focus else {'x': 0, 'y': 0})
            CHButton:
                size_hint_x: None
                width: self.height
                text: '发送'
""")


class ChatScreen(Screen):
    pass
