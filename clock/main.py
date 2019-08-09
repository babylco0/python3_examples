import kivy
from kivy.app import App
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
import time


Builder.load_string("""
<DigitalClock>:
    _time: label_time
    cols: 1
    Label:
        id: label_time
        # 设置文本居中对齐
        text_size: self.size
        halign: 'center'
        valign: 'middle'
""")


class DigitalClock(GridLayout):
    """数字时钟小程序"""
    _time = ObjectProperty(None)  # 时间显示label

    def __init__(self, **kwargs):
        """初始化时间和绑定"""
        super(DigitalClock, self).__init__(**kwargs)  # 调用父构造函数
        self._time.text = time.strftime("%Y-%m-%d\n%H:%M:%S", time.localtime())
        Clock.schedule_interval(self.update_time, 0.5)  # 每0.5s调用一次update_time函数

    def update_time(self, dt):
        """更新时间"""
        self._time.text = time.strftime("%Y-%m-%d\n%H:%M:%S", time.localtime())


class ClockApp(App):
    """一个时钟小程序"""
    def build(self):
        return DigitalClock()


if __name__ == '__main__':
    ClockApp().run()
