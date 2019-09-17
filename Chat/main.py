# 局域网聊天程序
import _thread
import json
import socket
import time
import urllib

import kivy
from kivy.app import App
from kivy.base import Builder
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer, HTTPServer
from http.client import HTTPConnection

from kivy.properties import StringProperty, ListProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition

__version__ = "1.0.0"


Builder.load_string("""
<NodeButton@Button>:
    on_press: 
        app.client.ids.t_address.text = self.text
        app.sm.transition.direction = 'left'
        app.sm.current = 'client'
<MessageLabel@Label>:
    text_size: self.size
    halign: 'left'
    valign: 'middle'
    
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
            Button:  # 进入客户端
                text: 'Client'
                size_hint_x: None
                width: self.height * 2
                on_press: root.manager.transition.direction = 'left'; root.manager.current = 'client'
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
                    text: '192.168.1.100'
                Label:
                    size_hint_x: None
                    width: self.height * 2
                    text: 'Range:'
                TextInput:  # 扫描范围
                    id: scan_range
                    text: '10'
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
                text: '192.168.1.101:8080'
            Button:
                text: 'Add'
                size_hint_x: None
                width: self.height * 2
                on_press: root.add_new_node()
        
        RecycleView:  # 节点列表
            viewclass: 'NodeButton'
            id: rv
            RecycleGridLayout:
                default_size: None, sp(52)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                cols: 1        

            
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
                on_press: root.manager.transition.direction = 'right'; root.manager.current = 'contact'
            Button:  # 对话地址
                id: t_address
                text: '0.0.0.0'
            Button: # 打开服务端
                text: 'Server'
                size_hint_x: None
                width: self.height * 2
                on_press: root.manager.transition.direction = 'left'; root.manager.current = 'server'
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
                hint_text: 'Input message...'
                on_focus: root.edit_message()
            Button:
                size_hint_x: None
                width: self.height
                text: 'Send'
                on_press: root.send_message()

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
                on_press: root.manager.transition.direction = 'right'; root.manager.current = 'client'
            Button:  # 本机地址信息
                text: '[ %s ]\\n[ %s ]' % (root.host_ip, root.host_port)
            ToggleButton:
                size_hint_x: None
                width: self.height * 2
                text: 'Log On' if self.state=='normal' else 'Log Off'
                state: 'down'
                id: log_switch
                on_state: root.show_logs()

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
            
""")

logs = []  # 日志信息列表
nodes = []  # 节点列表
messages = []  # 信息列表


def get_host_ip():
    """获取本地IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


class ServerRequestHandler(BaseHTTPRequestHandler):
    """服务器请求处理类"""

    def do_GET(self):
        """GET请求处理"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        if self.path == '/testing.html':
            rst_data = {'result': get_host_ip()}
            self.wfile.write(json.dumps(rst_data).encode())
        else:
            self.wfile.write('test'.encode())

    def log_request(self, code='-', size='-'):
        """接受请求成功记录"""
        logs.append('Get Request From [%s:%s] \n' % self.client_address
                    + time.strftime("%H:%M:%S %Y-%m-%d", time.localtime()))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = urllib.parse.parse_qs(self.rfile.read(content_length).decode('utf-8'))  # <--- Gets the data itself
        # print(post_data)
        logs.append('Get Message %s \n' % post_data['message']
                    + time.strftime("%H:%M:%S %Y-%m-%d", time.localtime()))
        messages.append('From [%s:%s] \n ' % self.client_address
                        + '%s \n ' % post_data['message']
                        + time.strftime("%H:%M:%S %Y-%m-%d", time.localtime()))
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        rst_data = {'result': 'OK'}
        self.wfile.write(json.dumps(rst_data).encode())


class ChatContact(Screen):
    """联系人节点"""
    start_ip = '192.168.1.100'
    scan_range = 10

    def add_new_node(self):
        """手动添加一个节点"""
        host_url = self.ids.new_host.text
        try:
            conn = HTTPConnection(host_url, timeout=.5)
            conn.request('GET', "/testing.html")
            r1 = conn.getresponse()
            data = json.loads(r1.read())
            new_node = {'address': host_url, 'info': data['result']}
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
        g = [0] * 4
        for x in range(4):
            g[x] = int(gateway_ipv4[x])
        subnet = g.copy()
        for x in range(0, self.scan_range):
            subnet[3] = g[3] + x
            host_url = '%s.%s.%s.%s:8080' % tuple(subnet)
            # print(host_url)
            try:
                conn = HTTPConnection(host_url, timeout=.5)
                conn.request('GET', "/testing.html")
                r1 = conn.getresponse()
                data = json.loads(r1.read())
                new_node = {'address': host_url, 'info': data['result']}
                nodes.append(new_node)
                self.update_nodes()
            except Exception as e:
                pass
                # print(str(e))

    def update_nodes(self):
        """更新节点列表显示"""
        self.ids.rv.data = [{'text': n['info']} for n in list(nodes)]


class ChatClient(Screen):
    """聊天客户端"""

    def __init__(self, **kwargs):
        super(ChatClient, self).__init__(**kwargs)
        _thread.start_new_thread(self.thread_listen_messages, ())

    def send_message(self):
        """发送信息"""
        url = '%s:8080' % self.ids.t_address.text
        # print(url)
        message = self.ids.ti_message.text
        if len(message) == 0:
            return
        try:
            conn = HTTPConnection(url)
            params = urllib.parse.urlencode({'message': message})
            headers = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain'}
            conn.request('POST', "/", params, headers)
            r1 = conn.getresponse()
            data = json.loads(r1.read())
            # print(data)
            if data['result'] == 'OK':
                messages.append('To [%s] \n ' % url
                                + '%s \n ' % message
                                + time.strftime("%H:%M:%S %Y-%m-%d", time.localtime()))
        except Exception as e:
            print(str(e))

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
        self.host_ip = get_host_ip()
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
        except Exception as e:
            logs.append("Starting server error %s" % str(e)
                        + time.strftime("%H:%M:%S %Y-%m-%d", time.localtime()))

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
        self.sm = ScreenManager(transition=SlideTransition(duration=.35))
        self.contact = ChatContact(name='contact')
        self.client = ChatClient(name='client')
        self.server = ChatServer(name='server')
        self.sm.add_widget(self.client)
        self.sm.add_widget(self.server)
        self.sm.add_widget(self.contact)
        # sm.current = 'client'
        self.server.start_server()  # 自动打开服务器监听
        return self.sm


if __name__ == '__main__':
    ChatApp().run()
