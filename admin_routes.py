from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from db import get_db_connection
import bleach  

admin = Blueprint('admin', __name__)

def login_required(f):
    @wraps(f)
    def dfunc(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return dfunc


def selloradm_required(f):
    @wraps(f)
    def dfunc(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.')
            return redirect(url_for('auth.login'))
        if not session.get('is_seller') and not session.get('is_admin'):
            flash('Only sellers or admins can access this page')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return dfunc


@admin.route('/')
@login_required
def admin_home():
    if session.get('is_admin'):
        return redirect(url_for('admin.managusers'))
    return redirect(url_for('admin.manproducts'))

@admin.route('/products')
@login_required
def manproducts():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('admin_products.html', products=products)

@admin.route('/products/add', methods=['GET', 'POST'])
@selloradm_required
def adproduct():
    if request.method == 'POST':
        name = bleach.clean(request.form['name'], tags=[], strip=True)
        price = float(request.form['price'])
        description = bleach.clean(
            request.form.get('description', ''),
            tags=['b', 'i', 'u', 'p', 'br'],  
            strip=True
        )
        seller_email = session['email']

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO products (name, price, description, seller_name) VALUES (?, ?, ?, ?)',
            (name, price, description, seller_email)
        )
        conn.commit()
        conn.close()

        flash('Product added successfully')
        return redirect(url_for('admin.manproducts'))

    return render_template('add_product.html')

@admin.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@selloradm_required
def edit_product(id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()

    if not product:
        flash('Product not found')
        conn.close()
        return redirect(url_for('admin.manproducts'))

    if session.get('is_seller') and not session.get('is_admin'):
        if product['seller_name'] != session.get('email'):
            flash('You can only edit your own products')
            conn.close()
            return redirect(url_for('admin.manproducts'))

    if request.method == 'POST':
        name = bleach.clean(request.form['name'], tags=[], strip=True)
        price = float(request.form['price'])
        description = bleach.clean(
            request.form.get('description', ''),
            tags=['b', 'i', 'u', 'p', 'br'], 
            strip=True
        )

        conn.execute(
            'UPDATE products SET name = ?, price = ?, description = ? WHERE id = ?',
            (name, price, description, id)
        )
        conn.commit()
        conn.close()
        flash('Product updated successfully')
        return redirect(url_for('admin.manproducts'))

    conn.close()
    return render_template('edit_product.html', product=product)

@admin.route('/products/delete/<int:id>')
@selloradm_required
def delproduct(id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()

    if not product:
        flash('Product not found')
        conn.close()
        return redirect(url_for('admin.manproducts'))

    if session.get('is_seller') and not session.get('is_admin'):
        if product['seller_name'] != session.get('email'):
            flash('You can only delete your own products')
            conn.close()
            return redirect(url_for('admin.manproducts'))

    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Product deleted successfully')
    return redirect(url_for('admin.manproducts'))

@admin.route('/users')
@login_required
def managusers():
    if not session.get('is_admin'):
        flash('Admins only')
        return redirect(url_for('index'))

    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('admin_users.html', users=users)


@admin.route('/users/toggle_suspend/<int:user_id>')
@login_required
def toggle_suspend(user_id):
    if not session.get('is_admin'):
        flash('Admins only')
        return redirect(url_for('index'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    if not user:
        flash('User not found.')
        conn.close()
        return redirect(url_for('admin.managusers'))

    new_status = 0 if user['is_suspended'] else 1
    conn.execute('UPDATE users SET is_suspended = ? WHERE id = ?', (new_status, user_id))
    conn.commit()
    conn.close()

    status_text = "unsuspended" if new_status == 0 else "suspended"
    flash(f"User {user['email']} has been {status_text}.")
    return redirect(url_for('admin.managusers'))


@admin.route('/users/make_seller/<int:user_id>')
@login_required
def make_seller(user_id):
    if not session.get('is_admin'):
        flash('Admins only.')
        return redirect(url_for('index'))

    conn = get_db_connection()
    conn.execute('UPDATE users SET is_seller = 1 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

    flash('User promoted to seller')
    return redirect(url_for('admin.managusers'))


@admin.route('/users/remove_seller/<int:user_id>')
@login_required
def remove_seller(user_id):
    if not session.get('is_admin'):
        flash('Admins only.')
        return redirect(url_for('index'))

    conn = get_db_connection()
    conn.execute('UPDATE users SET is_seller = 0 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

    flash('Seller status removed')
    return redirect(url_for('admin.managusers'))