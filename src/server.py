# src/server.py
from flask import Flask, send_from_directory
from flask_socketio import SocketIO
import os
import eventlet

def start_server(serial_handler):
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__),'static'))
    socketio = SocketIO(app)

    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    @socketio.on('connect')
    def handle_connect():
        print('Cliente conectado')

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Cliente desconectado')

    def read_and_emit_data():
        while True:
            data = serial_handler.get_data(use_demo_data=False)
            socketio.emit('ecg_data', {'data': data})
            eventlet.sleep(0.01)  # Asegúrate de que 'eventlet' esté disponible

    # Iniciar la tarea en segundo plano
    socketio.start_background_task(target=read_and_emit_data)

    # Ejecutar el servidor
    socketio.run(app, host='0.0.0.0', port=5000)
