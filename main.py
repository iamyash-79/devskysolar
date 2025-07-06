from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/topbar")
def topbar():
    return render_template("topbar.html")

@app.route("/bottom")
def bottom():
    return render_template("bottom.html")

if __name__ == "__main__":
    app.run(debug=True)
