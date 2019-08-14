# 倒计时/计时器程序
import _thread
import time

from kivy.app import App
from kivy.graphics import Color
from kivy.graphics import Rectangle, Ellipse
from kivy.graphics.instructions import InstructionGroup
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

__version__ = "1.0.0"


Builder.load_string("""       
<EllipticButton>:
    # 背景
    canvas.before: 
        Color:
            rgb:(1, 0, 0)
        Ellipse:
            size: (min(self.width, self.height), min(self.width, self.height))
            pos: (self.center_x - min(self.width, self.height) / 2, self.center_y - min(self.width, self.height) / 2)
    background_color: (0, 0, 0, 0)  # 设置背景透明
            
<Count>:
    control: layout_control
    t_hour: carousel_hour
    t_min: carousel_min
    t_sec: carousel_sec
    orientation: 'vertical'
    spacing: 10
    FloatLayout:
        size_hint: (1, .8)
        BoxLayout:
            size_hint: (.5, .5)
            pos_hint: {'x': .25, 'y': .5}
            Carousel:
                id: carousel_hour
                direction: 'top'
                loop: True
            Label:
                text: ':'
                font_size: 100
            Carousel:
                id: carousel_min
                direction: 'top'
                loop: True
            Label:
                text: ':'
                font_size: 100
            Carousel:
                id: carousel_sec
                direction: 'top'
                loop: True
        Label:
            id: label_timer
            size_hint: (.5, .5)
            pos_hint: {'x': .25, 'y': .0}
            text: "00"
            font_size: 100
    BoxLayout:
        id: layout_control
        size_hint: (1, .1)
        orientation: 'horizontal'
        spacing: 10 
""")


class EllipticButton(Button):
    """椭圆按钮类"""
    def __init__(self, **kwargs):
        super(EllipticButton, self).__init__(**kwargs)
        self.bind(state=self.change_foreground_color)

    def change_foreground_color(self, s, state):
        """修改前景色"""
        front_color = Color(0, 1, 0, .8)  # 修改此处可更改前景色
        front = InstructionGroup()
        front.add(front_color)
        front.add(Rectangle(pos=self.pos, size=self.size))
        if state == 'normal':
            self.canvas.after.clear()
        else:
            self.canvas.after.add(front)


class Count(BoxLayout):
    """倒计时布局"""
    control = ObjectProperty(None)
    t_hour = ObjectProperty(None)
    t_min = ObjectProperty(None)
    t_sec = ObjectProperty(None)
    timer = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super(Count, self).__init__(**kwargs)
        # 添加小时设置器
        for i in range(100):
            label = Label(text="{:0>2d}".format(i), font_size=80)
            self.t_hour.add_widget(label)
        self.t_hour.bind(index=self.set_hour)
        # 添加分钟设置器
        for i in range(60):
            label = Label(text="{:0>2d}".format(i), font_size=80)
            self.t_min.add_widget(label)
        self.t_min.bind(index=self.set_min)
        # 添加秒设置器
        for i in range(60):
            label = Label(text="{:0>2d}".format(i), font_size=80)
            self.t_sec.add_widget(label)
        self.t_sec.bind(index=self.set_sec)
        # 添加控制按钮
        self.start = EllipticButton(text='Start')
        self.start.bind(on_press=self.start_counting)
        self.pause_resume = EllipticButton(text='Pause')
        self.pause_resume.bind(on_press=self.timer_pause_resume)
        self.stop = EllipticButton(text='Stop')
        self.stop.bind(on_press=self.timer_stop)
        self.control.add_widget(self.start)
        # 控制信号
        self.counter = 0.0
        self.timer = 0.0
        self.stop_time = 0.0
        self.is_run = False
        self.is_paused = False
        self.bind(timer=self.update_timer)

    def set_hour(self, s, i):
        """设置小时"""
        pass

    def set_min(self, s, i):
        """设置分钟"""
        pass

    def set_sec(self, s, i):
        """设置秒数"""
        pass

    def timer_pause_resume(self, sender):
        """暂停/恢复倒计时"""
        if sender.text == 'Pause':  # 暂停计时器
            # 暂停计时器
            self.is_paused = True
            sender.text = 'Resume'
        else:  # 恢复计时器
            # 恢复计时器
            self.is_paused = False
            sender.text = 'Pause'

    def timer_stop(self, sender):
        """停止计时器"""
        self.is_run = False  # 停止倒计时线程
        self.timer = 0.0
        self.stop_time = 0.0

    def update_timer(self, s, t):
        """更新倒数器"""
        remain = int(self.counter - t)
        self.t_hour.index = remain // 3600
        self.t_min.index = (remain // 60) % 60
        self.t_sec.index = remain % 60
        self.ids.label_timer.text = "{:0>2d}".format(99 - int(t * 100) % 100)

    def start_counting(self, s):
        """启动倒计时"""
        # 获取设定时间
        self.counter = self.t_hour.index * 3600 + self.t_min.index * 60 + self.t_sec.index
        if self.counter <= 0:
            return
        else:
            # 移除开始按钮, 增加暂停/恢复，停止按钮
            self.control.remove_widget(self.start)
            self.control.add_widget(self.pause_resume)
            self.pause_resume.text = 'Pause'
            self.control.add_widget(self.stop)
            # 启动倒计时线程
            self.is_run = True
            self.is_paused = False
            self.timer = 0.0
            _thread.start_new_thread(self.thread_counting, ())

    def thread_counting(self):
        """倒计时线程"""
        start = time.time()
        while self.is_run:
            if self.is_paused:
                self.stop_time = time.time() - start - self.timer
            else:
                self.timer = time.time() - start - self.stop_time
            if self.timer >= self.counter:
                # self.timer = self.counter
                self.is_run = False
            time.sleep(.01)
        # 移除暂停/恢复，停止按钮, 增加开始按钮
        self.control.remove_widget(self.pause_resume)
        self.control.remove_widget(self.stop)
        self.control.add_widget(self.start)
        self.timer = 0


class CountApp(App):
    """倒计时小程序"""
    def build(self):
        return Count()


if __name__ == '__main__':
    CountApp().run()
