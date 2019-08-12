import math
import time

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color
from kivy.graphics import Line
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget

__version__ = "2.0.0"

Builder.load_string("""
<DigitalClock>:
    _time: label_time
    typt_hour: toggle_button
    _time_zone: label_zone
    cols: 1
    spacing: 10
    AnalogClock:
        id: analog_clock_layout
        size_hint: (1, .7)              
    Label:
        id: label_time
        size_hint: (1, .2)
        # 设置文本居中对齐
        text_size: self.size
        halign: 'center'
        valign: 'middle'
        # 设置为markup text
        markup: True
    BoxLayout:
        size_hint: (1, .1)
        ToggleButton:
            id: toggle_button
            size_hint: (.2, 1)  # 大小设置为固定
            text: '12'
            state: 'normal'  # 默认抬起
        Label:
            id: label_zone
""")

Builder.load_string("""
<AnalogClock>:
    canvas:
        # 背景
        Color:
            rgb: (1, 1, 1)
        Rectangle:
            size: self.size
            pos: self.pos
        # 表盘
        Color:
            rgb: (0, 0, 0)
        Line:
            width: 6
            ellipse: (self.center_x - min(self.width, self.height) / 2, \
                      self.center_y - min(self.width, self.height) / 2, \
                      min(self.width, self.height), \
                      min(self.width, self.height))
        # 中心
        Ellipse:
            size: (6, 6)
            pos: (self.center_x - 3, self.center_y - 3)
""")


class AnalogClock(Widget):
    """模拟时钟控件"""

    def __init__(self, **kwargs):
        """绘制模拟时钟"""
        super(AnalogClock, self).__init__(**kwargs)
        self.radius = min(self.width, self.height) / 2  # 表盘半径
        # 刻度
        self.scales = []
        for sec in range(0, 360, 6):
            if sec % 15 == 0:  # 角度为15的倍数时，加粗加长
                w = 6
                l = self.radius * 8 / 10
            else:
                w = 3
                l = self.radius * 9 / 10
            self.scales.append(Line(points=[self.center_x + l * math.sin(sec / 180 * math.pi),
                                            self.center_y + l * math.cos(sec / 180 * math.pi),
                                            self.center_x + self.radius * math.sin(sec / 180 * math.pi),
                                            self.center_y + self.radius * math.cos(sec / 180 * math.pi)],
                                    width=w)
                               )
        # 添加刻度至控件
        for s in self.scales:
            self.canvas.add(s)
        # 表针
        with self.canvas:
            # 秒针
            self.second_hand = Line(
                points=[self.center_x, self.center_y, self.center_x, self.center_y + self.radius / 5],
                width=3)
            # 分针
            self.minute_hand = Line(
                points=[self.center_x, self.center_y, self.center_x, self.center_y + self.radius * 3 / 5],
                width=6)
            # 时针
            self.hour_hand = Line(
                points=[self.center_x, self.center_y, self.center_x, self.center_y + self.radius / 2],
                width=8)
        # 绑定pos size重绘图形
        self.bind(pos=self.redraw, size=self.redraw)
        Clock.schedule_interval(self.update_time, 0.5)  # 每0.5s调用一次update_time函数

    def redraw(self, w, args):
        """重绘控件"""
        # 圆形表盘
        self.radius = min(self.width, self.height) / 2  # 表盘半径
        # 清除原刻度
        for s in self.scales:
            self.canvas.remove(s)
        self.scales.clear()
        # 重绘刻度
        for sec in range(0, 360, 6):
            if sec % 15 == 0:
                w = 6
                l = self.radius * 8 / 10
            else:
                w = 3
                l = self.radius * 9 / 10
            self.scales.append(Line(points=[self.center_x + l * math.sin(sec / 180 * math.pi),
                                            self.center_y + l * math.cos(sec / 180 * math.pi),
                                            self.center_x + self.radius * math.sin(sec / 180 * math.pi),
                                            self.center_y + self.radius * math.cos(sec / 180 * math.pi)],
                                    width=w)
                               )
        # 添加重绘的刻度
        for s in self.scales:
            self.canvas.add(s)
        # 重绘表针
        self.update_time(0.5)

    def update_time(self, dt):
        """更新时间"""
        # 获取当前时间
        tm_sec = time.localtime().tm_sec
        tm_min = time.localtime().tm_min
        tm_hour = time.localtime().tm_hour
        # 移除原表针
        self.canvas.remove(self.second_hand)
        self.canvas.remove(self.minute_hand)
        self.canvas.remove(self.hour_hand)
        # 重绘表针
        with self.canvas:
            # 时针
            Color(0, 0, 1)
            self.hour_hand = Line(points=[self.center_x, self.center_y,
                                          self.center_x + (self.radius / 2) * math.sin(tm_hour * math.pi / 6),
                                          self.center_y + (self.radius / 2) * math.cos(tm_hour * math.pi / 6)],
                                  width=8)
            # 分针
            Color(0, 1, 0)
            self.minute_hand = Line(points=[self.center_x, self.center_y,
                                            self.center_x + (self.radius * 3 / 5) * math.sin(tm_min * math.pi / 30),
                                            self.center_y + (self.radius * 3 / 5) * math.cos(tm_min * math.pi / 30)],
                                    width=6)
            # 秒针
            Color(1, 0, 0)
            self.second_hand = Line(points=[self.center_x, self.center_y,
                                            self.center_x + (self.radius * 4 / 5) * math.sin(tm_sec * math.pi / 30),
                                            self.center_y + (self.radius * 4 / 5) * math.cos(tm_sec * math.pi / 30)],
                                    width=3)
            Color(0, 0, 0)


class DigitalClock(GridLayout):
    """数字时钟小程序"""
    _time = ObjectProperty(None)  # 时间显示label
    typt_hour = ObjectProperty(None)  # 时间显示格式 12/24
    _time_zone = ObjectProperty(None)  # 时区显示label

    def __init__(self, **kwargs):
        """初始化时间和绑定"""
        super(DigitalClock, self).__init__(**kwargs)  # 调用父构造函数
        self._time.text = time.strftime("%Y-%m-%d\n%H:%M:%S", time.localtime())  # 初始化时间显示
        self.typt_hour.bind(state=self.set_type_hour)  # 绑定时间显示格式
        self._time_zone.text = time.localtime().tm_zone
        Clock.schedule_interval(self.update_time, 0.5)  # 每0.5s调用一次update_time函数

    def update_time(self, dt):
        """更新时间"""
        s = time.localtime().tm_sec  # 秒
        m = time.localtime().tm_min  # 分
        h = time.localtime().tm_hour  # 时
        #  分钟秒对应到rgb
        r = int(s * 255 / 60)
        g = int(m * 255 / 60)
        b = int(h * 255 / 24)
        c = '{:0>2x}{:0>2x}{:0>2x}'.format(r, g, b)  # 合并rgb值
        # format_time = "[b][i][u]%Y-%m-%d[/u][/i]\n\n[color={}]%H:%M:%S[/color][/b]".format(c)  # markup时间字符串
        if self.typt_hour.state == 'normal':  # 12小时格式显示
            if h <= 12:
                format_time = "[b][i][u]%Y-%m-%d[/u][/i]\n\n[color={}]AM %I:%M:%S[/color][/b]".format(c)  # markup时间字符串
            else:
                format_time = "[b][i][u]%Y-%m-%d[/u][/i]\n\n[color={}]PM %I:%M:%S[/color][/b]".format(c)  # markup时间字符串
        else:  # 24 小时格式显示
            format_time = "[b][i][u]%Y-%m-%d[/u][/i]\n\n[color={}]%H:%M:%S[/color][/b]".format(c)  # markup时间字符串
        self._time.text = time.strftime(format_time, time.localtime())

    def set_type_hour(self, sender, state):
        """设置时间显示格式"""
        if state == 'normal':
            sender.text = '12'
        else:
            sender.text = '24'


class ClockApp(App):
    """一个时钟小程序"""

    def build(self):
        return DigitalClock()


if __name__ == '__main__':
    ClockApp().run()
