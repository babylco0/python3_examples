import kivy
from kivy.app import App
from kivy.uix.button import Button


class FirstApp(App):
    """第一个kivy程序"""
    def build(self):
        return Button(text='Hello kivy')


if __name__ == '__main__':
    FirstApp().run()
