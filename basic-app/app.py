from flask import Flask, Response
import json

app = Flask(__name__)

random_string = "e"

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/healthz")
def healthz():
    return Response("{'status':'ok'}", status=200, mimetype='application/json')

def generate_test_response():
    response = {"fail":"false"}
    return response

@app.route("/test")
def test_app():
    response = generate_test_response()
    resp_json = json.dumps(response)
    return Response(resp_json, status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080)