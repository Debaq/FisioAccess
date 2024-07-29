from kivy.animation import Animation
from kivy.properties import BooleanProperty, ObjectProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivymd.app import MDApp
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivymd.uix.button import MDButton, MDButtonText
import os
import platform

class NavItem(ButtonBehavior, MDBoxLayout):
    icon = StringProperty("")
    text = StringProperty("")


class HomeScreen(MDScreen):
    nav_drawer_collapsed = BooleanProperty(True)
    app = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def toggle_nav_drawer(self):
        self.nav_drawer_collapsed = not self.nav_drawer_collapsed
        nav_card = self.ids.nav_card
        if self.nav_drawer_collapsed:
            nav_card.size_hint_x = 0.07
        else:
            nav_card.size_hint_x = 0.15

    def highlight_button(self, button):
        return
        for child in self.ids.nav_items.children:
            if isinstance(child, NavItem):
                child.md_bg_color = self.app.theme_cls.primaryColor if child == button else [0, 0, 0, 0]

    def show_exit_confirmation(self):
        self.dialog = MDDialog(
            # ----------------------------Icon-----------------------------
            MDDialogIcon(
                icon="power",
            ),
            # -----------------------Headline text-------------------------
            MDDialogHeadlineText(
                text="Gestión de Energía",
            ),
            # -----------------------Supporting text-----------------------
            MDDialogSupportingText(
                text="¿Desea apagar el sistema?",
            ),
            # -----------------------Custom content------------------------

            # ---------------------Button container------------------------
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Cancelar"),
                    style="text",
                    on_release=self.close_dialog  # Cambiado aquí
                ),
                MDButton(
                    MDButtonText(text="Apagar"),
                    style="text",
                    on_release=self.power_off  # Añadido un método para apagar
                ),
                spacing="8dp",
            ),
            # -------------------------------------------------------------
        )
        self.dialog.open()

    def close_dialog(self, *args):
        print("Cerrando diálogo")
        if hasattr(self, 'dialog'):
            self.dialog.dismiss()
        else:
            print("No se encontró el diálogo para cerrar")

    def power_off(self, *args):
        print("Apagando el sistema")
        self.close_dialog()
        
        system = platform.system()
        
        if system == "Linux":
            os.system("shutdown -h now")
        else:
            print(f"Sistema operativo no reconocido: {system}")
            # Aquí podrías mostrar un mensaje al usuario