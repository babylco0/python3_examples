# 卡牌小游戏程序
import _thread
import random
import time

from kivy.app import App
from kivy.lang.builder import Builder
from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior

__version__ = "1.0.0"

Builder.load_string("""
<SelectableCard>:
    # 背景色来指示卡牌类型
    canvas.before:
        Color:
            rgba: 
                (1, 0, 0, 1) if self.mode == 0 \
                else (0, 1, 0, 1) if self.mode == 1 \
                else (0, 0, 1, 1) if self.mode == 2 \
                else (1, 0, 1, 1)
        Ellipse:
            size: self.size
            pos: self.pos
    # 前景色 选中时透明
    canvas.after:
        Color:
            rgba: 
                (0, 0, 0, 1) if not self.selectable \
                else (1, 1, 1, .1) if self.selected \
                else (.1, .8, .5, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    font_size: sp(30)
<RV>:
    layout: gridlayout
    viewclass: 'SelectableCard'
    SelectableRecycleGridLayout:
        id: gridlayout
        default_size: dp(60), dp(60)
        default_size_hint: None, None
        size_hint_y: None
        height: self.minimum_height
        cols: 6
        spacing: 10
        multiselect: True
        touch_multiselect: True
<TurnOver>:
    orientation: 'vertical'
    BoxLayout:
        orientation: 'horizontal' 
        size_hint_y: None
        height: sp(52)
        Button:
            text: 'New'
            size_hint_x: None
            width: sp(52)
            on_press: 
                rv.layout.count = 0
                rv.new_game()
        Label:
            text: '{}'.format(rv.layout.count)
        Button:
            size_hint_x: None
            width: sp(52)
            text: 'Help'
            on_press: rv.open_all()
    BoxLayout:
        orientation: 'horizontal' 
        Label:
        RV:
            id: rv
            size_hint_x: None
            width: sp(430)
        Label: 
    Label: 
        size_hint_y: None
        height: sp(52)
        text: '{}:{}'.format((rv.layout.timer // 60), (rv.layout.timer % 60))
""")


class FinishedPopup(Popup):

    def __init__(self, **kwargs):
        super(FinishedPopup, self).__init__(**kwargs)
        self.auto_dismiss = True


class SelectableCard(RecycleDataViewBehavior, Label):
    """ 可翻转的卡牌"""
    index = None
    mode = NumericProperty(0)
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        """视图改变"""
        self.index = index
        return super(SelectableCard, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        """ 触摸按下事件"""
        if super(SelectableCard, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:  # 按下坐标是否在卡牌坐标内且改卡牌可被选中
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """卡牌被选中"""
        self.selected = is_selected


class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior, RecycleGridLayout):
    """卡牌网格布局"""
    is_checking = False  # 是否正在检测卡牌
    count = NumericProperty(0)  # 翻牌次数
    timer = NumericProperty(0)  # 使用时间
    is_starting = False  # 开始计时标识

    def select_with_touch(self, index, touch):
        """触碰选中"""
        if self.is_checking:
            return
        if len(self.selected_nodes) != 0:  # 获取选中卡牌数量
            pre_index = self.selected_nodes[0]
            if pre_index == index:  # 两次点击相同卡牌
                return
        super(SelectableRecycleGridLayout, self).select_with_touch(index, touch)
        self.count += 1  # 翻转次数加一
        if not self.is_starting:
            self.is_starting = True
            _thread.start_new_thread(self.thread_timer, ())
        if len(self.selected_nodes) > 1:  # 当选中卡牌为2个时 检测选中卡牌是否相同
            self.is_checking = True
            _thread.start_new_thread(self.check_selected_cards, ())

    def thread_timer(self):
        """计时线程"""
        start = time.time()
        while self.is_starting:
            self.timer = int(time.time() - start)
            time.sleep(.1)

    def check_selected_cards(self):
        """检测被选中卡牌是否相同"""
        pre_index = self.selected_nodes[0]
        index = self.selected_nodes[1]
        if (self.parent.data[pre_index]['mode'] == self.parent.data[index]['mode']) and (
                self.parent.data[pre_index]['text'] == self.parent.data[index]['text']):  # 卡牌相同
            # 使两张卡牌无效
            self.parent.data[index]['mode'] = self.parent.data[pre_index]['mode'] = 0
            self.parent.data[index]['selectable'] = self.parent.data[pre_index]['selectable'] = False
            # 更新视图
            self.parent.refresh_from_data()
        time.sleep(.3)  # 延时0.3s 清空选择
        self.clear_selection()
        # 检查是否已全部消除
        for card in self.parent.data:
            if card['selectable']:
                self.is_checking = False
                return
        # 已全部消除显示弹窗
        popup = FinishedPopup(title='Score: {}'.format(self.count), size_hint=(.8, .2))
        popup.content = Label(text='Using: {}m{}s'.format((self.timer // 60), (self.timer % 60)))
        popup.open()
        self.is_starting = False  # 停止计时
        self.timer = 0
        self.count = 0
        self.parent.new_game()


class RV(RecycleView):
    """Recycle 视图类"""
    layout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.new_game()

    def new_game(self):
        """新游戏"""
        self.data = [{'text': str(x), 'mode': x % 3, 'selectable': True, 'selected': True} for x in range(24)] * 2
        random.shuffle(self.data)  # 随机打乱顺序
        self.refresh_from_data()

    def open_all(self):
        """选中所有卡牌以显示"""
        _thread.start_new_thread(self.select_all, ())

    def select_all(self):
        for x in range(48):
            self.layout.select_node(x)
        time.sleep(1)
        self.layout.clear_selection()


class TurnOver(BoxLayout):
    """翻转卡牌游戏"""
    pass


class TurnOverApp(App):
    """翻转卡牌程序"""
    def build(self):
        return TurnOver()


if __name__ == '__main__':
    TurnOverApp().run()
