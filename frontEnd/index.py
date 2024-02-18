from flask import *;

app = Flask(__name__, template_folder="../frontEnd", static_folder="../frontEnd")

@app.route("/")
def index():
    return render_template("index.html");

if __name__ == "__main__":
    app.run(debug=True)