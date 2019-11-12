# 局域网聊天程序
import _thread
import json
import socket
import time
import urllib
from os.path import join, exists

import kivy
from kivy.app import App
from kivy.base import Builder
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer, HTTPServer
from http.client import HTTPConnection

from kivy.properties import StringProperty, NumericProperty, DictProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from kivy.uix.pagelayout import PageLayout
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from Crypto.PublicKey import RSA

__version__ = "1.0.0"


Builder.load_string("""
<NodeButton@Button>:  # 节点按钮 点击选择对话目标
    font_name: 'msyh.ttc'
    on_press: 
        app.client.ids.t_address.text = self.text
        app.sm.transition.direction = 'left'
        app.sm.current = 'client'
<MessageLabel@Label>:  # 信息标签
    text_size: self.size
    halign: 'left'
    valign: 'middle'
    font_name: 'msyh.ttc'
    
<ChatContact>:  # 联系人列表
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: None
            height: sp(52)
            Button:
                text: ' '
                size_hint_x: None
                width: self.height * 2
            Button:
                text: 'Contact List'
                on_press: app.open_help()
            Button:  # 进入客户端
                text: 'Client'
                size_hint_x: None
                width: self.height * 2
                on_press: app.to_client('left')
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: sp(104)
            GridLayout:
                cols: 2            
                Label:
                    size_hint_x: None
                    width: self.height * 2
                    text: 'Start IP:'
                TextInput:  # 起始地址
                    id: start_ip
                    text: root.start_ip
                Label:
                    size_hint_x: None
                    width: self.height * 2
                    text: 'Range:'
                TextInput:  # 扫描范围
                    id: scan_range
                    text: str(root.scan_range)
            Button: # 扫描局域网
                text: 'Scan'
                size_hint_x: None
                width: self.height
                on_press: root.scan_local()
        BoxLayout:  # 手动添加一个地址
            orientation: 'horizontal'
            size_hint_y: None
            height: sp(52)
            Label:
                text: 'IP:'
                size_hint_x: None
                width: self.height * 2
            TextInput:  # 地址
                id: new_host
                text: root.new_host
            Button:
                text: 'Add'
                size_hint_x: None
                width: self.height * 2
                on_press: root.add_new_node()
        NodeButton:  # 所有节点（群聊）
            text: 'All Nodes'
            size_hint_y: None
            height: sp(52)
        RecycleView:  # 节点列表
            viewclass: 'NodeButton'
            id: rv
            RecycleGridLayout:
                default_size: None, sp(52)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                cols: 1    
        ProgressBar:
            id: progress_scan
            size_hint_y: None
            height: sp(10)    
            max: root.scan_range
            
<ChatClient>:  # 客户端
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: None
            height: sp(52)
            Button:  # 打开联系人节点列表
                size_hint_x: None
                width: self.height * 2
                text: 'Contact'
                on_press: app.to_contact('right')
            Button:  # 对话地址
                text: 'Client'
                on_press: app.open_help()
            Button: # 打开服务端
                text: 'Server'
                size_hint_x: None
                width: self.height * 2
                on_press: app.to_server('left') 
        BoxLayout:
            size_hint_y: None
            height: sp(36)
            Label:
                text: 'To '
                text_size: self.size
                halign: 'center'
                size_hint_x: None
                width: sp(104)
            Label:  # 对话地址
                id: t_address
                text_size: self.size
                halign: 'left'
                text: 'All Nodes'
                font_name: 'msyh.ttc'
        RecycleView:
            id: rv_messages
            viewclass: 'MessageLabel'
            RecycleGridLayout:
                default_size: None, sp(104)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                cols: 1
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
            TextInput:
                id: ti_message
                font_name: 'msyh.ttc'
                hint_text: 'Input message...'
                text_language: 'zh_CN'
                on_focus: root.edit_message()
            Button:
                size_hint_x: None
                width: self.height
                text: 'Send'
                on_press: app.send_message()

<ChatServer>:  # 服务端
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: None
            height: sp(52)
            Button:  # 返回客户端
                text: 'Client'
                size_hint_x: None
                width: self.height * 2
                on_press: app.to_client('right')
            Button:  # 本机地址信息
                text: 'Server'
                on_press: app.open_help()
            ToggleButton:
                size_hint_x: None
                width: self.height * 2
                text: 'Log On' if self.state=='normal' else 'Log Off'
                state: 'down'
                id: log_switch
                on_state: root.show_logs()
        Label:  # 本机地址信息
            size_hint_y: None
            height: sp(36)
            text: 'Local host: [ %s : %s ]' % (root.host_ip, root.host_port)
        BoxLayout:  # 日志信息
            orientation: 'vertical'
            RecycleView:
                id: rv
                viewclass: 'Label'
                RecycleGridLayout:
                    default_size: None, sp(52)
                    default_size_hint: 1, None
                    size_hint_y: None
                    height: self.minimum_height
                    cols: 1
                
        BoxLayout:  # 手动启动服务器
            size_hint_y: None
            height: sp(52)
            Button:
                text: 'Start'
                on_press: root.start_server()
            # Button:
            #    text: 'Stop'        
            #    on_press: root.stop_server()
            
<UserSetting>:  # 用户设置
    FloatLayout:
        orientation: 'vertical'
        Label:
            id: label_welcome
            font_name: 'msyh.ttc'
            size_hint: (.8, None)
            height: sp(54)
            pos_hint: {'x': .1, 'y': .6}
            text: 'Input a Nickname: ' if root.is_new else 'Welcome < %s >' % root.data['name']
        TextInput:
            id: ti_nickname
            font_name: 'msyh.ttc'
            height: sp(54)
            size_hint: (.8, None)
            pos_hint: {'x': .1, 'y': .5}
            multiline: False
            disabled: False if root.is_new else True 
            hint_text: 'Input a Nickname' if root.is_new else 'Click <Reset> to Setting a New Nickname'      
        Button:
            text: 'Reset'  
            height: sp(54)
            size_hint: (.8, None)
            pos_hint: {'x': .1, 'y': .4}
            disabled: True if root.is_new else False  
            on_press: root.is_new = True; root.data.clear() 
        Button:
            text: 'Start'
            size_hint_y: None
            height: sp(54)
            pos_hint: {'x': 0, 'y': 0}
            on_press: app.save_user_setting()
""")

logs = []  # 日志信息列表
nodes = []  # 节点列表
messages = []  # 信息列表
user_info = {'name': '','pubkey': ''}


def get_host_ip():
    """获取本地IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(.1)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


local_ip = get_host_ip()


class ServerRequestHandler(BaseHTTPRequestHandler):
    """服务器请求处理类"""

    def do_GET(self):
        """GET请求处理"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        if self.path == '/info.html':
            self.wfile.write(json.dumps(user_info).encode())
        else:
            rst_data = {'result': local_ip}
            self.wfile.write(json.dumps(rst_data).encode())

    def log_request(self, code='-', size='-'):
        """接受请求成功记录"""
        logs.append('Get Request From [%s:%s] \n' % self.client_address
                    + time.strftime("%H:%M:%S %Y-%m-%d", time.localtime()))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = urllib.parse.parse_qs(self.rfile.read(content_length).decode('utf-8'))  # <--- Gets the data itself
        # print(post_data)
        # logs.append('Get Message %s \n' % post_data['data']
        #            + time.strftime("%H:%M:%S %Y-%m-%d", time.localtime()))
        # 获取节点昵称
        name = '%s:%s' % self.client_address
        for node in nodes:
            address = node['address'].split(':')[0]
            if self.client_address[0] == address:
                name = node['name']
                break
        messages.append('From [%s] \n ' % name
                        + '%s \n ' % post_data['data']
                        + time.strftime("%H:%M:%S %Y-%m-%d", time.localtime()))
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        rst_data = {'result': 'OK'}
        self.wfile.write(json.dumps(rst_data).encode())


class UserSetting(Screen):
    """用户配置类"""
    data = DictProperty()
    is_new = BooleanProperty(True)


class ChatContact(Screen):
    """联系人节点"""
    start_ip = StringProperty('0.0.0.0')
    new_host = StringProperty('0.0.0.0')
    scan_range = NumericProperty(10)

    def __init__(self, **kwargs):
        super(ChatContact, self).__init__(**kwargs)
        host_ips = local_ip.split('.')
        self.new_host = '%s.%s.%s.%s:8080' % tuple(host_ips)
        host_ips[3] = '100'
        self.start_ip = '%s.%s.%s.%s' % tuple(host_ips)

    def add_new_node(self):
        """手动添加一个节点"""
        self.new_host = self.ids.new_host.text
        try:
            conn = HTTPConnection(self.new_host, timeout=.5)
            conn.request('GET', "/info.html")
            r1 = conn.getresponse()
            data = json.loads(r1.read())
            new_node = {'address': self.new_host, 'name': data['name'], 'pubkey': data['pubkey']}
            if new_node not in nodes:
                nodes.append(new_node)
            self.update_nodes()
        except Exception as e:
            pass

    def scan_local(self):
        """扫描本地网络"""
        self.start_ip = self.ids.start_ip.text
        self.scan_range = int(self.ids.scan_range.text)
        _thread.start_new_thread(self.thread_sacn_local, ())

    def thread_sacn_local(self):
        nodes.clear()
        gateway_ipv4 = self.start_ip.split('.')
        g = [int(gateway_ipv4[x]) for x in range(4)]
        subnet = g.copy()
        for x in range(0, self.scan_range):
            subnet[3] = g[3] + x
            host_url = '%s.%s.%s.%s:8080' % tuple(subnet)
            # 跳过自己IP地址
            if subnet[3] != int(local_ip.split('.')[3]):
                try:
                    conn = HTTPConnection(host_url, timeout=.1)
                    conn.request('GET', "/info.html")
                    r1 = conn.getresponse()
                    data = json.loads(r1.read())
                    new_node = {'address': host_url, 'name': data['name'], 'pubkey': data['pubkey']}
                    nodes.append(new_node)
                    self.update_nodes()
                except Exception as e:
                    pass
            self.ids.progress_scan.value = x + 1

    def update_nodes(self):
        """更新节点列表显示"""
        self.ids.rv.data = [{'text': n['name'] + ' @ ' + n['address']} for n in list(nodes)]


class ChatClient(Screen):
    """聊天客户端"""

    def __init__(self, **kwargs):
        super(ChatClient, self).__init__(**kwargs)
        _thread.start_new_thread(self.thread_listen_messages, ())


    def edit_message(self):
        """编辑对话框"""
        if self.ids.ti_message.focus:  # 被焦点时 输入框置于屏幕中央
            self.ids.input_layout.pos_hint = {'x': 0, 'y': .5}
        else:
            self.ids.input_layout.pos_hint = {'x': 0, 'y': 0}

    def thread_listen_messages(self):
        """监听信息线程"""
        while True:
            self.ids.rv_messages.data = [{'text': x, 'halign': 'left' if x[0] == 'F' else 'right'} for x in messages]
            time.sleep(.5)


class ChatServer(Screen):
    """聊天服务端"""
    host_ip = StringProperty('0.0.0.0')
    host_port = StringProperty('8080')

    def __init__(self, **kwargs):
        super(ChatServer, self).__init__(**kwargs)
        self.host_ip = local_ip
        self.host = (self.host_ip, int(self.host_port))
        self.server = HTTPServer(self.host, ServerRequestHandler)
        _thread.start_new_thread(self.logs_handler, ())

    def start_server(self):
        """启动服务监听"""
        try:
            # host = (self.host_ip, int(self.host_port))
            # self.server = HTTPServer(host, ServerRequestHandler)
            logs.append("Starting server, listen at: [ %s:%s ] \n" % self.host
                        + time.strftime("%H:%M:%S %Y-%m-%d", time.localtime()))
            _thread.start_new_thread(self.thread_start_server, ())
            return True
        except Exception as e:
            logs.append("Starting server error %s" % str(e)
                        + time.strftime("%H:%M:%S %Y-%m-%d", time.localtime()))
            return False

    def thread_start_server(self):
        self.server.serve_forever()

    def stop_server(self):
        """关闭服务监听"""
        self.server.shutdown()
        # print(self.server.server_port)
        logs.append("Stop server [ %s:%s ] \n" % (self.server.server_address, self.server.server_port)
                    + time.strftime("%H:%M:%S %Y-%m-%d", time.localtime()))

    def show_logs(self):
        """显示日志"""
        if self.ids.log_switch.state == 'down':
            _thread.start_new_thread(self.logs_handler, ())

    def logs_handler(self):
        """日志处理函数"""
        while self.ids.log_switch.state == 'down':
            self.ids.rv.data = [{'text': x} for x in logs]
            time.sleep(.5)


class ChatApp(App):
    """聊天小程序"""
    def build(self):
        self.sm = ScreenManager(transition=SlideTransition())
        self.contact = ChatContact(name='contact')
        self.client = ChatClient(name='client')
        self.server = ChatServer(name='server')
        self.user_setting = UserSetting(name='user')
        self.load_user_setting()
        self.sm.add_widget(self.user_setting)
        # self.sm.add_widget(self.client)
        # self.sm.add_widget(self.server)
        # self.sm.add_widget(self.contact)
        # sm.current = 'client'
        # self.server.start_server()  # 自动打开服务器监听
        return self.sm

    def to_server(self, direction):
        """显示服务端"""
        if not self.sm.has_screen('server'):
            self.sm.add_widget(self.server)
        self.sm.transition.direction = direction
        self.sm.current = 'server'

    def to_client(self, direction):
        """显示客户端"""
        if not self.sm.has_screen('client'):
            self.sm.add_widget(self.client)
        self.sm.transition.direction = direction
        self.sm.current = 'client'

    def to_contact(self, direction):
        """显示客户端"""
        if not self.sm.has_screen('contact'):
            self.sm.add_widget(self.contact)
        self.sm.transition.direction = direction
        self.sm.current = 'contact'

    def load_user_setting(self):
        """加载用户配置"""
        if not exists(self.user_fn):
            self.user_setting.data = []
            self.user_setting.is_new = True
            return
        with open(self.user_fn) as fd:
            data = json.load(fd)
        self.user_setting.data = data
        self.user_setting.is_new = False

    def save_user_setting(self):
        """保存用户配置"""
        is_new = self.user_setting.is_new
        if self.user_setting.is_new:  # 新建用户
            # 获取用户昵称
            if len(self.user_setting.ids.ti_nickname.text) == 0:
                self.user_setting.ids.ti_nickname.focus = True
                return
            else:
                self.user_setting.data['name'] = self.user_setting.ids.ti_nickname.text
            self.user_setting.ids.ti_nickname.text = ''
            self.user_setting.is_new = False

        # self.to_client('left')
        _thread.start_new_thread(self.thread_open_client, (is_new, ))

    def thread_open_client(self, is_new):
        """打开程序线程"""
        popup = Popup(title='Create Keys ...',
                      content=ProgressBar(max=100),
                      size_hint=(.8, .2))
        popup.open()
        if is_new:
            # 生成密钥
            key = RSA.generate(1024)
            rsa_prikey = key.exportKey('PEM').decode('utf-8')
            rsa_pubkey = key.publickey().exportKey('PEM').decode('utf-8')
            self.user_setting.data['prikey'] = rsa_prikey
            self.user_setting.data['pubkey'] = rsa_pubkey
            time.sleep(.1)
            popup.title = 'Save setting ...'
            popup.content.value = 20
            with open(self.user_fn, 'w') as fd:
                json.dump(self.user_setting.data, fd)
            time.sleep(.1)
        popup.title = 'Using setting ...'
        popup.content.value = 40
        user_info['name'] = self.user_setting.data['name']
        user_info['pubkey'] = self.user_setting.data['pubkey']
        time.sleep(.1)
        popup.title = 'Start server ...'
        popup.content.value = 60
        if self.server.start_server():
            time.sleep(.1)
            popup.title = 'Start succeed ...'
            popup.content.value = 80
            time.sleep(.1)
            popup.title = 'Open client ...'
            popup.content.value = 100
            self.to_client('left')
            popup.dismiss()
        else:
            time.sleep(.1)
            popup.title = 'Start failed ...'
            popup.content.value = 80
            time.sleep(.1)
            popup.title = 'Open server ...'
            popup.content.value = 100
            self.to_server('left')
            popup.dismiss()


    def send_message(self):
        """发送信息"""
        message = self.client.ids.ti_message.text
        if len(message) == 0:  # 输入为空 返回
            return
        if self.client.ids.t_address.text != 'All Nodes':
            t_name, url = self.client.ids.t_address.text.split(' @ ')  # 获取用户名和链接
            if self.post_request(url, message):
                messages.append('To [%s] \n ' % t_name
                                + '[ %s ]\n ' % message
                                + time.strftime("%H:%M:%S %Y-%m-%d", time.localtime()))
                self.client.ids.ti_message.text = ''
            else:
                messages.append('To [%s] \n ' % t_name
                                + 'Failed!!! ')
        else:  # 发送给所有节点
            for node in nodes:
                t_name = node['name']
                url = node['address']
                if self.post_request(url, message):
                    messages.append('To [%s] \n ' % t_name
                                    + '[ %s ]\n ' % message
                                    + time.strftime("%H:%M:%S %Y-%m-%d", time.localtime()))
                    self.client.ids.ti_message.text = ''
                else:
                    messages.append('To [%s] \n ' % t_name
                                    + 'Failed!!! ')

    def post_request(self, url, data):
        """发送POST请求"""
        try:
            conn = HTTPConnection(url)
            params = urllib.parse.urlencode({'data': data})
            headers = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain'}
            conn.request('POST', "/", params, headers)
            r1 = conn.getresponse()
            data = json.loads(r1.read())
            # print(data)
            if data['result'] == 'OK':
                return True
        except Exception as e:
            logs.append("Error: %s\n" % str(e)
                        + time.strftime("%H:%M:%S %Y-%m-%d", time.localtime()))
            return False

    def open_help(self):
        """打开帮助弹窗"""
        pass

    def encrypt_message(self, message):
        """加密信息"""
        pass

    @property
    def user_fn(self):
        return join('./', 'user.json')


if __name__ == '__main__':
    ChatApp().run()
