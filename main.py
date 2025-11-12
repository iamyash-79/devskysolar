# ---------- main.py ----------
from flask import Flask, request, render_template, jsonify, Response, session, flash, redirect
import smtplib
import ssl
import mysql.connector
import datetime
import logging

# ---------- Config ----------
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ---------- Logging ----------
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# ---------- EMAIL SETTINGS (cPanel Mail) ----------
MAIL_HOST = "host"   # ✅ Your cPanel mail server
MAIL_PORT = 465                     # SSL Port
MAIL_USER = example@gmail.in"
MAIL_PASSWORD = "yourpassword"    # Your cPanel mail password
MAIL_FROM = MAIL_USER
MAIL_TO = "dexample@gmail.com"   # Receiver email

# ---------- MYSQL CONNECTION ----------
def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="devskyso_traffic",
        password="password",
        database="devskyso_traffic",
        autocommit=False
    )

# ---------- EMAIL SENDER ----------
def send_lead_email(subject, body_html, body_text):
    try:
        logging.info("📧 Sending lead email via cPanel...")
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(MAIL_HOST, MAIL_PORT, context=context) as server:
            server.login(MAIL_USER, MAIL_PASSWORD)
            msg = f"From: {MAIL_FROM}\nTo: {MAIL_TO}\nSubject: {subject}\nContent-Type: text/html;\n\n{body_html}"
            server.sendmail(MAIL_FROM, MAIL_TO, msg.encode("utf-8"))
        logging.info("✅ Lead email sent successfully via cPanel.")
    except Exception as e:
        logging.exception("❌ Email sending failed:")
        print("Email send error:", e)

# ---------- TRAFFIC LOGGER ----------
@app.before_request
def log_traffic():
    """Store visitor IP and timestamp once per hour."""
    try:
        conn = get_mysql_connection()
        c = conn.cursor(dictionary=True)
        ip = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        page = request.path
        now = datetime.datetime.now()
        one_hour_ago = now - datetime.timedelta(hours=1)

        c.execute("SELECT COUNT(*) AS cnt FROM visits WHERE ip=%s AND timestamp>=%s", (ip, one_hour_ago))
        row = c.fetchone()
        already_logged = row["cnt"] if row and "cnt" in row else 0

        if already_logged == 0:
            c.execute(
                "INSERT INTO visits (ip, user_agent, pages, timestamp, name, contact) VALUES (%s, %s, %s, %s, %s, %s)",
                (ip, user_agent, page, now, None, None)
            )
            conn.commit()

        c.close()
        conn.close()
    except Exception:
        logging.exception("Traffic log error:")

def get_total_visitors():
    try:
        conn = get_mysql_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM visits")
        count = c.fetchone()[0]
        c.close()
        conn.close()
        return count
    except Exception:
        logging.exception("Error fetching total visitors:")
        return 0

@app.context_processor
def inject_traffic():
    """Inject total visitors in all templates."""
    return {"total_visitors": get_total_visitors()}

# ---------- ROBOTS & SITEMAP ----------
@app.route("/robots.txt")
def robots_txt():
    content = "User-agent: *\nDisallow: /owner/\nSitemap: https://devskysolar.in/sitemap.xml"
    return Response(content, mimetype="text/plain")

@app.route("/sitemap.xml")
def sitemap():
    urls = [
        "https://devskysolar.in/",
        "https://devskysolar.in/approach",
        "https://devskysolar.in/services",
        "https://devskysolar.in/contact",
        "https://devskysolar.in/leads"
    ]
    sitemap_xml = [
        "<?xml version='1.0' encoding='UTF-8'?>",
        "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"
    ]
    for url in urls:
        sitemap_xml.append(f"  <url><loc>{url}</loc></url>")
    sitemap_xml.append("</urlset>")
    return Response("\n".join(sitemap_xml), mimetype="application/xml")

# ---------- PAGES ----------
@app.route("/")
def home():
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM faq ORDER BY category ASC, id ASC")
        faq_rows = cursor.fetchall()
        cursor.close()
        conn.close()

        faqs = {}
        for row in faq_rows:
            cat = row.get("category") or "General"
            faqs.setdefault(cat, []).append({
                "question": row.get("question", ""),
                "answer": row.get("answer", "")
            })
    except Exception:
        logging.exception("Error loading FAQs")
        faqs = {}

    return render_template(
        "index.html",
        title="We Build. You Shine.",
        subtitle="At Dev Sky Solar, we don’t just install solar panels — we build trust, empower homes, and ignite possibilities.",
        faqs=faqs
    )

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/quick")
def quick():
    return render_template("quick.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/faq")
def faq():
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM faq ORDER BY category ASC, id ASC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        faqs = {}
        for row in rows:
            cat = row.get("category") or "General"
            faqs.setdefault(cat, []).append({
                "question": row.get("question", ""),
                "answer": row.get("answer", "")
            })
    except Exception:
        logging.exception("Error loading FAQ")
        faqs = {}
    return render_template("faq.html", faqs=faqs)

@app.route("/calculator")
def calculator():
    return render_template("calculator.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/links")
def links():
    return render_template("links.html")

@app.route("/leads")
def leads():
    return render_template("leads.html")

# ---------- LEAD SUBMISSION ----------
@app.route("/submit_lead", methods=["POST"])
def submit_lead():
    company = request.form.get("company", "").strip()
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()
    kw = request.form.get("kw", "").strip()
    time_pref = request.form.get("time", "").strip()
    comments = request.form.get("comments", "").strip()

    # ✅ Basic validation
    if not name or not phone:
        return jsonify({"success": False, "message": "Name and phone number are required."})

    conn = None
    cursor = None
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)

        # ✅ Optional: prevent duplicate leads for same phone
        cursor.execute("SELECT id FROM leads WHERE phone = %s", (phone,))
        existing = cursor.fetchone()
        if existing:
            return jsonify({"success": False, "message": "This phone number already exists."})

        # ✅ Insert lead data (now includes company, no lead_type)
        cursor.execute("""
            INSERT INTO leads (name, company, phone, address, kw_required, installation_time, comments, added_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """, (name, company, phone, address, kw, time_pref, comments))
        conn.commit()

        # ✅ Prepare email content
        subject = f"New Solar Lead: {name} ({phone})"
        html_body = f"""
        <h2>🌞 New Lead Received</h2>
        <p><strong>Name:</strong> {name}</p>
        {f"<p><strong>Company:</strong> {company}</p>" if company else ""}
        <p><strong>Phone:</strong> {phone}</p>
        <p><strong>Address:</strong> {address}</p>
        <p><strong>KW Required:</strong> {kw or 'Not specified'}</p>
        <p><strong>Preferred Time:</strong> {time_pref or 'Not specified'}</p>
        <p><strong>Comments:</strong> {comments or 'None'}</p>
        <p style='color:#888;font-size:0.9em;'>Auto notification from Dev Sky Solar Website</p>
        """

        plain_body = (
            f"New Lead Received:\n"
            f"Name: {name}\n"
            + (f"Company: {company}\n" if company else "")
            + f"Phone: {phone}\n"
            f"Address: {address}\n"
            f"KW Required: {kw or 'Not specified'}\n"
            f"Preferred Time: {time_pref or 'Not specified'}\n"
            f"Comments: {comments or 'None'}"
        )

        # ✅ Send email notification
        send_lead_email(subject, html_body, plain_body)

        logging.info("✅ Lead saved & email sent for phone: %s", phone)
        return jsonify({"success": True, "message": "Your inquiry has been submitted successfully!"})

    except mysql.connector.Error as db_err:
        if conn:
            conn.rollback()
        logging.exception("❌ Database error while saving lead:")
        return jsonify({"success": False, "message": f"Database error: {db_err}"})

    except Exception as e:
        if conn:
            conn.rollback()
        logging.exception("❌ Unexpected error while saving lead:")
        return jsonify({"success": False, "message": f"Error: {e}"})

    finally:
        # ✅ Clean resource closure
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']

        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM admins 
            WHERE (email = %s OR mobile = %s) AND password = %s
        """, (identifier, identifier, password))
        admin = cursor.fetchone()
        conn.close()

        if admin:
            session['admin_id'] = admin['id']
            session['admin_name'] = admin['name']
            flash('Login successful!', 'success')
            return redirect('/dashboard')
        else:
            flash('Invalid email/mobile or password!', 'danger')

    return render_template('login.html')
    
@app.route("/dashboard")
def dashboard():
    if 'admin_logged_in' not in session:
        return redirect("/login")
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM leads ORDER BY added_time DESC")
    leads = cursor.fetchall()
    conn.close()
    return render_template("dashboard.html", leads=leads)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect('/login')    
    
# ---------- Run ----------
if __name__ == "__main__":
    app.run(debug=True)

