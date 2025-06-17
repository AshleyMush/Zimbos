from . import main_bp
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from models import db, Group, BasketItem, PurchasedItem
from forms import CSRFProtectForm


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
    form = CSRFProtectForm()
    groups = Group.query.all()
    basket_ids = [item.group_id for item in current_user.basket_items]
    print(f"⭐ Basket IDs: {basket_ids}")
    print(f"⭐current_user basket items:  {current_user.basket_items}  Groups:{groups}")
    return render_template('main/dashboard.html', groups=groups, basket_ids=basket_ids, form=form)


@main_bp.route('/add_to_basket', methods=['POST'])
@login_required
def add_to_basket():
    """AJAX endpoint to add a group to basket."""
    form = CSRFProtectForm()
    if not form.validate_on_submit():
        return jsonify({'success': False, 'message': 'Invalid CSRF token.'}), 400

    user = current_user
    group_id = request.json.get('group_id') or request.form.get('group_id')
    if not group_id:
        return jsonify({'success': False, 'message': 'No group_id provided.'}), 400
    group_id = int(group_id)

    # Check if already purchased
    already_purchased = any(item.group_id == group_id for item in current_user.purchased_items)
    if already_purchased:
        return jsonify({'success': False, 'message': 'Group already purchased.'}), 400

    # Enforce checkout limit
    checkout_limit = current_app.config.get('GROUP_CHECKOUT_LIMIT', 3)
    purchased_count = len(current_user.purchased_items)
    basket_count = len(current_user.basket_items)+1  # +1 for the new item being added

    print(f"⭐ Purchased Count: {purchased_count}, Basket Count: {basket_count }- Basket Count Type: {type(basket_count)}")
    if purchased_count + basket_count > checkout_limit:
        print(f"⭐ Checkout limit reached: {purchased_count + basket_count} >= {checkout_limit}")
        return jsonify({'success': False, 'message': f'Checkout limit {checkout_limit} reached.'}), 400

    # Prevent duplicates in basket
    existing = BasketItem.query.filter_by(user_id=user.id, group_id=group_id).first()
    if existing:
        return jsonify({'success': False, 'message': 'Already in basket.'}), 400

    # Add to basket
    item = BasketItem(user_id=user.id, group_id=group_id)
    db.session.add(item)
    db.session.commit()


    in_basket = current_user.basket_items
    print(f"⭐ Basket Count: {basket_count} Basket IDs: {in_basket}")
    return jsonify({'success': True, 'basket_count': basket_count}), 200


@main_bp.route('/remove_from_basket', methods=['POST'])
@login_required
def remove_from_basket():
    """AJAX endpoint to remove a group from basket."""
    form = CSRFProtectForm()
    if not form.validate_on_submit():
        return jsonify({'success': False, 'message': 'Invalid CSRF token.'}), 400

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


@main_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Render checkout summary or finalize purchase via AJAX."""
    user = current_user
    basket_items = current_user.basket_items

    form = CSRFProtectForm()
    if request.method == 'POST':
        if not form.validate_on_submit():
            return jsonify({'success': False, 'message': 'Invalid CSRF token.'}), 400

        limit = current_app.config.get('GROUP_CHECKOUT_LIMIT', 3)
        if len(user.purchased_items) + len(basket_items) > limit:
            return jsonify({'success': False, 'message': 'Checkout limit reached.'}), 400

        purchased_ids = []
        for item in list(basket_items):
            db.session.add(PurchasedItem(user_id=user.id, group_id=item.group_id))
            group = Group.query.get(item.group_id)
            if group:
                group.member_count += 1
            db.session.delete(item)
            purchased_ids.append(item.group_id)
        db.session.commit()

        links = _generate_group_links()

        return jsonify({'success': True, 'purchased_ids': purchased_ids, 'links': links}), 200

    groups = [Group.query.get(item.group_id) for item in basket_items]
    limit = current_app.config.get('GROUP_CHECKOUT_LIMIT', 3)

    return render_template(
        'main/checkout.html',
        groups=groups,
        basket_count=len(basket_items),
        limit=limit,
        form=form,
    )

@main_bp.route('/remove_from_checkout', methods=['POST'])
@login_required
def remove_from_checkout():
    """AJAX endpoint to remove a group while on the checkout page."""
    form = CSRFProtectForm()
    if not form.validate_on_submit():
        return jsonify({'success': False, 'message': 'Invalid CSRF token.'}), 400

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


def _generate_group_links():
    """Helper to build purchased group link data."""
    purchased_groups = [item.group for item in current_user.purchased_items]
    return [
        {'id': g.id, 'name': g.name, 'url': g.url}
        for g in purchased_groups
        if g is not None
    ]

@main_bp.route('/send_group_links', methods=['POST'])
@login_required
def send_group_links():
    """Send purchased group links via email (placeholder)."""
    print("⭐ Sending group links via email... Current user:", current_user.email)
    form = CSRFProtectForm()
    if not form.validate_on_submit():
        return jsonify({'success': False, 'message': 'Invalid CSRF token.'}), 400

    links = _generate_group_links()

    # TODO: Integrate Mailgun to send `links` to current_user.email

    return jsonify({'success': True, 'links': links}), 200
