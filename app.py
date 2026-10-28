import sqlite3
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

# ---------------- DATABASE ----------------

def db():
    con = sqlite3.connect("data.db")
    con.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            company TEXT,
            status TEXT DEFAULT 'New'
        )
    """)
    return con


NAV = """
<p>
<a href="/">Products</a> |
<a href="/quote">New Quotation</a> |
<a href="/leads">Lead Tracker</a> |
<a href="/dashboard">Dashboard</a>
</p>
<hr>
"""

# ---------------- PRODUCTS PAGE ----------------

PRODUCTS_PAGE = NAV + """
<h1>Sales Quotation Manager</h1>
<h2>Products</h2>

<form method="post">
    <input name="name" placeholder="Product name" required>
    <input name="price" type="number" step="0.01"
           min="0" placeholder="Price (Rs)" required>
    <button type="submit">Add Product</button>
</form>

<br>
<table border="1" cellpadding="8">
<tr><th>Name</th><th>Price (Rs)</th></tr>
{% for p in products %}
<tr><td>{{ p[1] }}</td><td>{{ "%.2f"|format(p[2]) }}</td></tr>
{% endfor %}
</table>
"""

# ---------------- QUOTATION PAGE ----------------

QUOTE_PAGE = NAV + """
<h1>New Quotation</h1>

{% if products %}
<form method="post">
    <label>Product:</label>
    <select name="product" required>
        {% for p in products %}
        <option value="{{ p[0] }}">
            {{ p[1] }} - Rs {{ "%.2f"|format(p[2]) }}
        </option>
        {% endfor %}
    </select>

    <p>Quantity:
    <input name="qty" type="number" min="1" value="1" required></p>

    <p>Discount %:
    <input name="discount" type="number" min="0" max="100"
           step="0.01" value="0" required></p>

    <button type="submit">Calculate</button>
</form>
{% else %}
<p>Add a product before creating a quotation.</p>
{% endif %}

{% if q %}
<h2>Quotation Result</h2>
<table border="1" cellpadding="8">
<tr><td>Product</td><td>{{ q.name }}</td></tr>
<tr><td>Unit price</td><td>Rs {{ "%.2f"|format(q.price) }}</td></tr>
<tr><td>Quantity</td><td>{{ q.qty }}</td></tr>
<tr><td>Subtotal</td><td>Rs {{ "%.2f"|format(q.subtotal) }}</td></tr>
<tr><td>Discount</td><td>- Rs {{ "%.2f"|format(q.discount) }}</td></tr>
<tr><td>GST (18%)</td><td>Rs {{ "%.2f"|format(q.gst) }}</td></tr>
<tr><th>Total</th><th>Rs {{ "%.2f"|format(q.total) }}</th></tr>
</table>
{% endif %}
"""

# ---------------- LEAD TRACKER PAGE ----------------

LEADS_PAGE = NAV + """
<h1>Lead Tracker</h1>
<h2>Add New Lead</h2>

<form method="post">
    <p><input name="name" placeholder="Customer name" required></p>
    <p><input name="phone" placeholder="Phone number"></p>
    <p><input name="email" type="email" placeholder="Email address"></p>
    <p><input name="company" placeholder="Company name"></p>
    <button type="submit">Add Lead</button>
</form>

<h2>Customer Leads</h2>

{% if leads %}
<table border="1" cellpadding="8">
<tr>
    <th>Name</th><th>Phone</th><th>Email</th>
    <th>Company</th><th>Status</th><th>Update Status</th>
</tr>
{% for lead in leads %}
<tr>
    <td>{{ lead[1] }}</td>
    <td>{{ lead[2] or "-" }}</td>
    <td>{{ lead[3] or "-" }}</td>
    <td>{{ lead[4] or "-" }}</td>
    <td>{{ lead[5] }}</td>
    <td>
        <form method="post" action="/update_lead/{{ lead[0] }}">
            <select name="status">
                {% for s in ["New", "Contacted", "Converted"] %}
                <option value="{{ s }}"
                {% if lead[5] == s %}selected{% endif %}>
                    {{ s }}
                </option>
                {% endfor %}
            </select>
            <button type="submit">Update</button>
        </form>
    </td>
</tr>
{% endfor %}
</table>
{% else %}
<p>No leads yet. Add your first lead above.</p>
{% endif %}
"""

# ---------------- DASHBOARD PAGE ----------------

DASHBOARD_PAGE = NAV + """
<h1>Sales Dashboard</h1>

<h2>Products: {{ product_count }}</h2>

<h2>Total Leads: {{ total_leads }}</h2>

<h2>Lead Status Summary</h2>
<table border="1" cellpadding="8">
<tr><th>Status</th><th>Count</th></tr>
{% for status, count in status_counts %}
<tr><td>{{ status }}</td><td>{{ count }}</td></tr>
{% endfor %}
</table>

<p>
<strong>Converted leads:</strong> {{ converted }}
</p>
<p>
<strong>Conversion rate:</strong> {{ conversion_rate }}%
</p>
"""

# ---------------- HOME / PRODUCTS ----------------

@app.route("/", methods=["GET", "POST"])
def home():
    con = db()

    if request.method == "POST":
        name = request.form["name"].strip()
        price = float(request.form["price"])

        if name and price >= 0:
            con.execute(
                "INSERT INTO products (name, price) VALUES (?, ?)",
                (name, price)
            )
            con.commit()

        con.close()
        return redirect("/")

    products = con.execute(
        "SELECT * FROM products ORDER BY id DESC"
    ).fetchall()

    con.close()
    return render_template_string(PRODUCTS_PAGE, products=products)


# ---------------- QUOTATIONS ----------------

@app.route("/quote", methods=["GET", "POST"])
def quote():
    con = db()
    products = con.execute("SELECT * FROM products").fetchall()
    q = None

    if request.method == "POST":
        try:
            product_id = int(request.form["product"])
            qty = int(request.form["qty"])
            discount_percent = float(request.form["discount"])

            p = con.execute(
                "SELECT * FROM products WHERE id = ?",
                (product_id,)
            ).fetchone()

            if p and qty > 0 and 0 <= discount_percent <= 100:
                subtotal = p[2] * qty
                discount = subtotal * discount_percent / 100
                taxable_amount = subtotal - discount
                gst = taxable_amount * 0.18
                total = taxable_amount + gst

                q = {
                    "name": p[1],
                    "price": p[2],
                    "qty": qty,
                    "subtotal": round(subtotal, 2),
                    "discount": round(discount, 2),
                    "gst": round(gst, 2),
                    "total": round(total, 2)
                }
        except (ValueError, TypeError):
            pass

    con.close()
    return render_template_string(QUOTE_PAGE, products=products, q=q)


# ---------------- LEAD TRACKER ----------------

@app.route("/leads", methods=["GET", "POST"])
def leads_page():
    con = db()

    if request.method == "POST":
        name = request.form["name"].strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        company = request.form.get("company", "").strip()

        if name:
            con.execute("""
                INSERT INTO leads (name, phone, email, company, status)
                VALUES (?, ?, ?, ?, 'New')
            """, (name, phone, email, company))
            con.commit()

        con.close()
        return redirect("/leads")

    leads = con.execute(
        "SELECT * FROM leads ORDER BY id DESC"
    ).fetchall()

    con.close()
    return render_template_string(LEADS_PAGE, leads=leads)


# ---------------- UPDATE LEAD STATUS ----------------

@app.route("/update_lead/<int:lead_id>", methods=["POST"])
def update_lead(lead_id):
    status = request.form.get("status")
    allowed_statuses = ["New", "Contacted", "Converted"]

    if status in allowed_statuses:
        con = db()
        con.execute(
            "UPDATE leads SET status = ? WHERE id = ?",
            (status, lead_id)
        )
        con.commit()
        con.close()

    return redirect("/leads")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():
    con = db()

    product_count = con.execute(
        "SELECT COUNT(*) FROM products"
    ).fetchone()[0]

    total_leads = con.execute(
        "SELECT COUNT(*) FROM leads"
    ).fetchone()[0]

    converted = con.execute(
        "SELECT COUNT(*) FROM leads WHERE status = 'Converted'"
    ).fetchone()[0]

    status_counts = con.execute("""
        SELECT status, COUNT(*)
        FROM leads
        GROUP BY status
        ORDER BY status
    """).fetchall()

    conversion_rate = (
        round(converted / total_leads * 100, 2)
        if total_leads else 0
    )

    con.close()

    return render_template_string(
        DASHBOARD_PAGE,
        product_count=product_count,
        total_leads=total_leads,
        converted=converted,
        conversion_rate=conversion_rate,
        status_counts=status_counts
    )


# ---------------- START APP ----------------

if __name__ == "__main__":
    app.run(debug=True)