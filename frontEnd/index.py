from flask import *
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker
from passlib.hash import sha256_crypt
import subprocess
engine = create_engine("mysql+pymysql://root:Be@verW0rks@localhost/register")
                        #mysql+pymysql//username:password@localhost/databasename)
db = scoped_session(sessionmaker(bind=engine))
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

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        secure_password = sha256_crypt.encrypt(str(password))
        if password == confirm:
            db.execute("INSERT INTO users(name, username, password) VALUES(:name,username,password)",
                       {"name":name,"username":username,"password":secure_password})
            db.commit()
            return redirect(url_for('login'))
        else:
            return render_template("register.html")

    return render_template("register.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("name")
        password = request.form.get("password")

        usernamedata = db.execute("SELECT username FROM users WHERE username=:username",{"username":username}).fetchone()
        passworddata = db.execute("SELECT password FROM users WHERE username=:username",{"username":username}).fetchone()

        if usernamedata is None:
            return render_template("frontEnd/login/login.html")
        else:
            for password_data in passworddata:
                if sha256_crypt.verify(password,password_data):
                    return render_template("dashboard.html")
                else:
                    return render_template("frontEnd/login/login.html")
        #query the database to find login information
    return render_template("frontEnd/login/login.html")
@app.route("/statistics")
def statistics():
    return render_template("subpages/statistics.html")

@app.route("/autismResources")
def autismResources():
    return redirect("https://www.autismspeaks.org/resource-guide")

@app.route("/session/<category>")
def session(category=""):
    subprocess.Popen(["python", "../BeaverWorks-Team-166/backEnd/chat/chilicooked.py", category], 0)
    return render_template("subpages/startSession.html")
    

if __name__ == "__main__":
    app.run()