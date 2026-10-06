from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.secret_key = "campus_lost_found_secret_key"


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///campuslostfound.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ============================================================
# DATABASE MODELS
# ============================================================

class LostItem(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    item_name = db.Column(db.String(100), nullable=False)

    category = db.Column(db.String(50), nullable=False)

    location = db.Column(db.String(100), nullable=False)

    description = db.Column(db.Text, nullable=False)

    phone = db.Column(db.String(20), nullable=False)

    email = db.Column(db.String(100), nullable=False)


class FoundItem(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    item_name = db.Column(db.String(100), nullable=False)

    category = db.Column(db.String(50), nullable=False)

    location = db.Column(db.String(100), nullable=False)

    description = db.Column(db.Text, nullable=False)

    phone = db.Column(db.String(20), nullable=False)

    email = db.Column(db.String(100), nullable=False)


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    fullname = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    # Get recent lost reports
    recent_lost = LostItem.query.order_by(
        LostItem.id.desc()
    ).limit(3).all()

    # Get recent found reports
    recent_found = FoundItem.query.order_by(
        FoundItem.id.desc()
    ).limit(3).all()

    # Combine both types
    all_reports = []

    for item in recent_lost:
        all_reports.append({
            "status": "Lost",
            "item_name": item.item_name,
            "location": item.location,
            "id": item.id
        })

    for item in recent_found:
        all_reports.append({
            "status": "Found",
            "item_name": item.item_name,
            "location": item.location,
            "id": item.id
        })

    # Sort and keep only 3 reports
    all_reports = sorted(
        all_reports,
        key=lambda x: x["id"],
        reverse=True
    )[:3]

    return render_template(
        "home.html",
        reports=all_reports
    )
# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form.get("fullname", "").strip()

        email = request.form.get("email", "").strip()

        password = request.form.get("password", "")


        # Check empty fields

        if not fullname or not email or not password:

            return render_template(
                "register.html",
                error="Please fill all fields."
            )


        # Check if email already exists

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:

            return render_template(
                "register.html",
                error="Email already registered."
            )


        # Create new user

        hashed_password = generate_password_hash(password)

        new_user = User(

            fullname=fullname,

            email=email,

            password=hashed_password

        )


        db.session.add(new_user)

        db.session.commit()


        return redirect(url_for("login"))


    return render_template("register.html")


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()

        password = request.form.get("password", "")


        user = User.query.filter_by(email=email).first()


        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id

            session["user_name"] = user.fullname

            return redirect(url_for("home"))


        return render_template(

            "login.html",

            error="Invalid email or password."

        )


    return render_template("login.html")


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    # User must be logged in

    if "user_id" not in session:

        return redirect(url_for("login"))


    user_id = session["user_id"]


    # Get only this user's reports

    lost_items = LostItem.query.filter_by(
        user_id=user_id
    ).all()


    found_items = FoundItem.query.filter_by(
        user_id=user_id
    ).all()


    return render_template(

        "dashboard.html",

        lost_items=lost_items,

        found_items=found_items

    )


# ============================================================
# REPORT LOST ITEM
# ============================================================

@app.route("/report-lost", methods=["GET", "POST"])
def report_lost():

    if "user_id" not in session:

        return redirect(url_for("login"))


    if request.method == "POST":

        new_report = LostItem(

            user_id=session["user_id"],

            item_name=request.form.get("item_name", "").strip(),

            category=request.form.get("category", "").strip(),

            location=request.form.get("location", "").strip(),

            description=request.form.get("description", "").strip(),

            phone=request.form.get("phone", "").strip(),

            email=request.form.get("email", "").strip()

        )


        db.session.add(new_report)

        db.session.commit()


        return render_template(

            "report_lost.html",

            success=True

        )


    return render_template("report_lost.html")


# ============================================================
# REPORT FOUND ITEM
# ============================================================

@app.route("/report-found", methods=["GET", "POST"])
def report_found():

    if "user_id" not in session:

        return redirect(url_for("login"))


    if request.method == "POST":

        new_report = FoundItem(

            user_id=session["user_id"],

            item_name=request.form.get("item_name", "").strip(),

            category=request.form.get("category", "").strip(),

            location=request.form.get("location", "").strip(),

            description=request.form.get("description", "").strip(),

            phone=request.form.get("phone", "").strip(),

            email=request.form.get("email", "").strip()

        )


        db.session.add(new_report)

        db.session.commit()


        return render_template(

            "report_found.html",

            success=True

        )


    return render_template("report_found.html")


# ============================================================
# SEARCH
# ============================================================

@app.route("/search", methods=["GET", "POST"])
def search():

    reports = []


    if request.method == "POST":

        query = request.form.get("query", "").strip()


        if query:

            search_term = f"%{query}%"


            # ------------------------------------------------
            # SEARCH LOST ITEMS
            # ------------------------------------------------

            lost_items = LostItem.query.filter(

                (LostItem.item_name.ilike(search_term)) |

                (LostItem.category.ilike(search_term)) |

                (LostItem.location.ilike(search_term)) |

                (LostItem.description.ilike(search_term))

            ).all()


            for item in lost_items:

                reports.append({

                    "status": "Lost",

                    "item_name": item.item_name,

                    "category": item.category,

                    "location": item.location,

                    "description": item.description,

                    "phone": item.phone,

                    "email": item.email

                })


            # ------------------------------------------------
            # SEARCH FOUND ITEMS
            # ------------------------------------------------

            found_items = FoundItem.query.filter(

                (FoundItem.item_name.ilike(search_term)) |

                (FoundItem.category.ilike(search_term)) |

                (FoundItem.location.ilike(search_term)) |

                (FoundItem.description.ilike(search_term))

            ).all()


            for item in found_items:

                reports.append({

                    "status": "Found",

                    "item_name": item.item_name,

                    "category": item.category,

                    "location": item.location,

                    "description": item.description,

                    "phone": item.phone,

                    "email": item.email

                })


    return render_template(

        "search.html",

        reports=reports

    )


# ============================================================
# EDIT LOST ITEM
# ============================================================

@app.route("/edit-lost/<int:id>", methods=["GET", "POST"])
def edit_lost(id):

    if "user_id" not in session:

        return redirect(url_for("login"))


    item = LostItem.query.get_or_404(id)


    # Make sure the report belongs to logged-in user

    if item.user_id != session["user_id"]:

        return "Unauthorized", 403


    if request.method == "POST":

        item.item_name = request.form.get(
            "item_name", ""
        ).strip()


        item.category = request.form.get(
            "category", ""
        ).strip()


        item.location = request.form.get(
            "location", ""
        ).strip()


        item.description = request.form.get(
            "description", ""
        ).strip()


        item.phone = request.form.get(
            "phone", ""
        ).strip()


        item.email = request.form.get(
            "email", ""
        ).strip()


        db.session.commit()


        return redirect(url_for("dashboard"))


    return render_template(

        "edit_report.html",

        item=item,

        report_type="Lost"

    )


# ============================================================
# EDIT FOUND ITEM
# ============================================================

@app.route("/edit-found/<int:id>", methods=["GET", "POST"])
def edit_found(id):

    if "user_id" not in session:

        return redirect(url_for("login"))


    item = FoundItem.query.get_or_404(id)


    # Make sure the report belongs to logged-in user

    if item.user_id != session["user_id"]:

        return "Unauthorized", 403


    if request.method == "POST":

        item.item_name = request.form.get(
            "item_name", ""
        ).strip()


        item.category = request.form.get(
            "category", ""
        ).strip()


        item.location = request.form.get(
            "location", ""
        ).strip()


        item.description = request.form.get(
            "description", ""
        ).strip()


        item.phone = request.form.get(
            "phone", ""
        ).strip()


        item.email = request.form.get(
            "email", ""
        ).strip()


        db.session.commit()


        return redirect(url_for("dashboard"))


    return render_template(

        "edit_report.html",

        item=item,

        report_type="Found"

    )


# ============================================================
# DELETE LOST ITEM
# ============================================================

@app.route("/delete-lost/<int:id>")
def delete_lost(id):

    if "user_id" not in session:

        return redirect(url_for("login"))


    item = LostItem.query.get_or_404(id)


    # Make sure user owns this report

    if item.user_id != session["user_id"]:

        return "Unauthorized", 403


    db.session.delete(item)

    db.session.commit()


    return redirect(url_for("dashboard"))


# ============================================================
# DELETE FOUND ITEM
# ============================================================

@app.route("/delete-found/<int:id>")
def delete_found(id):

    if "user_id" not in session:

        return redirect(url_for("login"))


    item = FoundItem.query.get_or_404(id)


    # Make sure user owns this report

    if item.user_id != session["user_id"]:

        return "Unauthorized", 403


    db.session.delete(item)

    db.session.commit()


    return redirect(url_for("dashboard"))


# ============================================================
# TEST ROUTE
# ============================================================

@app.route("/test")
def test():

    return str(session)


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    with app.app_context():

        db.create_all()


    app.run(debug=True)