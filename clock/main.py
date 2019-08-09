import kivy
from kivy.app import App
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
import time

__version__ = "1.0.0"

Builder.load_string("""
<DigitalClock>:
    _time: label_time
    typt_hour: toggle_button
    _time_zone: label_zone
    cols: 1
    Label:
        id: label_time
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
