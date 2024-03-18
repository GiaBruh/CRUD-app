from bcolors import bcolors as bgc
from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime
from datetime import date
from forms import ModalForm, TestForm, LoginForm, RegisterForm
from flask_bootstrap import Bootstrap

db = SQLAlchemy()


class UserModel(db.Model):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    email = Column(String(35), nullable=False, unique=True)
    password = Column(String(100), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}', email='{self.email}')>"


class EmployeeModel(db.Model):
    __tablename__ = "employees"  # More descriptive table name

    employee_id = Column(String(100), primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)  # Specify max length and not nullable
    dob = Column(DateTime, nullable=False)  # Not nullable
    email = Column(String(255), nullable=False, unique=True)  # Unique email constraint
    phone_number = Column(String(15), nullable=False)
    department = Column(String(255), nullable=False)

    def __init__(self, name, dob, email, phone_number, department):
        self.name = name
        self.dob = dob
        self.email = email
        self.phone_number = phone_number
        self.department = department

    def __repr__(self):
        return f"<Employee(employee_id={self.employee_id}, name='{self.name}', dob='{self.dob.isoformat()}', email='{self.email}', phone_number='{self.phone_number}',department='{self.department}')>"

    def calculate_age(self):
        """Calculates age based on the date of birth."""
        today = date.today()
        birthyear = self.dob.year
        return (
            today.year
            - birthyear
            - ((today.month, today.day) < (self.dob.month, self.dob.day))
        )

    @property
    def age(self):
        """Property to access calculated age without modifying the model."""
        return self.calculate_age()


app = Flask(__name__)
app.config["SECRET_KEY"] = "fatcock"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://giabuu:11122003@localhost/test_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
Bootstrap(app)


@app.route("/form", methods=["GET", "POST"])
def form():
    name = None
    test_form = TestForm()
    if test_form.validate_on_submit():
        name = test_form.name.data
        test_form.name.data = ""
    return render_template("form.html", form=test_form, name=name)


@app.route("/list", methods=["GET", "POST"])
def employee_list():
    return_list = db.session.execute(
        db.select(EmployeeModel).order_by(EmployeeModel.employee_id)
    ).scalars()

    form = ModalForm()
    if form.validate_on_submit():
        name = form.name.data
        dob = form.dob.data
        email = form.email.data
        phone_number = form.phone_number.data
        department = form.department.data
        emp = EmployeeModel(name, dob, email, phone_number, department)
        db.session.add(emp)
        db.session.commit()
        return render_template("list.html", employees=return_list, form=form)
    return render_template("list.html", employees=return_list, form=form)


# TODO: create new employee
# @app.route("/list/create", methods=["GET", "POST"])
# def create():
#     if request.method == "GET":
#         return render_template("list.html")

#     if request.method == "POST":
#         return redirect("/list")


# TODO: update existed employee
@app.route("/list/update")
def update(): ...


# TODO: delete existed employee
@app.route("/list/delete")
def delete(): ...


def get_user(username: str, password: str):
    user = db.one_or_404(
        db.select(UserModel).filter_by(username=username, password=password)
    )
    return user


@app.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm() 
    if  request.method == "POST":
        username = login_form.username.data
        password = login_form.password.data
        user = get_user(username, password)
        if user is not None:
            session['username'] = username
            return redirect(url_for("home"))
    return render_template("login.html", form=login_form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST":  # TODO: If I add 'form.validate()' this shit will stop working 
        user = UserModel(form.username.data, form.email.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Thanks for registering")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for("login"))
    
@app.route("/")
@app.route("/home")
def home():
    if 'username' in session:  
        return render_template("home.html", user=session['username'])
    return redirect(url_for("login")) 


# @app.route("/list")
# def list():
#     return_list = (get_employees())
#     print(bgc.WARNING + str(type(return_list)) + bgc.ENDC)
#     return render_template("list.html", employees=(return_list))


@app.before_request
def create_table():
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    create_table()
    app.run(host="localhost", port=5000, debug=True)
