from kivy.uix.screenmanager import Screen

class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("WelcomeScreen initialized")
