# app.py
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',
        database='ecommercems'
    )
    return connection

@app.route('/')
def index():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM product')
    products = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('index.html', products=products)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        quantity = request.form['quantity']
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO product (name, description, price, quantity) VALUES (%s, %s, %s, %s)', 
                       (name, description, price, quantity))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('index'))
    return render_template('add_product.html')

@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM product WHERE product_id = %s', (product_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('index'))

@app.route('/modify_product/<int:product_id>', methods=['GET', 'POST'])
def modify_product(product_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        quantity = request.form['quantity']
        cursor.execute('UPDATE product SET name=%s, description=%s, price=%s, quantity=%s WHERE product_id=%s', 
                       (name, description, price, quantity, product_id))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('index'))
    cursor.execute('SELECT * FROM product WHERE product_id = %s', (product_id,))
    product = cursor.fetchone()
    cursor.close()
    connection.close()
    return render_template('modify_product.html', product=product)

# Query 1: Top 5 Best-Selling Products in the Last Quarter
@app.route('/top_selling_products')
def top_selling_products():
    query = """
    SELECT p.name, SUM(op.quantity) AS total_sold
    FROM `order` o
    JOIN order_product op ON o.order_id = op.order_id
    JOIN product p ON op.product_id = p.product_id
    WHERE o.date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
    GROUP BY p.product_id
    ORDER BY total_sold DESC
    LIMIT 5;
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('top_selling_products.html', results=results)

# Query 2: Customers Who Spent Over a Certain Amount in the Past Year
@app.route('/high_value_customers')
def high_value_customers():
    query = """
    SELECT u.username, u.email, SUM(o.total_amount) AS total_spent
    FROM `user` u
    JOIN `order` o ON u.user_id = o.user_id
    WHERE o.date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
    GROUP BY u.user_id
    HAVING total_spent > 1000; -- Replace 1000 with the threshold amount
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('high_value_customers.html', results=results)

# Query 3: Average Profit Margin for Each Product Category
@app.route('/average_profit_margin')
def average_profit_margin():
    query = """
    SELECT c.name AS category_name, AVG(p.price - p.cost) AS avg_profit_margin
    FROM product p
    JOIN product_category pc ON p.product_id = pc.product_id
    JOIN category c ON pc.category_id = c.category_id
    GROUP BY c.category_id;
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('average_profit_margin.html', results=results)

# Query 4: Products with Low Stock Levels that Haven't Sold in the Past Month
@app.route('/low_stock_products')
def low_stock_products():
    query = """
    SELECT p.name, p.quantity
    FROM product p
    LEFT JOIN order_product op ON p.product_id = op.product_id
    LEFT JOIN `order` o ON op.order_id = o.order_id AND o.date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
    WHERE p.quantity < 10 AND o.order_id IS NULL;
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('low_stock_products.html', results=results)

# Query 5: Sales Trends by Month for the Past Year
@app.route('/sales_trends')
def sales_trends():
    query = """
    SELECT DATE_FORMAT(o.date, '%Y-%m') AS month, SUM(o.total_amount) AS total_sales
    FROM `order` o
    WHERE o.date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
    GROUP BY month
    ORDER BY month;
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('sales_trends.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
