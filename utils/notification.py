from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.icon_definitions import md_icons
from kivymd.uix.label import MDIcon
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import StringProperty, ObjectProperty

class Notificador(MDCard):
    texto = StringProperty()
    icono = StringProperty('information')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (Window.width * 0.8, dp(50))
        self.pos_hint = {"center_x": 0.5, "top": 1.1}  # Empezamos fuera de la pantalla
        self.md_bg_color = (0.2, 0.7, 0.2, 1)
        self.radius = [10, 10, 10, 10]
        self.elevation = 10
        self.opacity = 0

        # Crear layout para icono y texto
        self.layout = MDBoxLayout(orientation='horizontal', padding=[10, 0, 10, 0], spacing=10, adaptive_height=True)
        
        # Agregar icono
        self.icon_widget = MDIcon(
            icon=self.icono, 
            theme_text_color="Custom", 
            text_color=(1, 1, 1, 1),
            pos_hint={'center_y': 0.5}
        )
        self.layout.add_widget(self.icon_widget)
        
        # Agregar el texto como un MDLabel
        self.label = MDLabel(
            text=self.texto,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            size_hint_y=None,
            height=self.height
        )
        self.layout.add_widget(self.label)
        
        self.add_widget(self.layout)

    def on_texto(self, instance, value):
        self.label.text = value

    def on_icono(self, instance, value):
        self.icon_widget.icon = value

    def mostrar(self, texto, icono='information', duracion=3):
        self.texto = texto
        self.icono = icono
        self.opacity = 1
        anim = Animation(pos_hint={"center_x": 0.5, "top": 0.95}, duration=0.3)
        anim.start(self)
        Clock.schedule_once(self.iniciar_ocultar, duracion)

    def iniciar_ocultar(self, *args):
        anim = Animation(pos_hint={"center_x": 0.5, "top": 1.1}, duration=0.3)
        anim.bind(on_complete=self.reset_opacity)
        anim.start(self)

    def reset_opacity(self, *args):
        self.opacity = 0

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.iniciar_ocultar()
            return True
        return super().on_touch_down(touch)