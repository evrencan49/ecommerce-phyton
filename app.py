# app.py
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='yourusername',
        password='yourpassword',
        database='yourdatabase'
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

if __name__ == '__main__':
    app.run(debug=True)
