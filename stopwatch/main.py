import time
import _thread

from kivy.app import App
from kivy.clock import Clock
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

__version__ = "1.0.0"

Builder.load_string("""
<Stopwatch>:
    control: layout_control
    timer: label_timer
    # start: button_start
    record: layout_record
    orientation: 'vertical'
    spacing: 10
    Label:
        id: label_timer
        size_hint:(1, .8)
        font_size: 100
        text: "00:00:00.00"
    ScrollView:
        id: sv
        size_hint: (1, .1)
        GridLayout:
            id: layout_record
            cols: 1
            spacing: 10
            size_hint_y: None
            height: max(self.minimum_height, sv.height)
    BoxLayout:
        id: layout_control
        size_hint: (1, .1)
        orientation: 'horizontal'
        spacing: 10
    #    Button:  # 定义在kv文件中的控件被移除后，再次添加会出现错误
    #        id: button_start
    #        text: 'Start' 
    #        on_press: root.timer_start() 
""")


class Stopwatch(BoxLayout):
    """计时器布局"""
    control = ObjectProperty(None)  # 控制组
    # start = ObjectProperty(None)  # 开始按钮
    record = ObjectProperty(None)  # 记录
    timer = ObjectProperty(None)  # 计时器
    counter = NumericProperty(0)  # 计时器内部计数，以0.01s为单位

    def __init__(self, **kwargs):
        """初始化"""
        super(Stopwatch, self).__init__(**kwargs)
        self.start = Button(text='Start')  # 启动按钮
        self.start.bind(on_press=self.timer_start)
        self.pause_resume = Button(text='Pause')  # 暂停/恢复按钮
        self.pause_resume.bind(on_press=self.timer_pause_resume)
        self.record_reset = Button(text='Record')  # 记录/重置按钮
        self.record_reset.bind(on_press=self.timer_record_reset)
        self.start_time = 0.0  # 计时器启动时的时间戳
        self.paused_time = 0.0  # 暂停时间计时
        self.record_index = 0
        self.record_list = []
        self.bind(counter=self.update_timer)  # 自动更新计时器
        self.is_stopped = True
        self.is_paused = True
        self.control.add_widget(self.start)

    def timer_count(self):
        """计时器计数"""
        self.start_time = time.time()
        while not self.is_stopped:
            if self.is_paused:  # 暂停计时器
                self.paused_time = time.time() - self.start_time - self.counter  # 记录暂停时间
            else:
                self.counter = time.time() - self.start_time - self.paused_time  # 当前时间-启动时间-暂停时间
            time.sleep(0.01)

    def update_timer(self, s, c):
        """更新计时器显示"""
        int_counter = int(c * 100)  # 取整数部分
        tm_ms = int_counter % 100  # 毫秒数
        tm_sec = (int_counter // 100) % 60  # 秒数
        tm_min = (int_counter // 6000) % 60  # 分钟数
        tm_hour = (int_counter // 360000)  # 小时数
        self.timer.text = "{:d}:{:0>2d}:{:0>2d}.{:0>2d}".format(tm_hour, tm_min, tm_sec, tm_ms)  # 更新显示

    def timer_start(self, sender):
        """计时器启动"""
        # 移除启动按钮
        self.control.remove_widget(self.start)
        # 添加暂停/重置按钮
        self.pause_resume.text = 'Pause'
        self.record_reset.text = 'Record'
        self.control.add_widget(self.pause_resume)
        self.control.add_widget(self.record_reset)
        # 启动计时器
        self.is_stopped = False
        self.is_paused = False
        _thread.start_new_thread(self.timer_count, ())

    def timer_pause_resume(self, sender):
        """计时器暂停/恢复"""
        if sender.text == 'Pause':  # 暂停计时器
            # 暂停计时器
            self.is_paused = True
            sender.text = 'Resume'
            self.record_reset.text = 'Reset'
        else:  # 恢复计时器
            # 恢复计时器
            self.is_paused = False
            sender.text = 'Pause'
            self.record_reset.text = 'Record'

    def timer_record_reset(self, sender):
        """记录一次数据"""
        if sender.text == 'Record':  # 记录一次
            # 记录
            if self.record_index == 0:  # 第一次记录修改布局
                self.timer.size_hint = (1, .2)
                self.ids.sv.size_hint = (1, .7)
                self.control.size_hint = (1, .1)
            r = self.counter
            self.record_list.append(r)
            int_counter = int(r * 100)  # 取整数部分
            tm_ms = int_counter % 100  # 毫秒数
            tm_sec = (int_counter // 100) % 60  # 秒数
            tm_min = (int_counter // 6000) % 60  # 分钟数
            tm_hour = (int_counter // 360000)  # 小时数
            layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=80)
            layout.add_widget(Label(text="{}".format(self.record_index + 1)))
            layout.add_widget(Label(text="{:d}:{:0>2d}:{:0>2d}.{:0>2d}".format(tm_hour, tm_min, tm_sec, tm_ms)))
            dt = r - self.record_list[0]
            int_counter = int(dt * 100)  # 取整数部分
            tm_ms = int_counter % 100  # 毫秒数
            tm_sec = (int_counter // 100) % 60  # 秒数
            tm_min = (int_counter // 6000) % 60  # 分钟数
            tm_hour = (int_counter // 360000)  # 小时数
            layout.add_widget(Label(text="+{:d}:{:0>2d}:{:0>2d}.{:0>2d}".format(tm_hour, tm_min, tm_sec, tm_ms)))
            self.record.add_widget(layout)
            self.record_index += 1
        else:  # 重置计数器
            # 移除暂停/恢复，记录/重置按钮
            self.is_stopped = True
            self.counter = 0.0
            self.paused_time = 0.0
            self.control.remove_widget(self.pause_resume)
            self.control.remove_widget(self.record_reset)
            # 添加启动按钮
            self.record.clear_widgets()
            self.control.add_widget(self.start)
            # 恢复布局
            self.timer.size_hint = (1, .8)
            self.ids.sv.size_hint = (1, .1)
            self.control.size_hint = (1, .1)
            self.record_list.clear()
            self.record_index = 0


class StopwatchApp(App):
    """计时器小程序"""
    def build(self):
        return Stopwatch()

    def on_pause(self):
        return True


if __name__ == '__main__':
    StopwatchApp().run()
