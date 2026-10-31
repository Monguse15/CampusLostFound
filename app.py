
import os
from datetime import datetime

from flask import (
    Flask, render_template, request,
    redirect, url_for, session
)

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import (
    generate_password_hash, check_password_hash
)


app = Flask(__name__)

# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "dev-only-change-this-secret-key"
)



# ============================================================
# DATABASE CONFIGURATION
# ============================================================

database_url = os.environ.get("DATABASE_URL")

if database_url:
    # Use Neon PostgreSQL on Render
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql+psycopg://",
            1
        )
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

else:
    # Use SQLite locally in VS Code
    os.makedirs(app.instance_path, exist_ok=True)

    database_path = os.path.join(
        app.instance_path,
        "campuslostfound.db"
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + database_path.replace("\\", "/")
    )

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)




# ============================================================
# DATABASE MODELS
# ============================================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


class LostItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)


class FoundItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    recipient_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    item_type = db.Column(db.String(10), nullable=False)
    item_id = db.Column(db.Integer, nullable=False)

    message = db.Column(db.String(255), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    is_read = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    sender = db.relationship(
        "User",
        foreign_keys=[sender_id]
    )

    recipient = db.relationship(
        "User",
        foreign_keys=[recipient_id]
    )


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

with app.app_context():
    db.create_all()


# ============================================================
# HELPER FUNCTION: GET ITEM
# ============================================================

def get_item(item_type, item_id):

    if item_type == "lost":
        return LostItem.query.get_or_404(item_id)

    elif item_type == "found":
        return FoundItem.query.get_or_404(item_id)

    else:
        return None


# ============================================================
# GLOBAL NOTIFICATION COUNT
# ============================================================

@app.context_processor
def notification_count():

    unread_count = 0

    if "user_id" in session:

        unread_count = Notification.query.filter_by(
            recipient_id=session["user_id"],
            is_read=False
        ).count()

    return {
        "unread_notifications": unread_count
    }


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    recent_lost = LostItem.query.order_by(
        LostItem.id.desc()
    ).limit(18).all()

    recent_found = FoundItem.query.order_by(
        FoundItem.id.desc()
    ).limit(18).all()

    return render_template(
        "home.html",
        recent_lost=recent_lost,
        recent_found=recent_found
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

        if not fullname or not email or not password:
            return render_template(
                "register.html",
                error="Please fill all fields."
            )

        if len(password) < 6:
            return render_template(
                "register.html",
                error="Password must contain at least 6 characters."
            )

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            return render_template(
                "register.html",
                error="Email already registered."
            )

        new_user = User(
            fullname=fullname,
            email=email,
            password=generate_password_hash(password)
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

            session.clear()
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

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    lost_items = LostItem.query.filter_by(
        user_id=user_id
    ).order_by(LostItem.id.desc()).all()

    found_items = FoundItem.query.filter_by(
        user_id=user_id
    ).order_by(FoundItem.id.desc()).all()

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

        item_name = request.form.get("item_name", "").strip()
        category = request.form.get("category", "").strip()
        location = request.form.get("location", "").strip()
        description = request.form.get("description", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()

        if not item_name:
            return render_template(
                "report_lost.html",
                error="Item name is required."
            ), 400

        if not phone.isascii() or not phone.isdigit() or len(phone) != 10:
            return render_template(
                "report_lost.html",
                error="Please enter a valid 10-digit phone number."
            ), 400

        new_report = LostItem(
            user_id=session["user_id"],
            item_name=item_name,
            category=category,
            location=location,
            description=description,
            phone=phone,
            email=email
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

        item_name = request.form.get("item_name", "").strip()
        category = request.form.get("category", "").strip()
        location = request.form.get("location", "").strip()
        description = request.form.get("description", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()

        if not item_name:
            return render_template(
                "report_found.html",
                error="Item name is required."
            ), 400

        if not phone.isascii() or not phone.isdigit() or len(phone) != 10:
            return render_template(
                "report_found.html",
                error="Please enter a valid 10-digit phone number."
            ), 400

        new_report = FoundItem(
            user_id=session["user_id"],
            item_name=item_name,
            category=category,
            location=location,
            description=description,
            phone=phone,
            email=email
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

            lost_items = LostItem.query.filter(
                (LostItem.item_name.ilike(search_term)) |
                (LostItem.category.ilike(search_term)) |
                (LostItem.location.ilike(search_term)) |
                (LostItem.description.ilike(search_term))
            ).all()

            for item in lost_items:

                reports.append({
                    "id": item.id,
                    "type": "lost",
                    "status": "Lost",
                    "item_name": item.item_name,
                    "category": item.category,
                    "location": item.location,
                    "description": item.description
                })

            found_items = FoundItem.query.filter(
                (FoundItem.item_name.ilike(search_term)) |
                (FoundItem.category.ilike(search_term)) |
                (FoundItem.location.ilike(search_term)) |
                (FoundItem.description.ilike(search_term))
            ).all()

            for item in found_items:

                reports.append({
                    "id": item.id,
                    "type": "found",
                    "status": "Found",
                    "item_name": item.item_name,
                    "category": item.category,
                    "location": item.location,
                    "description": item.description
                })

    return render_template(
        "search.html",
        reports=reports
    )


# ============================================================
# INDIVIDUAL ITEM DETAILS
# ============================================================

@app.route("/item/<item_type>/<int:item_id>")
def item_details(item_type, item_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    item = get_item(item_type, item_id)

    if item is None:
        return "Invalid item type", 404

    already_responded = False

    if item.user_id != session["user_id"]:

        already_responded = Notification.query.filter_by(
            recipient_id=item.user_id,
            sender_id=session["user_id"],
            item_type=item_type,
            item_id=item_id
        ).first() is not None

    return render_template(
        "item_details.html",
        item=item,
        item_type=item_type,
        already_responded=already_responded
    )


# ============================================================
# RESPOND TO AN ITEM
# ============================================================

@app.route(
    "/respond/<item_type>/<int:item_id>",
    methods=["POST"]
)
def respond_to_item(item_type, item_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    item = get_item(item_type, item_id)

    if item is None:
        return "Invalid item type", 404

    sender_id = session["user_id"]

    if item.user_id == sender_id:
        return "You cannot respond to your own report.", 403

    existing_notification = Notification.query.filter_by(
        recipient_id=item.user_id,
        sender_id=sender_id,
        item_type=item_type,
        item_id=item_id
    ).first()

    if existing_notification:
        return redirect(
            url_for(
                "item_details",
                item_type=item_type,
                item_id=item_id
            )
        )

    if item_type == "lost":
        message = "Someone says they found your lost item!"
    else:
        message = "Someone thinks this found item belongs to them!"

    notification = Notification(
        recipient_id=item.user_id,
        sender_id=sender_id,
        item_type=item_type,
        item_id=item_id,
        message=message
    )

    db.session.add(notification)
    db.session.commit()

    return redirect(
        url_for(
            "item_details",
            item_type=item_type,
            item_id=item_id
        )
    )


# ============================================================
# NOTIFICATIONS PAGE
# ============================================================

@app.route("/notifications")
def notifications():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_notifications = Notification.query.filter_by(
        recipient_id=session["user_id"]
    ).order_by(
        Notification.created_at.desc()
    ).all()

    return render_template(
        "notifications.html",
        notifications=user_notifications
    )


# ============================================================
# OPEN NOTIFICATION
# ============================================================

@app.route("/notification/<int:notification_id>")
def open_notification(notification_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    notification = Notification.query.get_or_404(
        notification_id
    )

    if notification.recipient_id != session["user_id"]:
        return "Unauthorized", 403

    notification.is_read = True
    db.session.commit()

    return redirect(
        url_for(
            "item_details",
            item_type=notification.item_type,
            item_id=notification.item_id
        )
    )


# ============================================================
# EDIT LOST ITEM
# ============================================================

@app.route("/edit-lost/<int:id>", methods=["GET", "POST"])
def edit_lost(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    item = LostItem.query.get_or_404(id)

    if item.user_id != session["user_id"]:
        return "Unauthorized", 403

    if request.method == "POST":

        item.item_name = request.form.get("item_name", "").strip()
        item.category = request.form.get("category", "").strip()
        item.location = request.form.get("location", "").strip()
        item.description = request.form.get("description", "").strip()
        item.phone = request.form.get("phone", "").strip()
        item.email = request.form.get("email", "").strip()

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

    if item.user_id != session["user_id"]:
        return "Unauthorized", 403

    if request.method == "POST":

        item.item_name = request.form.get("item_name", "").strip()
        item.category = request.form.get("category", "").strip()
        item.location = request.form.get("location", "").strip()
        item.description = request.form.get("description", "").strip()
        item.phone = request.form.get("phone", "").strip()
        item.email = request.form.get("email", "").strip()

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

@app.route("/delete-lost/<int:id>", methods=["POST"])
def delete_lost(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    item = LostItem.query.get_or_404(id)

    if item.user_id != session["user_id"]:
        return "Unauthorized", 403

    Notification.query.filter_by(
        item_type="lost",
        item_id=item.id
    ).delete()

    db.session.delete(item)
    db.session.commit()

    return redirect(url_for("dashboard"))


# ============================================================
# DELETE FOUND ITEM
# ============================================================

@app.route("/delete-found/<int:id>", methods=["POST"])
def delete_found(id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    item = FoundItem.query.get_or_404(id)

    if item.user_id != session["user_id"]:
        return "Unauthorized", 403

    Notification.query.filter_by(
        item_type="found",
        item_id=item.id
    ).delete()

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
    app.run(debug=True)
