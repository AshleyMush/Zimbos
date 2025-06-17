from . import admin_bp
from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from models import db, User, Group
from forms import GroupForm, CSRFProtectForm  # import CheckoutLimitForm when ready
from utililties.decorators import roles_required


# -- User Management --
@admin_bp.route('/users')
@roles_required('Admin')
@login_required
def manage_users():
    # user = current_user  # placeholder for future role checks
    users = User.query.all()
    return render_template('users.html', users=users)

@admin_bp.route('/users/ban/<int:user_id>')
@roles_required('Admin')
@login_required
def ban_user(user_id):
    # user = current_user
    target = User.query.get_or_404(user_id)
    target.is_active = False
    db.session.commit()
    flash(f'User {target.name} is now banned.', 'warning')
    return redirect(url_for('admin.manage_users'))


# -- Group Management (CRUD) --
@admin_bp.route('/groups')
@roles_required('Admin')
@login_required
def list_groups():
    # user = current_user
    groups = Group.query.all()
    return render_template('groups.html', groups=groups)

@admin_bp.route('/groups/create', methods=['GET', 'POST'])
@roles_required('Admin')
@login_required
def create_group():
    # user = current_user
    form = GroupForm()
    if form.validate_on_submit():
        group = Group(
            name=form.name.data,
            url=form.url.data,
            description=form.description.data,
            picture_filename=form.picture_filename.data,
            member_count=form.member_count.data or 0
        )
        db.session.add(group)
        db.session.commit()
        flash('Group created.', 'success')
        return redirect(url_for('admin.list_groups'))
    return render_template('group_form.html', form=form, action='Create')

@admin_bp.route('/groups/<int:group_id>/edit', methods=['GET', 'POST'])
@roles_required('Admin')
@login_required
def edit_group(group_id):
    # user = current_user
    group = Group.query.get_or_404(group_id)
    form = GroupForm(obj=group)
    if form.validate_on_submit():
        group.name = form.name.data
        group.url = form.url.data
        group.description = form.description.data
        group.picture_filename = form.picture_filename.data
        group.member_count = form.member_count.data or group.member_count
        db.session.commit()
        flash('Group updated.', 'success')
        return redirect(url_for('admin.list_groups'))
    return render_template('group_form.html', form=form, action='Edit')

@admin_bp.route('/groups/<int:group_id>/delete', methods=['POST'])
@roles_required('Admin')
@login_required
def delete_group(group_id):
    form = CSRFProtectForm()
    if not form.validate_on_submit():
        abort(400)

    # user = current_user
    group = Group.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    flash('Group deleted.', 'danger')
    return redirect(url_for('admin.list_groups'))


# -- Checkout Limit Configuration --
@admin_bp.route('/settings/checkout_limit', methods=['GET', 'POST'])
@roles_required('Admin')
@login_required
def configure_checkout_limit():
    # user = current_user
    """
    Adjust the maximum number of groups a user can checkout.
    Requires CheckoutLimitForm with IntegerField 'limit'.
    """
    # from forms import CheckoutLimitForm
    # form = CheckoutLimitForm(limit=current_app.config.get('GROUP_CHECKOUT_LIMIT', 3))
    # if form.validate_on_submit():
    #     new_limit = form.limit.data
    #     current_app.config['GROUP_CHECKOUT_LIMIT'] = new_limit
    #     flash(f'Checkout limit set to {new_limit}', 'success')
    #     return redirect(url_for('admin.list_groups'))
    # return render_template('checkout_limit_form.html', form=form)
    form = CSRFProtectForm()
    if request.method == 'POST' and not form.validate_on_submit():
        abort(400)

    flash('Checkout limit configuration placeholder.', 'info')
    return redirect(url_for('admin.list_groups'))
