from kivy.uix.screenmanager import Screen

class HelpScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("HelpScreen initialized")
