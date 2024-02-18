from flask import *;

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/account")
def account():
    return render_template("account.html")

@app.route("/history")
def history():
    return render_template("subpages/history.html")

@app.route("/settings")
def settings():
    return render_template("subpages/settings.html")

@app.route("/startSession")
def startSession():
    return render_template("subpages/startSession.html")

@app.route("/statistics")
def statistics():
    return render_template("subpages/statistics.html")

@app.route("/autismResources")
def autismResources():
    return redirect("https://www.autismspeaks.org/resource-guide")

if __name__ == "__main__":
    app.run()