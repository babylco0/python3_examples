# kv 文件例程
import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty


# Builder.load_file('kivy_ex_kvfile.kv')

Builder.load_string("""
<MainLayout>:
    button: button1
    Button:
        id: button1
        text: 'Button ObjectProperty'
    Button:
        id: button2
        text: 'Button kv'
        on_press: root.state_changed(self, self.state)
        on_release: root.state_changed(self, self.state)
    Button:
        id: button3
        text: 'Button ids'
    Button:
        id: button4
        text: 'Button access kv'
        on_press: button1.state = 'down'
        on_release: button1.state = 'normal'
    Button:
        id: button5
        text: 'Button access label'
        on_press: root.label.text = '{0} state is {1}'.format(self.text, self.state)
        on_release: root.label.text = '{0} state is {1}'.format(self.text, self.state)
    Button:
        id: button6
        text: 'Button access app'
        on_press: root.label.text = '{0}:{1} state is {2}'.format(app.name, self.text, self.state)
        on_release: root.label.text = '{0}:{1} state is {2}'.format(app.name, self.text, self.state)
""")


class MainLayout(GridLayout):
    """主布局"""
    button = ObjectProperty(None)  # 定义一个对象属性

    def __init__(self, **kwargs):
        """主布局初始化"""
        super(MainLayout, self).__init__(**kwargs)
        self.cols = 1  # 设置行数为1
        self.button_init = Button(text='Button init')  # 按钮控件
        self.label = Label(text='')  # 标签控件，用于显示按钮状态
        self.add_widget(self.button_init)  # 添加控件至布局
        self.add_widget(self.label)
        self.button_init.bind(state=self.state_changed)  # 绑定按钮状态改变事件
        self.button.bind(state=self.state_changed)
        # self.ids['button3'].bind(state=self.state_changed)
        self.ids.button3.bind(state=self.state_changed)

    def state_changed(self, sender, state):
        """处理按钮状态改变事件"""
        self.label.text = '{0} state is {1}'.format(sender.text, state)


class MyApp(App):
    """主应用"""
    name = 'MyApp'

    def build(self):
        return MainLayout()


if __name__ == '__main__':
    MyApp().run()
