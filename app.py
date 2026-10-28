import sqlite3
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)
DB_NAME = "data.db"


def db():
    con = sqlite3.connect(DB_NAME)
    con.row_factory = sqlite3.Row
    con.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            company TEXT,
            status TEXT DEFAULT 'New'
        )
    """)
    con.commit()
    return con


STYLE = """
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f3f6fb;
    color: #1e293b;
}
header {
    background: #172554;
    color: white;
    padding: 22px 7%;
}
header h1 { margin: 0 0 8px; font-size: 25px; }
header p { margin: 0; color: #cbd5e1; }
nav {
    background: white;
    padding: 16px 7%;
    border-bottom: 1px solid #e2e8f0;
}
nav a {
    color: #1d4ed8;
    text-decoration: none;
    font-weight: bold;
    margin-right: 22px;
}
main { max-width: 1100px; margin: 32px auto; padding: 0 20px; }
h2 { margin-top: 0; color: #172554; }
h3 { color: #334155; }
.card {
    background: white;
    padding: 24px;
    border-radius: 14px;
    margin-bottom: 24px;
    box-shadow: 0 4px 15px #0f172a0b;
    border: 1px solid #e2e8f0;
}
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 18px;
    margin-bottom: 24px;
}
.stat {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 22px;
}
.stat p { color: #64748b; margin: 0 0 12px; }
.stat strong { font-size: 28px; color: #1d4ed8; }
input, select {
    width: 100%;
    padding: 12px;
    margin: 7px 0 15px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    font-size: 15px;
    background: white;
}
label { font-weight: bold; font-size: 14px; }
button, .button {
    display: inline-block;
    background: #2563eb;
    color: white;
    padding: 11px 17px;
    border: 0;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
    text-decoration: none;
}
button:hover, .button:hover { background: #1d4ed8; }
table { width: 100%; border-collapse: collapse; }
th, td {
    text-align: left;
    padding: 13px;
    border-bottom: 1px solid #e2e8f0;
}
th { background: #eff6ff; color: #1e3a8a; }
.table-wrap { overflow-x: auto; }
.total { font-size: 23px; color: #15803d; font-weight: bold; }
.muted { color: #64748b; }
footer { text-align: center; padding: 25px; color: #64748b; }
@media (max-width: 600px) {
    nav a { display: inline-block; margin: 5px 12px 5px 0; }
    header { padding: 20px; }
    main { padding: 0 12px; margin-top: 20px; }
    .card { padding: 16px; }
}
@media print {
    @page {
        size: A4;
        margin: 10mm;
    }

    body {
        font-size: 12px;
    }

    header, nav, button {
        display: none !important;
    }

    .card {
        padding: 10px !important;
        margin: 0 !important;
        box-shadow: none !important;
        break-inside: avoid;
    }

    table {
        width: 100%;
        font-size: 12px;
    }
}
</style>
"""

NAV = """
<header>
    <h1>Sales Quotation Manager</h1>
    <p>Manage products, customer leads and quotations in one place.</p>
</header>
<nav>
    <a href="/">Products</a>
    <a href="/quote">New Quotation</a>
    <a href="/leads">Lead Tracker</a>
    <a href="/dashboard">Dashboard</a>
</nav>
"""

BASE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }} | Sales Quotation Manager</title>
""" + STYLE + """
</head>
<body>
""" + NAV + """
<main>
{{ content|safe }}
</main>
<footer>Sales Quotation Manager &copy; 2026</footer>
</body>
</html>
"""


def page(title, content, **context):
    html = render_template_string(content, **context)
    return render_template_string(BASE, title=title, content=html)


@app.route("/", methods=["GET", "POST"])
def home():
    con = db()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        try:
            price = float(request.form.get("price", ""))
            if not name or price < 0:
                raise ValueError
        except ValueError:
            con.close()
            return "Enter a valid product name and non-negative price.", 400

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

    content = """
    <div class="card">
        <h2>Products</h2>
        <p class="muted">Add and manage your product price list.</p>
        <form method="post">
            <label>Product name</label>
            <input name="name" placeholder="e.g. Air Cylinder" required>
            <label>Price (Rs)</label>
            <input name="price" type="number" min="0" step="0.01"
                   placeholder="Enter price" required>
            <button type="submit">+ Add Product</button>
        </form>
    </div>
    <div class="card">
        <h2>Product List ({{ products|length }})</h2>
        {% if products %}
        <div class="table-wrap"><table>
            <tr><th>Product</th><th>Price</th></tr>
            {% for p in products %}
            <tr><td>{{ p['name'] }}</td>
                <td>Rs {{ "%.2f"|format(p['price']) }}</td></tr>
            {% endfor %}
        </table></div>
        {% else %}
        <p class="muted">No products yet. Add your first product above.</p>
        {% endif %}
    </div>
    """
    return page("Products", content, products=products)


@app.route("/quote", methods=["GET", "POST"])
def quote():
    con = db()
    products = con.execute("SELECT * FROM products ORDER BY name").fetchall()
    q = None
    error = None

    if request.method == "POST":
        try:
            product_id = int(request.form["product"])
            qty = int(request.form["qty"])
            discount_percent = float(request.form.get("discount", 0))

            product = con.execute(
                "SELECT * FROM products WHERE id = ?", (product_id,)
            ).fetchone()

            if product is None:
                raise ValueError("Please select a valid product.")
            if qty < 1:
                raise ValueError("Quantity must be at least 1.")
            if not 0 <= discount_percent <= 100:
                raise ValueError("Discount must be between 0 and 100.")

            subtotal = product["price"] * qty
            discount = subtotal * discount_percent / 100
            taxable = subtotal - discount
            gst = taxable * 0.18
            total = taxable + gst

            q = {
                "name": product["name"],
                "price": product["price"],
                "qty": qty,
                "subtotal": subtotal,
                "discount": discount,
                "gst": gst,
                "total": total
            }
        except (ValueError, KeyError):
            error = "Please enter a valid product, quantity and discount."

    con.close()

    content = """
    <div class="card">
        <h2>New Quotation</h2>
        <p class="muted">Calculate subtotal, discount, GST and final price.</p>
        {% if error %}<p style="color:#dc2626">{{ error }}</p>{% endif %}
        {% if products %}
        <form method="post">
            <label>Select product</label>
            <select name="product" required>
                {% for p in products %}
                <option value="{{ p['id'] }}"
                    {% if request.form.get('product') == p['id']|string %}
                    selected{% endif %}>
                    {{ p['name'] }} - Rs {{ "%.2f"|format(p['price']) }}
                </option>
                {% endfor %}
            </select>
            <label>Quantity</label>
            <input name="qty" type="number" min="1"
                   value="{{ request.form.get('qty', '1') }}" required>
            <label>Discount (%)</label>
            <input name="discount" type="number" min="0" max="100"
                   step="0.01" value="{{ request.form.get('discount', '0') }}"
                   required>
            <button type="submit">Calculate Quotation</button>
        </form>
        {% else %}
        <p>No products available. Add a product before creating a quotation.</p>
        <a class="button" href="/">Go to Products</a>
        {% endif %}
    </div>

    {% if q %}
    <div class="card">
        <h2>Quotation Summary</h2>
        <div class="table-wrap"><table>
            <tr><th>Item</th><th>Amount</th></tr>
            <tr><td>Product</td><td>{{ q.name }}</td></tr>
            <tr><td>Unit price</td>
                <td>Rs {{ "%.2f"|format(q.price) }}</td></tr>
            <tr><td>Quantity</td><td>{{ q.qty }}</td></tr>
            <tr><td>Subtotal</td>
                <td>Rs {{ "%.2f"|format(q.subtotal) }}</td></tr>
            <tr><td>Discount</td>
                <td>- Rs {{ "%.2f"|format(q.discount) }}</td></tr>
            <tr><td>GST (18%)</td>
                <td>Rs {{ "%.2f"|format(q.gst) }}</td></tr>
        </table></div>
        <p class="total">Total: Rs {{ "%.2f"|format(q.total) }}</p>
        <button onclick="window.print()">Print Quotation</button>
    </div>
    {% endif %}
    """
    return page("New Quotation", content, products=products, q=q,
                error=error, request=request)


@app.route("/leads", methods=["GET", "POST"])
def leads():
    con = db()

    if request.method == "POST":
        if request.form.get("action") == "status":
            lead_id = request.form.get("lead_id", type=int)
            status = request.form.get("status", "New")
            allowed = {"New", "Contacted", "Qualified", "Converted", "Lost"}
            if lead_id and status in allowed:
                con.execute(
                    "UPDATE leads SET status = ? WHERE id = ?",
                    (status, lead_id)
                )
        else:
            name = request.form.get("name", "").strip()
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

    lead_list = con.execute(
        "SELECT * FROM leads ORDER BY id DESC"
    ).fetchall()
    con.close()

    content = """
    <div class="card">
        <h2>Lead Tracker</h2>
        <p class="muted">Record customers and track sales follow-ups.</p>
        <h3>Add New Lead</h3>
        <form method="post">
            <label>Customer name</label>
            <input name="name" placeholder="Customer name" required>
            <label>Phone number</label>
            <input name="phone" placeholder="Phone number">
            <label>Email address</label>
            <input name="email" type="email" placeholder="Email address">
            <label>Company name</label>
            <input name="company" placeholder="Company name">
            <button type="submit">+ Add Lead</button>
        </form>
    </div>
    <div class="card">
        <h2>Customer Leads</h2>
        {% if lead_list %}
        <div class="table-wrap"><table>
            <tr><th>Name</th><th>Phone</th><th>Email</th>
                <th>Company</th><th>Status</th><th>Update</th></tr>
            {% for lead in lead_list %}
            <tr>
                <td>{{ lead['name'] }}</td>
                <td>{{ lead['phone'] or '-' }}</td>
                <td>{{ lead['email'] or '-' }}</td>
                <td>{{ lead['company'] or '-' }}</td>
                <td>{{ lead['status'] or 'New' }}</td>
                <td>
                    <form method="post">
                        <input type="hidden" name="action" value="status">
                        <input type="hidden" name="lead_id"
                               value="{{ lead['id'] }}">
                        <select name="status">
                            {% for s in statuses %}
                            <option value="{{ s }}"
                                {% if (lead['status'] or 'New') == s %}
                                selected{% endif %}>{{ s }}</option>
                            {% endfor %}
                        </select>
                        <button type="submit">Update</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table></div>
        {% else %}
        <p class="muted">No leads yet. Add your first lead above.</p>
        {% endif %}
    </div>
    """
    return page("Lead Tracker", content, lead_list=lead_list,
                statuses=["New", "Contacted", "Qualified", "Converted", "Lost"])


@app.route("/dashboard")
def dashboard():
    con = db()
    product_count = con.execute(
        "SELECT COUNT(*) FROM products"
    ).fetchone()[0]
    lead_count = con.execute(
        "SELECT COUNT(*) FROM leads"
    ).fetchone()[0]
    converted = con.execute(
        "SELECT COUNT(*) FROM leads WHERE status = 'Converted'"
    ).fetchone()[0]
    status_rows = con.execute("""
        SELECT COALESCE(status, 'New') AS status, COUNT(*) AS count
        FROM leads GROUP BY COALESCE(status, 'New')
        ORDER BY count DESC
    """).fetchall()
    con.close()

    rate = (converted / lead_count * 100) if lead_count else 0

    content = """
    <h2>Sales Dashboard</h2>
    <div class="grid">
        <div class="stat"><p>Total Products</p>
            <strong>{{ product_count }}</strong></div>
        <div class="stat"><p>Total Leads</p>
            <strong>{{ lead_count }}</strong></div>
        <div class="stat"><p>Converted Leads</p>
            <strong>{{ converted }}</strong></div>
        <div class="stat"><p>Conversion Rate</p>
            <strong>{{ "%.1f"|format(rate) }}%</strong></div>
    </div>
    <div class="card">
        <h2>Lead Status Summary</h2>
        {% if status_rows %}
        <div class="table-wrap"><table>
            <tr><th>Status</th><th>Count</th></tr>
            {% for row in status_rows %}
            <tr><td>{{ row['status'] }}</td>
                <td>{{ row['count'] }}</td></tr>
            {% endfor %}
        </table></div>
        {% else %}
        <p class="muted">No customer leads yet.</p>
        {% endif %}
        <p><a class="button" href="/leads">Manage Leads</a></p>
    </div>
    """
    return page("Dashboard", content, product_count=product_count,
                lead_count=lead_count, converted=converted,
                rate=rate, status_rows=status_rows)


if __name__ == "__main__":
    db().close()
    app.run(debug=True)