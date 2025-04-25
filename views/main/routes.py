from . import main_bp
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from models import db, Group, BasketItem, PurchasedItem


class CSRFForm(FlaskForm):
    """Empty form just for CSRF protection in AJAX"""
    pass


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    Render dashboard with all groups, current basket IDs, and CSRF form.
    """
    form = CSRFForm()
    groups = Group.query.all()
    basket_ids = [item.group_id for item in current_user.basket_items]
    return render_template('main/dashboard.html', groups=groups, basket_ids=basket_ids, form=form)


@main_bp.route('/add_to_basket', methods=['POST'])
@login_required
def add_to_basket():
    """AJAX endpoint to add a group to basket."""
    user = current_user
    group_id = request.json.get('group_id') or request.form.get('group_id')
    if not group_id:
        return jsonify({'success': False, 'message': 'No group_id provided.'}), 400
    group_id = int(group_id)

    # Check if already purchased
    already_purchased = PurchasedItem.query.filter_by(user_id=user.id, group_id=group_id).first()
    if already_purchased:
        return jsonify({'success': False, 'message': 'Group already purchased.'}), 400

    # Enforce checkout limit
    limit = current_app.config.get('GROUP_CHECKOUT_LIMIT', 3)
    purchased_count = PurchasedItem.query.filter_by(user_id=user.id).count()
    basket_count = BasketItem.query.filter_by(user_id=user.id).count()
    print(f"⭐ Purchased Count: {purchased_count}, Basket Count: {basket_count}")
    if purchased_count + basket_count >= limit:
        print(f"⭐ Checkout limit reached: {purchased_count + basket_count} >= {limit}")
        return jsonify({'success': False, 'message': 'Checkout limit reached.'}), 400

    # Prevent duplicates in basket
    existing = BasketItem.query.filter_by(user_id=user.id, group_id=group_id).first()
    if existing:
        return jsonify({'success': False, 'message': 'Already in basket.'}), 400

    # Add to basket
    item = BasketItem(user_id=user.id, group_id=group_id)
    db.session.add(item)
    db.session.commit()


    # Check if the group is already in the basket
    #TODO: i added in basket to check whats in the basket and it works kinda
    in_basket = BasketItem.query.filter_by(user_id=user.id).all()
    print(f"⭐ Basket Count: {basket_count} Basket IDs: {in_basket}")
    return jsonify({'success': True, 'basket_count': basket_count.id}), 200


@main_bp.route('/remove_from_basket', methods=['POST'])
@login_required
def remove_from_basket():
    """AJAX endpoint to remove a group from basket."""
    user = current_user
    group_id = request.json.get('group_id') or request.form.get('group_id')
    if not group_id:
        return jsonify({'success': False, 'message': 'No group_id provided.'}), 400
    group_id = int(group_id)

    item = BasketItem.query.filter_by(user_id=user.id, group_id=group_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()

    new_basket_ids = [i.group_id for i in current_user.basket_items]
    return jsonify({'success': True, 'basket_count': len(new_basket_ids), 'basket_ids': new_basket_ids}), 200


@main_bp.route('/checkout', methods=['GET'])
@login_required
def checkout():
    """Render checkout summary."""
    user = current_user
    basket_items = current_user.basket_items
    groups = [Group.query.get(item.group_id) for item in basket_items]
    limit = current_app.config.get('GROUP_CHECKOUT_LIMIT', 3)
    return render_template('main/checkout.html', groups=groups, basket_count=len(basket_items), limit=limit)

# Note: checkout POST and tokenization to follow in Task E
