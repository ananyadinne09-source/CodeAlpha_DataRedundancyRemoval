from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from config import Config
from models import db, Record
from rapidfuzz import fuzz
import csv
import io
import os

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


# =========================
# AI DUPLICATE ASSISTANT CONFIG
# =========================

# Any name-similarity match at or above this percentage is flagged by
# the AI assistant and routed to the administrator for a decision.
DUPLICATE_SIMILARITY_THRESHOLD = 75


# =========================
# LOGIN
# =========================

@app.route("/")
def login():
    return render_template("login.html")


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    total_records = Record.query.count()

    # Records the AI Duplicate Assistant flagged (>= threshold similarity)
    # and that the administrator chose to register anyway.
    duplicates = Record.query.filter_by(is_duplicate=True).count()

    if total_records == 0:
        accuracy = 100
    else:
        accuracy = round(
            ((total_records - duplicates) / total_records) * 100
        )

    recent_records = (
        Record.query
        .order_by(Record.created_at.desc())
        .limit(5)
        .all()
    )

    battalion_data = (
        db.session.query(
            Record.department,
            db.func.count(Record.id)
        )
        .group_by(Record.department)
        .all()
    )

    battalion_labels = [row[0] for row in battalion_data]
    battalion_counts = [row[1] for row in battalion_data]

    recent_duplicates = (
        Record.query
        .filter_by(is_duplicate=True)
        .order_by(Record.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard.html",
        total_records=total_records,
        duplicates=duplicates,
        accuracy=accuracy,
        recent_records=recent_records,
        recent_duplicates=recent_duplicates,
        battalion_labels=battalion_labels,
        battalion_counts=battalion_counts
    )


# =========================
# ADD RECORD
# =========================

@app.route("/add", methods=["GET", "POST"])
def add_record():

    if request.method == "POST":

        name = request.form["name"].strip()

        email = request.form["email"].strip()

        phone = request.form["phone"].strip()

        department = request.form["department"].strip()

        force = request.form.get("force")

        # Phone Validation

        if len(phone) != 10 or not phone.isdigit():

            flash("Phone number must contain exactly 10 digits.", "danger")

            return redirect(url_for("add_record"))

        if phone[0] not in ["6", "7", "8", "9"]:

            flash("Enter a valid Indian mobile number.", "danger")

            return redirect(url_for("add_record"))

        # Exact duplicate

        existing = Record.query.filter(

            (Record.email == email) |

            (Record.phone == phone)

        ).first()

        if existing:

            flash("Email or Phone Number already exists.", "danger")

            return redirect(url_for("add_record"))

        # AI Duplicate Assistant — name similarity scan

        flagged_id = request.form.get("flagged_duplicate_id")

        flagged_score = request.form.get("flagged_similarity")

        if force != "yes":

            all_records = Record.query.all()

            best_match = None

            best_score = 0

            for record in all_records:

                similarity = fuzz.token_sort_ratio(

                    name.lower(),

                    record.name.lower()

                )

                if similarity >= DUPLICATE_SIMILARITY_THRESHOLD and similarity > best_score:

                    best_match = record

                    best_score = similarity

            if best_match:

                return render_template(

                    "duplicate_warning.html",

                    existing=best_match,

                    similarity=round(best_score),

                    threshold=DUPLICATE_SIMILARITY_THRESHOLD,

                    new_name=name,

                    new_email=email,

                    new_phone=phone,

                    new_department=department

                )

        # Administrator confirmed "Register Anyway" on an AI-flagged match

        is_duplicate = force == "yes" and flagged_score is not None

        new_record = Record(

            name=name,

            email=email,

            phone=phone,

            department=department,

            is_duplicate=is_duplicate,

            similarity_score=int(flagged_score) if is_duplicate else None,

            duplicate_of_id=int(flagged_id) if is_duplicate and flagged_id else None

        )

        db.session.add(new_record)

        db.session.commit()

        if is_duplicate:

            flash(

                f"Cadet Registered — flagged by AI Assistant as a "

                f"{flagged_score}% possible duplicate and included in the "

                f"duplicate count for administrator review.",

                "warning"

            )

        else:

            flash("Cadet Registered Successfully!", "success")

        return redirect(url_for("records"))

    return render_template("add_record.html")


# =========================
# RECORDS
# =========================

@app.route("/records")
def records():

    search = request.args.get("search")

    if search:

        records = Record.query.filter(

            (Record.name.contains(search)) |

            (Record.email.contains(search)) |

            (Record.phone.contains(search)) |

            (Record.department.contains(search))

        ).all()

    else:

        records = Record.query.all()

    return render_template(

        "records.html",

        records=records

    )


# =========================
# AI ASSISTANT — FLAGGED DUPLICATES
# =========================

@app.route("/duplicates")
def duplicates():

    flagged_records = (
        Record.query
        .filter_by(is_duplicate=True)
        .order_by(Record.created_at.desc())
        .all()
    )

    return render_template(
        "duplicates.html",
        flagged_records=flagged_records,
        threshold=DUPLICATE_SIMILARITY_THRESHOLD
    )


@app.route("/duplicates/unflag/<int:id>")
def unflag_duplicate(id):

    record = Record.query.get_or_404(id)

    record.is_duplicate = False

    record.similarity_score = None

    record.duplicate_of_id = None

    db.session.commit()

    flash(f"{record.name} has been cleared and removed from the duplicate count.", "success")

    return redirect(url_for("duplicates"))


# =========================
# REPORTS
# =========================

@app.route("/reports")
def reports():

    records = Record.query.all()

    battalion_data = (
        db.session.query(
            Record.department,
            db.func.count(Record.id)
        )
        .group_by(Record.department)
        .all()
    )

    battalion_labels = [row[0] for row in battalion_data]
    battalion_counts = [row[1] for row in battalion_data]

    flagged_count = Record.query.filter_by(is_duplicate=True).count()

    clean_count = len(records) - flagged_count

    return render_template(

        "reports.html",

        records=records,

        battalion_labels=battalion_labels,

        battalion_counts=battalion_counts,

        clean_count=clean_count,

        flagged_count=flagged_count

    )


# =========================
# DOWNLOAD CSV
# =========================

@app.route("/download_report")
def download_report():

    records = Record.query.all()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([

        "ID",

        "Cadet Name",

        "Email",

        "Phone",

        "Battalion",

        "Registered Date"

    ])

    for r in records:

        writer.writerow([

            r.id,

            r.name,

            r.email,

            r.phone,

            r.department,

            r.created_at.strftime("%d-%m-%Y")

            if r.created_at else ""

        ])

    response = make_response(output.getvalue())

    response.headers["Content-Disposition"] = "attachment; filename=Cadet_Report.csv"

    response.headers["Content-Type"] = "text/csv"

    return response


# =========================
# EDIT
# =========================

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    record = Record.query.get_or_404(id)

    if request.method == "POST":

        record.name = request.form["name"]

        record.email = request.form["email"]

        record.phone = request.form["phone"]

        record.department = request.form["department"]

        db.session.commit()

        flash("Cadet Updated Successfully!", "success")

        return redirect(url_for("records"))

    return render_template(

        "edit_record.html",

        record=record

    )


# =========================
# DELETE
# =========================

@app.route("/delete/<int:id>")
def delete(id):

    record = Record.query.get_or_404(id)

    db.session.delete(record)

    db.session.commit()

    flash("Cadet Deleted Successfully!", "success")

    return redirect(url_for("records"))


# =========================
# RUN
# =========================

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(debug=debug_mode)