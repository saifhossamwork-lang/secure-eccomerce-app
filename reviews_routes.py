from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db_connection
import bleach  

reviews = Blueprint('reviews', __name__)

@reviews.route('/product/<int:product_id>', methods=['GET', 'POST'])
def proddetail(product_id):
    conn = get_db_connection()

    if request.method == 'POST':
        if 'user_id' not in session:
            flash('Please log in to leave a review.')
            return redirect(url_for('auth.login'))

        content = request.form.get('content', '').strip()
        if content:
            safe_content = bleach.clean(
                content,
                tags=[],  
                attributes={},
                strip=True
            )

            user_id = session['user_id']
            conn.execute(
                'INSERT INTO reviews (product_id, user_id, content) VALUES (?, ?, ?)',
                (product_id, user_id, safe_content)
            )
            conn.commit()
            flash('Review added successfully!')
            return redirect(url_for('reviews.proddetail', product_id=product_id))
        else:
            flash('Review cannot be empty.')

    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()

    reviews_data = conn.execute('''
    SELECT reviews.content AS content, users.email AS email, reviews.created_at AS created_at
    FROM reviews
    JOIN users ON reviews.user_id = users.id
    WHERE reviews.product_id = ?
    ORDER BY reviews.created_at DESC
    ''', (product_id,)).fetchall()

    conn.close()
    return render_template('product_detail.html', product=product, reviews=reviews_data)