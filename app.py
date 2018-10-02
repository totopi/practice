from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def welcome():
    return render_template('index.html')

if __name__ == "__main_":
    app.run(debug=True)