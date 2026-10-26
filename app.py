import sqlite3
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

def db():
    con = sqlite3.connect("data.db")
    con.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price REAL)")
    return con

PAGE = """
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

@app.route("/", methods=["GET", "POST"])
def home():
    con = db()
    if request.method == "POST":
        con.execute("INSERT INTO products (name, price) VALUES (?, ?)",
                    (request.form["name"], request.form["price"]))
        con.commit()
        return redirect("/")
    products = con.execute("SELECT * FROM products").fetchall()
    return render_template_string(PAGE, products=products)

if __name__ == "__main__":
    app.run(debug=True)