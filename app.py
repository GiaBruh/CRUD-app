from bcolors import bcolors as bgc
from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Date
from datetime import date, timedelta
from forms import ModalForm, TestForm, LoginForm, RegisterForm
from flask_bootstrap import Bootstrap

# from flask_login import login_manager, login_required, LoginManager

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

    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)  # Specify max length and not nullable
    dob = Column(Date, nullable=False)  # Not nullable
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
app.permanent_session_lifetime = timedelta(hours=1)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://giabuu:11122003@localhost/test_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
Bootstrap(app)
# login_manager = LoginManager()


@app.route("/form", methods=["GET", "POST"])
def form():
    name = None
    test_form = TestForm()
    if test_form.validate_on_submit():
        name = test_form.name.data
        test_form.name.data = ""
    return render_template("form.html", form=test_form, name=name)


@app.route("/list", methods=["GET", "POST"])
def list():
    if "username" in session:
        return_list = db.session.execute(
            db.select(EmployeeModel).order_by(EmployeeModel.employee_id)
        ).scalars()

        form = ModalForm()
        return render_template("list.html", employees=return_list, form=form)
    return redirect(url_for("login"))


# TODO: create new employee
@app.route("/list/create", methods=["GET", "POST"])
def create():
    form = ModalForm()
    if request.method == "POST":
        fullname = form.name.data
        dob = form.dob.data
        email = form.email.data
        phone_number = form.phone_number.data
        department = form.department.data
        employee = EmployeeModel(fullname, dob, email, phone_number, department)
        db.session.add(employee)
        db.session.commit()
        flash("Employee added successfully!", "success")
    return redirect(url_for("list"))


@app.route("/list/update/<int:id>", methods=["GET", "POST"])
def update(id):
    employee = db.session.query(EmployeeModel).get(id)
    form = ModalForm(obj=employee)
    form.populate_obj(employee)
    db.session.add(employee)
    db.session.commit()
    # print(bgc.OKGREEN + "it works" + bgc.ENDC)
    flash(f'Employee #{id} updated successfully!', "success")
    return redirect(url_for("list"))


@app.route("/list/delete/<int:id>", methods=["GET", "POST"])
# @login_required
def delete(id):
    try:
        employee_to_delete = EmployeeModel.query.get_or_404(id)
        db.session.delete(employee_to_delete)
        db.session.commit()
    except:
        return redirect(url_for("list"))
    flash(f'Employee #{id} deleted successfully!', "success")
    return redirect(url_for("list"))


def get_user(username: str, password: str):
    user = db.one_or_404(
        db.select(UserModel).filter_by(username=username, password=password)
    )
    return user


@app.route("/login", methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if request.method == "POST":
        username = login_form.username.data
        password = login_form.password.data
        user = get_user(username, password)
        if user is not None:
            session.permanent = True
            session["username"] = username
            return redirect(url_for("home"))
    return render_template("login.html", form=login_form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if (
        request.method == "POST"
    ):  # TODO: If I add 'form.validate()' this shit will stop working
        user = UserModel(form.username.data, form.email.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        # flash("Thanks for registering")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/")
@app.route("/home")
def home():
    if "username" in session:
        return render_template("home.html", user=session["username"])
    return redirect(url_for("login"))


@app.before_request
def create_table():
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    create_table()
    app.run(host="localhost", port=5000, debug=True)
