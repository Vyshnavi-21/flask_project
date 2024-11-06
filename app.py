from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

DATABASE = 'expenses.db'

# Initialize SQLite database
def init_db():
    if not os.path.exists(DATABASE):
        with sqlite3.connect(DATABASE) as conn:
            conn.execute('''
                CREATE TABLE expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    date TEXT NOT NULL
                )
            ''')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    expenses = conn.execute('SELECT * FROM expenses').fetchall()
    conn.close()
    return render_template('index.html', expenses=expenses)

@app.route('/add', methods=('GET', 'POST'))
def add_expense():
    if request.method == 'POST':
        category = request.form['category']
        amount = request.form['amount']
        description = request.form['description']
        date = request.form['date']

        if not category or not amount or not date:
            flash('Category, amount, and date are required!')
        else:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO expenses (category, amount, description, date) VALUES (?, ?, ?, ?)',
                (category, amount, description, date)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('add_expense.html')

@app.route('/delete/<int:id>')
def delete_expense(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM expenses WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Expense was successfully deleted!')
    return redirect(url_for('index'))

@app.route('/data')
def data():
    conn = get_db_connection()
    expenses = conn.execute('SELECT category, SUM(amount) AS total FROM expenses GROUP BY category').fetchall()
    conn.close()
    data = {row['category']: row['total'] for row in expenses}
    return jsonify(data)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
