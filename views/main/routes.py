from . import main_bp
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from models import db, Group, BasketItem, PurchasedItem, InviteToken
from forms import CSRFProtectForm
from datetime import datetime, timedelta
import secrets
import requests
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail




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

    if purchased_count + basket_count > checkout_limit:
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
    if form.validate_on_submit():
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
            token_str = secrets.token_urlsafe(16)
            expires = datetime.utcnow() + timedelta(minutes=15)
            db.session.add(
                InviteToken(
                    user_id=user.id,
                    group_id=item.group_id,
                    token=token_str,
                    expires_at=expires,
                )
            )
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
    tokens = InviteToken.query.filter(
        InviteToken.user_id == current_user.id,
        InviteToken.expires_at > datetime.utcnow(),
    ).all()
    links = []
    for t in tokens:
        if t.group:
            invite_url = url_for('main.join_group', token=t.token, _external=True)
            links.append({'id': t.group.id, 'name': t.group.name, 'url': invite_url})
    return links

@main_bp.route('/send_group_links', methods=['POST'])
@login_required
def send_group_links():
    print("Sending group links via email...")
    form = CSRFProtectForm()
    if not form.validate_on_submit():
        return jsonify({'success': False, 'message': 'Invalid CSRF token.'}), 400

    links = _generate_group_links()
    if not links:
        return jsonify({'success': False, 'message': 'No active invites to send.'}), 400

    # Render both text and HTML
    text_body = render_template('emails/invite.txt', user=current_user, links=links)
    html_body = render_template('emails/invite.html', user=current_user, links=links)

    message = Mail(
        from_email="Zimbos Portal <no-reply@zimbos.org>",
        to_emails= [current_user.email],
        subject=  "Your Zimbos Group Invite Links",
        html_content= html_body)

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        sg.set_sendgrid_data_residency("eu")
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        current_app.logger.error("SendGrid error: %s", str(e))




    return jsonify({'success': True}), 200


@main_bp.route('/join/<token>')
def join_group(token):
    """Redirect to the real group URL if token is valid. """
    invite = InviteToken.query.filter_by(token=token).first_or_404()
    if invite.expires_at < datetime.utcnow():
        flash('Invite link has expired.', 'danger')
        return redirect(url_for('main.dashboard'))
    group = Group.query.get_or_404(invite.group_id)
    return redirect(group.url)
