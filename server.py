from waitress import serve
from main_folder import menuapp

serve(menuapp.app, host='127.0.0.1', port=5000)
