from kivymd.uix.menu import MDDropdownMenu

def create_menu(callback):
    menu_items = [
        {"viewclass": "OneLineListItem", "text": "EEG", "on_release": lambda x="EEG": callback(x)},
        {"viewclass": "OneLineListItem", "text": "ECG", "on_release": lambda x="ECG": callback(x)},
        {"viewclass": "OneLineListItem", "text": "EMG", "on_release": lambda x="EMG": callback(x)},
        {"viewclass": "OneLineListItem", "text": "Espirometría", "on_release": lambda x="Espirometría": callback(x)},
        {"viewclass": "OneLineListItem", "text": "Presión Arterial", "on_release": lambda x="Presión Arterial": callback(x)},
    ]
    return MDDropdownMenu(items=menu_items, width_mult=4)
