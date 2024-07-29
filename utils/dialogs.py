from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDButton

def create_confirm_dialog(close_callback, back_callback):
    return MDDialog(
        title="Confirmación",
        text="¿Desea salir sin guardar?",
        buttons=[
            MDButton(text="CANCELAR", on_release=close_callback),
            MDButton(text="SALIR", on_release=back_callback)
        ],
    )
