# Sales Quotation Manager

A simple web-based Sales Quotation Manager built using Python, Flask, and SQLite.

## Features

- Add and manage products
- Generate sales quotations
- Calculate subtotal, discounts, and 18% GST
- Store customer leads and contact details
- Track leads as New, Contacted, or Converted
- View a dashboard with product counts, lead statistics, and conversion rate

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- Git and GitHub

## How to Run the Project

1. Install Python.
2. Install Flask:

   ```bash
   pip install flask
   ```

3. Open the project folder in a terminal.
4. Run the application:

   ```bash
   python app.py
   ```

5. Open your browser and visit:

   `http://127.0.0.1:5000`

## Pages

- Products: `/`
- New Quotation: `/quote`
- Lead Tracker: `/leads`
- Dashboard: `/dashboard`

## Notes

The application uses a local SQLite database named `data.db`.

This project is intended for learning and demonstration purposes.