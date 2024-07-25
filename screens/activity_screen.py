from kivy.uix.screenmanager import Screen

class ActivityScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("ActivityScreen initialized")
