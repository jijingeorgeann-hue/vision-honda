from kivy.app import App
from kivy.uix.label import Label

class VisionHondaApp(App):
    def build(self):
        return Label(
            text='VISION HONDA\nDigital Sales Kit',
            font_size='25sp',
            halign='center'
        )

if __name__ == '__main__':
    VisionHondaApp().run()
