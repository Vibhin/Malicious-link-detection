from flask import Flask, render_template, flash, redirect, url_for, request
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required

import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
import model as md
import requests
import ipinfo
import socket
from pprint import pprint

app = Flask(__name__)
app.config['SECRET_KEY'] = "f548afcdab7da076d52652d8a7c9bf81"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"

model = pickle.load(open('model.pkl', 'rb'))  
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

api_token = "e55bc9f614e02b"
handler = ipinfo.getHandler(api_token)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Dataset(db.Model):
    s_no = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(1, 40), nullable=False)
    label = db.Column(db.String(3, 4), nullable=False)

    def __repr__(self):
        return f"Dataset('{self.url}', '{self.label}')"

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("test"))

    form = RegistrationForm()

    #print(form.username.data, form.validate_on_submit(), form.is_submitted(), form.validate(), form.errors)

    if form.validate_on_submit():
        #print(form.validate_on_submit)
        
        _user = User.query.filter_by(username=form.username.data).first()
        _email = User.query.filter_by(email=form.email.data).first()
        
        if _user == None and _email != None:
            flash("Email ID already exist!", "info")
        
        elif _email == None and _user != None:
            flash("Username already exist!", "info")

        elif _user != None and _email != None:
            flash("Username and Email ID already exist!", "info")

        else:
            user = User(username=form.username.data, email=form.email.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()

            flash("Your account has been created Successfully!", "success")
            return redirect(url_for("login"))
    
    #else:
    #    print(form.errors)

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("test"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        _password = User.query.filter_by(password=form.password.data).first()

        if user and _password:
            login_user(user, remember=False)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("test"))
        
        else:
            flash('Login Unsuccessful. Please check Email and Password', 'danger')
    
    #else:
    #    print(form.errors)

    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash("Logged Out successfully!.", "success")
    return redirect(url_for("home"))

@app.route("/account")
@login_required
def account():
    return render_template("account.html")


@app.route("/test")
@login_required
def test():

    print(current_user.email)

    return render_template("test.html", prediction=None)

@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    
    prediction = ""
    input_url = request.form.get("URL")
    https_flag = False

    print(request.form.get("URL"), current_user.email)

    
    if "https://" in input_url:
        https_flag = True
    
    input_url = input_url.replace("https://", "").strip()
    input_url = input_url.replace("www.", "").strip()
    input_url = input_url.replace("http://", "").strip()

    print(str(input_url + "/").split())

    X_predict = md.vectorizer.transform(str(input_url + "/").split())
    prediction = model.predict(X_predict)

    print(prediction)

    inp_url = input_url
    certificate_report = "Certificate expired"

    try:
      
      response = requests.get(request.form.get("URL"))
      certificate_report = "Certificate is Verified"

    except Exception as e:
      certificate_report = "Certificate expired"
    
    finally:
        print(input_url, https_flag, certificate_report)

        
        return render_template("test.html", prediction=prediction[0], https_status=https_flag, certificate=certificate_report)

@app.route("/modify", methods=["GET", "POST"])
@login_required
def modify():
    values = request.form
    print(values)

    if current_user.email.split("@")[-1] == "rmkec.ac.in":

        if values.get("Add") and values.get("URL"):
            if values.get("label") == "":
                flash("Please specify the label", "danger")
            
            else:
                if "https://" in values.get("URL"):
                    input_url = values.get("URL").replace("https://www.", " ").strip() + "/"
        
                if "http://" in values.get("URL"):
                    input_url = values.get("URL").replace("http://www.", " ").strip() + "/"
                
                data = Dataset(url=input_url, label=values.get("label").lower())
                db.session.add(data)
                db.session.commit()

                flash("Added to Database successfully!", "success")

        elif values.get("Remove") and values.get("URL"):
            if values.get("label") == "":
                flash("Please specify the label", "danger")
            
            else:
                if "https://" in values.get("URL"):
                    input_url = values.get("URL").replace("https://www.", " ").strip() + "/"
        
                if "http://" in values.get("URL"):
                    input_url = values.get("URL").replace("http://www.", " ").strip() + "/"

                data = Dataset.query.filter_by(url=input_url, label=values.get("label").lower()).first()

                if data == None:
                    flash("Website you entered is not in the database, Please Add to the databse First!", "danger")

                else:
                    db.session.delete(data)
                    db.session.commit()

                    flash("Removed from Database successfully!", "success")
            
        #elif values.get("URL") == "":
        #    flash("Enter the URL first!", "danger")
    
    else:
        flash("You should be a admin to modify database!", "danger")

        return redirect(url_for("test"))

    return render_template("modify.html")

@app.route("/get_details", methods=["GET", "POST"])
@login_required
def get_details():

    print(current_user.email)

    return render_template("get_details.html")


@app.route("/details", methods=["GET", "POST"])
@login_required
def url_details():
    inp_url = request.form.get("URL")

    inp_url = inp_url.replace("https://", "").strip()
    inp_url = inp_url.replace("www.", "").strip()
    inp_url = inp_url.replace("http://", "").strip()


    infolist = socket.getaddrinfo(inp_url, port=80)
    ip_address = infolist[-1][-1][0]

    details = handler.getDetails(infolist[-1][-1][0])

    #print(ip_address)
    print(inp_url)
    pprint(details.all)

    return render_template("details.html", details=details)
    
if __name__ == "__main__":
    app.run(debug=True)