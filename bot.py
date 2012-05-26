from flask import Flask, request, render_template, redirect

app = Flask(__name__)
@app.route("/", methods=['POST',])
def index():
    print dir(request)
    print request.json
    return request.json

if __name__ == "__main__":
    app.run()
