from flask import Flask, render_template, request, redirect
from database import get_hosts, set_name, init_db

app = Flask(__name__)

@app.route("/")
def index():
    hosts = get_hosts()
    return render_template("index.html", hosts=hosts)

@app.route("/rename", methods=["POST"])
def rename():
    ip = request.form["ip"]
    name = request.form["name"]
    set_name(ip, name)
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
