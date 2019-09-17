# 加密记事本程序
import json
import time
from os.path import exists, join

from kivy.app import App
from kivy.clock import Clock
from kivy.lang.builder import Builder
from kivy.properties import BooleanProperty, StringProperty, NumericProperty, ListProperty, \
    AliasProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition

__version__ = "1.0.0"

Builder.load_string("""
<MutableLabelTextInput@MutableTextInput>:
    # 普通标签
    Label:
        id: w_label
        pos: root.pos
        text: root.text
    # 输入框，双击标签时激活
    TextInput:
        id: w_textinput
        pos: root.pos
        text: root.text
        multiline: root.multiline
        on_focus: root.check_focus_and_view(self)

<MutableRstDocumentTextInput@MutableTextInput>:
    # Rst文档 <Android不支持Rst文档>
    RstDocument:
        id: w_label
        pos: root.pos
        text: root.text
    # 输入框，双击标签时激活
    TextInput:
        id: w_textinput
        pos: root.pos
        text: root.text
        multiline: root.multiline
        on_focus: root.check_focus_and_view(self)

<NoteView>:
    # 记事本查看/编辑
    on_note_content: app.set_note_content(self.note_index, self.note_content)
    on_note_title: app.set_note_title(self.note_index, self.note_title)

    BoxLayout:

        orientation: 'vertical'

        BoxLayout:

            orientation: 'horizontal'
            size_hint_y: None
            height: '48dp'
            padding: '5dp'
            # 背景色
            canvas:
                Color:
                    rgb: .3, .3, .3
                Rectangle:
                    pos: self.pos
                    size: self.size
            # 返回按钮，如果是新建且内容为空，则先删除再返回
            Button:
                text: '<'
                size_hint_x: None
                width: self.height
                on_release: 
                    if root.note_title == 'New note' and root.note_content == '' : \
                        app.del_note(root.note_index) 
                    app.go_notes()
            # 标题输入
            MutableLabelTextInput:
                text: root.note_title
                font_size: '16sp'
                multiline: False
                on_text: root.note_title = self.text
            # 删除按钮
            Button:
                text: 'X'
                size_hint_x: None
                width: self.height
                on_release: app.del_note(root.note_index)
        # 内容输入
        MutableLabelTextInput:
            text: root.note_content
            on_text: root.note_content = self.text

<NoteListItem>:
    # 记事本列表项
    on_note_mtime: root.update_mtime(root.note_mtime)
    height: '48sp'
    size_hint_y: None

    canvas:
        Color:
            rgb: .3, .3, .3
        Rectangle:
            pos: self.pos
            size: self.width, 1

    BoxLayout:

        padding: '5dp'
        # 标题
        Label:
            text: root.note_title
        # 修改时间
        Label:
            id: label_mtime
            text: "1982-07-07"
        # 编写按钮
        Button:
            text: '>'
            size_hint_x: None
            width: self.height
            on_release: app.edit_note(root.note_index)
        
<Notes>:
    # 记事本
    BoxLayout:

        orientation: 'vertical'

        BoxLayout:

            orientation: 'horizontal'
            size_hint_y: None
            height: '48dp'
            padding: '5dp'

            canvas:
                Color:
                    rgb: .3, .3, .3
                Rectangle:
                    pos: self.pos
                    size: self.size
            # 图标
            Image:
                source: 'icon.png'
                mipmap: True
                size_hint_x: None
                width: self.height
            # 标题
            Label:
                text: 'Notes'
                font_size: '16sp'
            # 新建按钮
            Button:
                text: '+'
                size_hint_x: None
                width: self.height
                on_release: app.add_note()
        # 记事本标题列表
        RecycleView:
            data: root.data_for_widgets
            viewclass: 'NoteListItem'
            RecycleBoxLayout:
                default_size: None, dp(56)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
                spacing: dp(2)

""")


class MutableTextInput(FloatLayout):
    """可变文本输入框"""
    text = StringProperty()
    multiline = BooleanProperty(True)

    def __init__(self, **kwargs):
        """初始化"""
        super(MutableTextInput, self).__init__(**kwargs)
        Clock.schedule_once(self.prepare, 0)

    def prepare(self, *args):
        """设置显示和输入"""
        self.w_textinput = self.ids.w_textinput.__self__
        self.w_label = self.ids.w_label.__self__
        self.view()

    def on_touch_down(self, touch):
        """双击标签编辑"""
        if self.collide_point(*touch.pos) and touch.is_double_tap:
            self.edit()
        return super(MutableTextInput, self).on_touch_down(touch)

    def edit(self):
        """编辑内容"""
        self.clear_widgets()
        self.add_widget(self.w_textinput)
        self.w_textinput.focus = True

    def view(self):
        self.clear_widgets()
        if not self.text:
            self.w_label.text = "Double tap/click to edit"
        self.add_widget(self.w_label)

    def check_focus_and_view(self, textinput):
        """当输入框失去焦点时显示内容"""
        if not textinput.focus:
            self.text = textinput.text
            self.view()


class NoteView(Screen):
    """记事本编辑/查看"""
    note_index = NumericProperty()
    note_title = StringProperty()
    note_content = StringProperty()
    note_mtime = NumericProperty()


class NoteListItem(BoxLayout):
    """记事本列表"""
    note_content = StringProperty()
    note_title = StringProperty()
    note_index = NumericProperty()
    note_mtime = NumericProperty()

    def update_mtime(self, mtime):
        """更新修改时间"""
        self.ids.label_mtime.text = time.strftime("%Y-%m-%d\n%H:%M:%S", time.localtime(mtime))


class Notes(Screen):
    """记事本类"""
    data = ListProperty()

    def _get_data_for_widgets(self):
        return [{
            'note_index': index,
            'note_content': item['content'],
            'note_title': item['title'],
            'note_mtime': item['mtime']}
            for index, item in enumerate(self.data)]

    data_for_widgets = AliasProperty(_get_data_for_widgets, bind=['data'])


class NoteApp(App):
    """记事本程序"""
    def build(self):
        self.notes = Notes(name='notes')
        self.load_notes()  # 加载记事本
        self.transition = SlideTransition(duration=.35)
        root = ScreenManager(transition=self.transition)
        root.add_widget(self.notes)
        return root

    def load_notes(self):
        """加载记事本"""
        if not exists(self.notes_fn):
            self.notes.data = []
            return
        with open(self.notes_fn) as fd:
            data = json.load(fd)
        self.notes.data = data

    def add_note(self):
        """增加一个记事"""
        self.notes.data.append({'title': 'New note',
                                'content': '',
                                'mtime': time.time()})
        note_index = len(self.notes.data) - 1
        self.edit_note(note_index)

    def edit_note(self, note_index):
        """编辑记事"""
        note = self.notes.data[note_index]
        name = 'note{}'.format(note_index)

        if self.root.has_screen(name):
            self.root.remove_widget(self.root.get_screen(name))

        view = NoteView(
            name=name,
            note_index=note_index,
            note_title=note.get('title'),
            note_content=note.get('content'),
            note_mtime=note.get('mtime'))
        self.root.add_widget(view)
        self.transition.direction = 'left'
        self.root.current = view.name

    def del_note(self, note_index):
        """删除记事"""
        del self.notes.data[note_index]
        self.save_notes()
        self.refresh_notes()
        self.go_notes()

    def set_note_content(self, note_index, note_content):
        """设置记事内容"""
        self.notes.data[note_index]['content'] = note_content
        self.notes.data[note_index]['mtime'] = time.time()
        data = self.notes.data
        self.notes.data = []
        self.notes.data = data
        self.save_notes()
        self.refresh_notes()

    def set_note_title(self, note_index, note_title):
        """设置记事标题"""
        self.notes.data[note_index]['title'] = note_title
        self.notes.data[note_index]['mtime'] = time.time()
        self.save_notes()
        self.refresh_notes()

    def refresh_notes(self):
        """刷新记事本"""
        data = self.notes.data
        self.notes.data = []
        self.notes.data = data

    def save_notes(self):
        """保存记事"""
        with open(self.notes_fn, 'w') as fd:
            json.dump(self.notes.data, fd)

    def go_notes(self):
        """返回记事本列表"""
        self.transition.direction = 'right'
        self.root.current = 'notes'

    @property
    def notes_fn(self):
        return join('./', 'notes.json')


if __name__ == '__main__':
    NoteApp().run()
