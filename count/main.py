# 倒计时/计时器程序
import _thread
import time

from kivy.app import App
from kivy.graphics import Color
from kivy.graphics import Rectangle
from kivy.graphics.instructions import InstructionGroup
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

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
            size_hint: (.5, None)
            height: lb.texture_size[1]  # 设置高度为标签文本高度
            pos_hint: {'x': .25, 'y': .5}
            # 倒计时小时值手动输入框
            NumericTextInput:
                id: carousel_hour
                _max: 100
                font_size: 100
                height: lb.texture_size[1]
            Label:
                id: lb
                text: ':'
                font_size: 100
                size: self.texture_size
             # 倒计时分钟值手动输入框
            NumericTextInput:
                id: carousel_min
                _max: 60
                font_size: 100
                height: lb.texture_size[1]
            Label:
                text: ':'
                font_size: 100
             # 倒计时秒数值手动输入框
            NumericTextInput:
                id: carousel_sec
                _max: 60
                font_size: 100
                height: lb.texture_size[1]
        # 倒计时0.01s显示
        Label:
            id: label_timer
            size_hint: (.5, .5)
            pos_hint: {'x': .25, 'y': .0}
            text: "00"
            font_size: 100
        # 控制按钮-设置倒计时小时值
        Button:
            text: '+'
            size_hint: (None, None)
            size: carousel_hour.size
            pos: carousel_hour.pos[0], carousel_hour.pos[1] + carousel_hour.height
            on_press: carousel_hour.value = (carousel_hour.value + 1) % carousel_hour._max
        Button:
            text: '-'
            size_hint: (None, None)
            size: carousel_hour.size
            pos: carousel_hour.pos[0], carousel_hour.pos[1] - carousel_hour.height
            on_press: carousel_hour.value = (carousel_hour.value - 1) % carousel_hour._max
        # 控制按钮-设置倒计时分钟值
        Button:
            text: '+'
            size_hint: (None, None)
            size: carousel_min.size
            pos: carousel_min.pos[0], carousel_min.pos[1] + carousel_min.height
            on_press: carousel_min.value = (carousel_min.value + 1) % carousel_min._max
        Button:
            text: '-'
            size_hint: (None, None)
            size: carousel_min.size
            pos: carousel_min.pos[0], carousel_min.pos[1] - carousel_min.height
            on_press: carousel_min.value = (carousel_min.value - 1) % carousel_min._max
        # 控制按钮-设置倒计时秒数值
        Button:
            text: '+'
            size_hint: (None, None)
            size: carousel_sec.size
            pos: carousel_sec.pos[0], carousel_sec.pos[1] + carousel_sec.height
            on_press: carousel_sec.value = (carousel_sec.value + 1) % carousel_sec._max
        Button:
            text: '-'
            size_hint: (None, None)
            size: carousel_sec.size
            pos: carousel_sec.pos[0], carousel_sec.pos[1] - carousel_sec.height
            on_press: carousel_sec.value = (carousel_sec.value - 1) % carousel_sec._max
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


class NumericTextInput(TextInput):
    """数字输入框
    仅允许输入2位数数字且小于最大值"""
    _max = NumericProperty(0)  # 可现实最大数值
    value = NumericProperty(0)  # 数值

    def __init__(self, **kwargs):
        super(NumericTextInput, self).__init__(**kwargs)
        self.halign = 'center'  # 文本居中
        self.multiline = False  # 单行
        self.size_hint_y = None  # 高度为绝对值
        # self.height = self.line_height
        self.input_filter = 'int'  # 仅可输入数值
        self.bind(text=self.on_text)
        self.bind(value=self.on_value)

    def on_text(self, sender, txt):
        """文本值改变事件"""
        if txt == '':
            self.text = '00'
        else:
            self.value = int(txt)
            if self.value >= self._max:  # 当值大于超过最大值时，设置值为0
                self.text = "{:0>2d}".format(0)
                self.select_all()
            else:  # 格式化显示样式
                self.text = "{:0>2d}".format(self.value)

    def on_value(self, sender, v):
        """修改文本"""
        self.text = "{:0>2d}".format(self.value)


class Count(BoxLayout):
    """倒计时布局"""
    control = ObjectProperty(None)  # 控制面板
    t_hour = ObjectProperty(None)  # 倒计时小时值
    t_min = ObjectProperty(None)  # 倒计时分钟值
    t_sec = ObjectProperty(None)  # 倒计时秒数值
    timer = NumericProperty(0.0)  # 内部计时器数值

    def __init__(self, **kwargs):
        super(Count, self).__init__(**kwargs)
        # 添加控制按钮
        self.start = EllipticButton(text='Start')  # 开始倒计时按钮
        self.start.bind(on_press=self.start_counting)
        self.pause_resume = EllipticButton(text='Pause')  # 暂停/恢复倒计时按钮
        self.pause_resume.bind(on_press=self.timer_pause_resume)
        self.stop = EllipticButton(text='Stop')  # 停止倒计时按钮
        self.stop.bind(on_press=self.timer_stop)
        self.control.add_widget(self.start)
        # 控制信号
        self.counter = 0.0  # 目标计数值
        self.timer = 0.0  #
        self.stop_time = 0.0  # 暂停计数值
        self.is_run = False  # 计数器运行指示
        self.is_paused = False  # 计数器停止指示
        self.bind(timer=self.update_timer)

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

    def update_timer(self, s, t):
        """更新倒数器"""
        remain = int(self.counter - t)  # 剩余倒计时值
        self.t_hour.value = remain // 3600
        self.t_min.value = (remain // 60) % 60
        self.t_sec.value = remain % 60
        self.ids.label_timer.text = "{:0>2d}".format(99 - int(t * 100) % 100)

    def start_counting(self, s):
        """启动倒计时"""
        # 获取设定时间，即计数器目标值
        self.counter = self.t_hour.value * 3600 + self.t_min.value * 60 + self.t_sec.value
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
            self.stop_time = 0.0
            _thread.start_new_thread(self.thread_counting, ())

    def thread_counting(self):
        """倒计时线程"""
        start = time.time()
        while self.is_run:
            if self.is_paused:
                self.stop_time = time.time() - start - self.timer
            else:
                self.timer = time.time() - start - self.stop_time
            if self.timer >= self.counter:  # 停止计数
                self.is_run = False
            time.sleep(.01)
        # 移除暂停/恢复，停止按钮, 增加开始按钮
        self.control.remove_widget(self.pause_resume)
        self.control.remove_widget(self.stop)
        self.control.add_widget(self.start)
        self.timer = 0  # 设置计数器值为0, 会自动更新倒计时器数值


class CountApp(App):
    """倒计时小程序"""
    def build(self):
        return Count()


if __name__ == '__main__':
    CountApp().run()
