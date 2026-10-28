import sqlite3
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

def db():
    con = sqlite3.connect("data.db")
    con.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price REAL)")
    return con

NAV = '<p><a href="/">Products</a> | <a href="/quote">New Quotation</a></p>'

PRODUCTS_PAGE = NAV + """
<h1>Sales Quotation Manager</h1>
<h2>Products</h2>
<form method="post">
  <input name="name" placeholder="Product name" required>
  <input name="price" type="number" step="0.01" placeholder="Price" required>
  <button>Add</button>
</form>
<table border="1" cellpadding="6">
  <tr><th>Name</th><th>Price (Rs)</th></tr>
  {% for p in products %}<tr><td>{{ p[1] }}</td><td>{{ p[2] }}</td></tr>{% endfor %}
</table>
"""

QUOTE_PAGE = NAV + """
<h1>New Quotation</h1>
<form method="post">
  <select name="product">
    {% for p in products %}<option value="{{ p[0] }}">{{ p[1] }} - Rs {{ p[2] }}</option>{% endfor %}
  </select>
  Qty: <input name="qty" type="number" min="1" value="1" required>
  Discount %: <input name="discount" type="number" min="0" max="100" value="0">
  <button>Calculate</button>
</form>
{% if q %}
<h3>Quotation</h3>
<table border="1" cellpadding="6">
  <tr><td>Product</td><td>{{ q.name }}</td></tr>
  <tr><td>Unit price</td><td>{{ q.price }}</td></tr>
  <tr><td>Quantity</td><td>{{ q.qty }}</td></tr>
  <tr><td>Subtotal</td><td>{{ q.subtotal }}</td></tr>
  <tr><td>Discount</td><td>- {{ q.discount }}</td></tr>
  <tr><td>GST 18%</td><td>{{ q.gst }}</td></tr>
  <tr><td><b>Total</b></td><td><b>{{ q.total }}</b></td></tr>
</table>
{% endif %}
"""

@app.route("/", methods=["GET", "POST"])
def home():
    con = db()
    if request.method == "POST":
        con.execute("INSERT INTO products (name, price) VALUES (?, ?)",
                    (request.form["name"], request.form["price"]))
        con.commit()
        return redirect("/")
    products = con.execute("SELECT * FROM products").fetchall()
    return render_template_string(PRODUCTS_PAGE, products=products)

@app.route("/quote", methods=["GET", "POST"])
def quote():
    con = db()
    products = con.execute("SELECT * FROM products").fetchall()
    q = None
    if request.method == "POST":
        p = con.execute("SELECT * FROM products WHERE id = ?",
                        (request.form["product"],)).fetchone()
        qty = int(request.form["qty"])
        subtotal = p[2] * qty
        discount = subtotal * float(request.form["discount"] or 0) / 100
        gst = (subtotal - discount) * 0.18
        q = {"name": p[1], "price": p[2], "qty": qty,
             "subtotal": round(subtotal, 2), "discount": round(discount, 2),
             "gst": round(gst, 2), "total": round(subtotal - discount + gst, 2)}
    return render_template_string(QUOTE_PAGE, products=products, q=q)

if __name__ == "__main__":
    app.run(debug=True)