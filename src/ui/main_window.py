import json
import os
import sys
from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Qt, QLocale

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.setupUi()
        
    def load_config(self):
        """Cargar configuración desde config.json"""
        # Obtener el directorio base de la aplicación
        if getattr(sys, "frozen", False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        config_path = os.path.join(base_path, "config", "config.json")
        try:
            with open(config_path, "r") as f:
                self.config = json.load(f)
            
            # Aplicar configuración
            self.setWindowTitle(self.tr(self.config["window_title"]))
            self.resize(
                self.config["window_size"]["width"],
                self.config["window_size"]["height"]
            )
        except Exception as e:
            print(self.tr("Error loading configuration: {}").format(e))
            self.config = {
                "app_name": "App",
                "window_title": self.tr("Application"),
                "window_size": {"width": 800, "height": 600}
            }
            self.setWindowTitle(self.config["window_title"])
            self.resize(
                self.config["window_size"]["width"],
                self.config["window_size"]["height"]
            )
    
    def setupUi(self):
        """Configurar la interfaz de usuario"""
        # Intentar importar la UI personalizada
        try:
            from .main_ui import Ui_MainWindow
            ui = Ui_MainWindow()
            print(self.tr("Loading custom UI from main_ui.py"))
        except ImportError:
            # Si no existe, usar la UI de demo
            from .main_demo_ui import DemoUI
            ui = DemoUI()
            print(self.tr("Loading demo UI"))
        
        # Configurar la UI
        ui.setupUi(self)
