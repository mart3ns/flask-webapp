import re
import auto_email
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .model import User, Item, Order, order_item
from . import db

authentication = Blueprint('authentication', __name__)


@authentication.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Már be van jelentkezve')
        return redirect(url_for('view.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if re.match(pattern, email) is None:
            flash('Helytelen e-mail formátum!', 'error')
            return redirect(request.url)

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Sikeres bejelentkezés', 'success')
                login_user(user, remember=True)
                return redirect(url_for('view.home'))
            else:
                flash('Rossz e-mail cím és/vagy jelszó', 'error')
        else:
            flash('Rossz e-mail cím és/vagy jelszó', 'error')

    return render_template("login.html", user=current_user)


@authentication.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sikeres kijelentkezés')
    return redirect(url_for('authentication.login'))


@authentication.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        flash('Már be van jelentkezve')
        return redirect(url_for('view.home'))

    save_details = [None, None, None, None]
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        password_check = request.form.get('password_check')
        address = request.form.get('address')

        save_details[0] = first_name
        save_details[1] = last_name
        save_details[2] = email
        save_details[3] = address

        user = User.query.filter_by(email=email).first()
        error = False

        if user:
            flash('A megadott e-mail címmel már regisztráltak!', 'error')
            error = True

        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if re.match(pattern, email) is None:
            flash('Helytelen e-mail cím!', 'error')
            error = True

        pattern = r'^[a-zA-ZáéíóöőúüűÁÉÍÓÖŐÚÜŰ\.\- ]+$'
        if re.match(pattern, last_name) is None or len(last_name) < 2:
            flash('A vezetéknév helytelen karaktereket tartalmaz és/vagy nem elég hosszú!', 'error')
            error = True
        if re.match(pattern, first_name) is None or len(first_name) < 2:
            flash('A keresztnév helytelen karaktereket tartalmaz és/vagy nem elég hosszú!', 'error')
            error = True
        if password != password_check:
            flash('A beírt jelszavak nem egyeznek!', 'error')
            error = True
        if len(password) < 8:
            flash('A jelszónak legalább 8 karakter hosszúnak kell lenni!', 'error')
            error = True

        pattern = r'^\d{4}\s[\w\s\-\/.,]+[\d.]$'
        if re.match(pattern, address) is None:
            flash('Szállítási cím nem megfelelő formátumú!', 'error')
            error = True

        if not error:
            new_user = User(first_name=first_name, last_name=last_name, email=email,
                            password=generate_password_hash(password, method='sha256'), address=address)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Profil létrehozva', 'success')

            auto_email.SUBJECT = 'Sikeres regisztráció'
            auto_email.BODY = f"""
Kedves {new_user.last_name} {new_user.first_name}!

Sikeresen regisztrált a Konzol_World oldalán!

Üdvözlettel,
A Konzol_World csapata
"""

            auto_email.send_email(new_user.email)

            return redirect(url_for('view.home'))
    return render_template("sign_up.html", user=current_user, save=save_details)


@authentication.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    sorted_orders = Order.query.filter_by(user_id=current_user.get_id()).all()

    items = Item.query.all()
    game_list = {}
    for game in items:
        game_list[game.id] = game.name + f' ({game.platform})'
    my_order_ids = []
    orders_amount = {}
    my_order_time = {}
    is_completed = {}
    cancelable_order = {}

    for order in sorted_orders:
        my_order_ids.append(order.id)
        orders_amount[order.id] = order.order_amount
        my_order_time[order.id] = str(order.date)
        if order.is_completed and not order.is_deleted:
            is_completed[order.id] = 'Teljesített'
        elif not order.is_completed and not order.is_deleted:
            is_completed[order.id] = 'Függőben'
        else:
            is_completed[order.id] = 'Törölt'
        elapsed_time = datetime.now() - order.date
        cancelable_order[order.id] = elapsed_time < timedelta(hours=1)

    items_in_order = db.session.query(order_item).all()

    orders_and_items = {}
    for item in items_in_order:
        if item[0] in my_order_ids:
            if not item[0] in orders_and_items:
                if item[2] == 1:
                    orders_and_items[item[0]] = [game_list[item[1]]]
                else:
                    orders_and_items[item[0]] = [game_list[item[1]] + f' ({item[2]} db)']
            else:
                if item[2] == 1:
                    orders_and_items[item[0]].append(game_list[item[1]])
                else:
                    orders_and_items[item[0]].append(game_list[item[1]] + f' ({item[2]} db)')

    if request.method == 'POST' and 'cancel_order' in request.form:
        order_id = request.form.get('order_id')
        order = Order.query.filter_by(id=order_id).first()

        order.is_deleted = True
        db.session.commit()
        flash(f'"{order_id}" számú rendelés törölve')
        return redirect(request.url)

    return render_template('profile.html', user=current_user, orders=orders_and_items, prices=orders_amount,
                           date=my_order_time, completed=is_completed, cancelable=cancelable_order)


@authentication.route('/profile/update', methods=['GET', 'POST'])
@login_required
def update_profile():
    if request.method == 'POST' and 'save' in request.form:
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        new_password = request.form.get('new_password')
        new_password_check = request.form.get('new_password_check')
        address = request.form.get('address')
        password = request.form.get('password')

        error = False
        pattern = r'^[a-zA-ZáéíóöőúüűÁÉÍÓÖŐÚÜŰ\.\- ]+$'
        if re.match(pattern, last_name) is None or len(last_name) < 2:
            flash('A vezetéknév helytelen karaktereket tartalmaz és/vagy nem elég hosszú!', 'error')
            error = True
        if re.match(pattern, first_name) is None or len(first_name) < 2:
            flash('A keresztnév helytelen karaktereket tartalmaz és/vagy nem elég hosszú!', 'error')
            error = True
        pattern = r'^\d{4}\s[\w\s\-\/.,]+[\d.]$'
        if re.match(pattern, address) is None:
            flash('Szállítási cím nem megfelelő formátumú!', 'error')
            error = True
        if new_password != new_password_check:
            flash('A beírt új jelszavak nem egyeznek!', 'error')
            error = True
        if new_password and len(new_password) < 8:
            flash('Az új jelszónak legalább 8 karakter hosszúnak kell lenni!', 'error')
            error = True
        if not check_password_hash(current_user.password, password):
            flash('Helytelen jelszó!', 'error')
            error = True
        if not error:
            if current_user.last_name != last_name:
                current_user.last_name = last_name
            if current_user.first_name != first_name:
                current_user.first_name = first_name
            if current_user.address != address:
                current_user.address = address
            if new_password:
                current_user.password = generate_password_hash(new_password, 'sha256')
            db.session.commit()
            flash('Sikeres módosítás!', 'success')
            return redirect(url_for('authentication.profile'))

    if request.method == 'POST' and 'cancel' in request.form:
        return redirect(url_for('authentication.profile'))

    return render_template('profile_update.html', user=current_user)
