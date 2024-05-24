from flask import Flask
from flask_cors import CORS

#Web Servivces
from ws.api_pdf import ws_pdf
from ws.api_prueba import ws_prueba


app = Flask(__name__)
CORS(app)


#Registrar los módulos que contienen a los servicios web
app.register_blueprint(ws_pdf)
app.register_blueprint(ws_prueba)



@app.route("/")
def index():
    return "Servicios web en ejecución"


if __name__ == "__main__":
    app.run(debug=True)