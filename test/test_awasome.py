from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu

KV = '''
MDScreen:
    md_bg_color: self.theme_cls.bg_normal

    MDTopAppBar:
        id: top_app_bar
        type: "small"
        size_hint_x: .8
        pos_hint: {"center_x": .5, "center_y": .9}

        MDTopAppBarLeadingButtonContainer:

            MDActionTopAppBarButton:
                icon: "arrow-left"

        MDTopAppBarTitle:
            text: "AppBar small"

        MDTopAppBarTrailingButtonContainer:

            MDActionTopAppBarButton:
                icon: "attachment"

            MDActionTopAppBarButton:
                icon: "calendar"

            MDActionTopAppBarButton:
                icon: "dots-vertical"
                on_release: app.open_menu(self)

    MDDropdownMenu:
        id: menu
        width_mult: 4
        items: [{"viewclass": "OneLineListItem", "text": "Option 1", "height": dp(56), "on_release": lambda x="Option 1": app.menu_callback(x)},{"viewclass": "OneLineListItem", "text": "Option 2", "height": dp(56), "on_release": lambda x="Option 2": app.menu_callback(x)},{"viewclass": "OneLineListItem", "text": "Option 3", "height": dp(56), "on_release": lambda x="Option 3": app.menu_callback(x)}]
'''

class MyApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def open_menu(self, instance):
        menu = self.root.ids.menu
        menu.caller = instance
        menu.open()

    def menu_callback(self, text_item):
        print(f"Menu item {text_item} clicked")
        self.root.ids.menu.dismiss()

if __name__ == "__main__":
    MyApp().run()
