# 记事本程序

from kivy.app import App
from kivy.lang.builder import Builder
from kivy.properties import BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.screenmanager import ScreenManager, Screen

Builder.load_string("""
<SelectableLabel>:
    # Draw a background to indicate selection
    canvas.before:
        Color:
            rgba: (.0, 0.9, .1, .3) if self.selected else (0, 0, 0, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    halign: 'left'
<RV>:
    viewclass: 'SelectableLabel'
    SelectableRecycleGridLayout:
        default_size: None, dp(56)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        # orientation: 'vertical'
        cols: 10
        multiselect: True
<NoteList>:
    GridLayout:
        cols: 1
        # 顶部控制按钮组
        BoxLayout:
            size_hint_y: None
            height: 52
            Button:
                size_hint: (None, None)
                size: (52, 52)
                text: 'New'
            Button:
        RV:
""")


class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''

        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''

        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''

        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))


class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior, RecycleGridLayout):
    """ Adds selection and focus behaviour to the view. """


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = [{'text': str(x)} for x in range(100)]

class NoteList(Screen):
    """记事本列表屏幕"""
    pass


class NoteEditor(Screen):
    """记事本编辑屏幕"""
    pass


class NoteApp(App):
    """记事本程序"""
    def build(self):
        sm = ScreenManager()
        list_screen = NoteList(name='list')
        edit_screen = NoteEditor(name='edit')
        sm.add_widget(list_screen)
        sm.add_widget(edit_screen)
        sm.current = 'list'
        return sm


if __name__ == '__main__':
    NoteApp().run()
