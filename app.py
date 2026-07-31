from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from config import Config
from models import db, Record
from rapidfuzz import fuzz
import csv
import io

app = Flask(__name__)

app.secret_key = "cadet_management_system"

app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


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

    duplicate_emails = (
        db.session.query(Record.email)
        .group_by(Record.email)
        .having(db.func.count(Record.email) > 1)
        .count()
    )

    duplicate_phones = (
        db.session.query(Record.phone)
        .group_by(Record.phone)
        .having(db.func.count(Record.phone) > 1)
        .count()
    )

    duplicates = duplicate_emails + duplicate_phones

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

    return render_template(
        "dashboard.html",
        total_records=total_records,
        duplicates=duplicates,
        accuracy=accuracy,
        recent_records=recent_records,
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

        # Name Similarity

        if force != "yes":

            all_records = Record.query.all()

            for record in all_records:

                similarity = fuzz.token_sort_ratio(

                    name.lower(),

                    record.name.lower()

                )

                if similarity >= 80:

                    return render_template(

                        "duplicate_warning.html",

                        existing=record,

                        similarity=round(similarity),

                        new_name=name,

                        new_email=email,

                        new_phone=phone,

                        new_department=department

                    )

        new_record = Record(

            name=name,

            email=email,

            phone=phone,

            department=department

        )

        db.session.add(new_record)

        db.session.commit()

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
# REPORTS
# =========================

@app.route("/reports")
def reports():

    records = Record.query.all()

    return render_template(

        "reports.html",

        records=records

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
    app.run(debug=True)