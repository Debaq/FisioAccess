from kivy.uix.screenmanager import Screen

class PreferencesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("PreferencesScreen initialized")
