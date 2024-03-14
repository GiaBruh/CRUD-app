from bcolors import bcolors as bgc
from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime
from datetime import date

db = SQLAlchemy()

class EmployeeModel(db.Model):
    __tablename__ = "employees"  # More descriptive table name

    employee_id = Column(String(100), primary_key=True)
    name = Column(String(255), nullable=False)  # Specify max length and not nullable
    dob = Column(DateTime, nullable=False)  # Not nullable
    email = Column(String(255), nullable=False, unique=True)  # Unique email constraint
    phone_number = Column(String(15), nullable=False)
    department = Column(String(255), nullable=False)

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

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://giabuu:11122003@localhost/test_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


@app.before_request
def create_table():
    with app.app_context():
        db.create_all()


@app.route("/list")
def employee_list():
    return_list = db.session.execute(
        db.select(EmployeeModel).order_by(EmployeeModel.employee_id)
    ).scalars()
    return render_template("list.html", employees=return_list)


@app.route("/list/create", methods=["GET", "POST"])
def create():
    if request.method == "GET":
        return render_template("list.html")

    if request.method == "POST":
        return redirect("/list")


@app.route("/list/update")
def update(): ...


@app.route("/list/delete")
def delete(): ...


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


# @app.route("/list")
# def list():
#     return_list = (get_employees())
#     print(bgc.WARNING + str(type(return_list)) + bgc.ENDC)
#     return render_template("list.html", employees=(return_list))


if __name__ == "__main__":
    create_table()
    app.run(host="localhost", port=5000, debug=True)
