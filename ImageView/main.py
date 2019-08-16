# 图片查看器

from kivy.app import App
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty
from kivy.uix.filechooser import FileSystemLocal
from kivy.uix.screenmanager import Screen, ScreenManager

__version__ = "1.0.0"

Builder.load_string("""
<ImageSelection>:
    file_chooser: fc
    BoxLayout:
        orientation: 'vertical'
        # 选择文件显示样式 列表/图标
        BoxLayout:
            size_hint_y: None
            height: sp(52)
            Button:
                text: 'Icon View'
                on_press: fc.view_mode = 'icon'
            Button:
                text: 'List View'
                on_press: fc.view_mode = 'list'
        Label:
            size_hint_y: None
            height: sp(52)
            text: fc.path
        FileChooser:
            id: fc
            path: '/sdcard/DCIM'  # android 照片存储目录
            rootpath: '/sdcard'  # 固定根目录为sdcard
            filters: ['*.jpg', '*.png',  '*.gif']  # 文件名后缀过滤
            on_submit: root.view_image()
            FileChooserIconLayout
            FileChooserListLayout
<ImageView>:
    image: image
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: None
            height: sp(52)
            Button:
                text: 'Return Selection'
                on_press:
                    root.manager.transition.direction = 'right'  # 屏幕滑动方向
                    root.manager.current = 'selection'
        AsyncImage:
            id: image
            allow_stretch: True
            keep_data: True
            anim_delay: 0.1
            source: ''
        BoxLayout:
            size_hint_y: None
            height: sp(52)
            Button:
                text: 'Prev Image'
                on_press: root.show_prev()
            Button:
                text: 'Next Image'
                on_press: root.show_next()
""")


class ImageView(Screen):
    """图片查看屏幕"""
    image = ObjectProperty(None)  # 图片

    def __init__(self, **kwargs):
        """初始化"""
        super(ImageView, self).__init__(**kwargs)
        self.list = []
        self.current = 0

    def set_image(self, p):
        """设置图片"""
        self.image.source = p
        # 添加图片至列表
        self.list.clear()
        idx = 0
        for f in self.manager.get_screen('selection').file_chooser.files : # 获取当前图片路径
            if not FileSystemLocal().is_dir(f):
                if f == p:  # 记录当前图片在文件中的位置
                    self.current = idx
                self.list.append(f)
                idx += 1

    def show_next(self):
        """显示下一张图片"""
        self.current += 1
        if self.current >= len(self.list):
            self.current = 0
        self.image.source = self.list[self.current]

    def show_prev(self):
        """显示上一张图片"""
        self.current -= 1
        if self.current < 0:
            self.current = len(self.list) - 1
        self.image.source = self.list[self.current]


class ImageSelection(Screen):
    """图片选择器"""
    file_chooser = ObjectProperty(None)  # 文件选择

    def view_image(self):
        """显示图片"""
        self.manager.get_screen('view').set_image(self.file_chooser.selection[0])
        self.manager.transition.direction = 'left'
        self.manager.current = 'view'


class ImageViewApp(App):
    def build(self):
        sm = ScreenManager()
        selection_screen = ImageSelection(name='selection')  # 定义一个图片选择屏幕
        view_screen = ImageView(name='view')  # 定义一个图片查看屏幕
        sm.add_widget(selection_screen)  # 添加屏幕至屏幕管理
        sm.add_widget(view_screen)
        sm.current = 'selection'
        return sm


ImageViewApp().run()
