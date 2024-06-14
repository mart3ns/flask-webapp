import os
import auto_email
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from sqlalchemy import select, update, delete
from werkzeug.utils import secure_filename
from sqlalchemy.sql import func
from .model import Item, User, Order, user_item, order_item
from . import db, allowed_file

view = Blueprint('view', __name__)


@view.route('/', methods=['GET', 'POST'])
@view.route('/home', methods=['GET', 'POST'])
def home():
    return render_template("home.html", user=current_user)


@view.route('/playstation', methods=['GET', 'POST'])
def playstation():
    if not current_user.is_authenticated:
        flash('A vásárláshoz jelentkezzen be vagy regisztráljon!')

    games = Item.query.filter(Item.platform.contains('PS'), Item.is_deleted == False).order_by(
        func.lower(Item.name).asc())

    recent_search = ''
    if request.method == 'POST' and 'filter' in request.form:
        query = request.form.get('search')
        recent_search = query
        if not recent_search == '':
            games = Item.query.filter(Item.name.contains(query), Item.is_deleted == False).where(
                Item.platform.contains('PS')).order_by(
                func.lower(Item.name).asc())

    if request.method == 'POST' and 'to_cart' in request.form:
        item_id = request.form.get('item_id')
        item_quantity = request.form.get('item_quantity')

        item = Item.query.filter_by(id=item_id).first()
        user = User.query.filter_by(id=current_user.get_id()).first()

        if item not in user.added_to_cart:
            if not item_quantity.isnumeric():
                flash('Helytelen mennyiség!')
            elif int(item_quantity) < 1:
                flash('A minimum rendelési mennyiség 1 db!')
            elif int(item_quantity) > 5:
                flash('A maximum rendelési mennyiség 5 db!')
            else:
                flash(f'{item.name} ({item.platform}) ({item_quantity} db) kosárba helyezve', 'success')
                user.added_to_cart.append(item)
                db.session.commit()
                stmt = update(user_item).where(
                    (user_item.c.user_id == user.id) & (user_item.c.item_id == item_id)
                ).values(quantity=item_quantity)
                db.session.execute(stmt)
        else:
            stmt = select(user_item.c.quantity).where(
                (user_item.c.user_id == user.id) & (user_item.c.item_id == item_id))
            connect = db.engine.connect()
            result = connect.execute(stmt)
            quantity = result.scalar()
            connect.close()

            if not item_quantity.isnumeric():
                flash('Helytelen mennyiség!')
            elif int(item_quantity) < 1:
                flash('A minimum rendelési mennyiség 1 db!')
            elif int(item_quantity) > 5:
                flash('A maximum rendelési mennyiség 5 db!')
            elif int(item_quantity) + quantity > 5:
                flash('A maximum rendelési mennyiség 5 db!')
            else:
                flash(f'{item.name} ({item.platform}) ({item_quantity} db) kosárba helyezve', 'success')
                stmt = update(user_item).where(
                    (user_item.c.user_id == user.id) & (user_item.c.item_id == item_id)
                ).values(quantity=user_item.c.quantity + item_quantity)
                db.session.execute(stmt)

        db.session.commit()

    if request.method == 'POST' and 'game_edit' in request.form:
        item_id = request.form.get('item_id')
        item_img = request.form.get('item_img').split('/')[-1].split('.')[0]
        item_name = request.form.get('item_name')
        item_platform = request.form.get('item_platform')
        item_price = request.form.get('item_price')
        return redirect(url_for('view.game_edit', id=item_id, img=item_img, name=item_name, platform=item_platform,
                                price=item_price))

    return render_template('playstation.html', items=games, recent_search=recent_search, user=current_user)


@view.route('/xbox', methods=['GET', 'POST'])
def xbox():
    if not current_user.is_authenticated:
        flash('A vásárláshoz jelentkezzen be vagy regisztráljon!')

    games = Item.query.filter(Item.platform.contains('XBOX'), Item.is_deleted == False).order_by(
        func.lower(Item.name).asc())

    recent_search = ''
    if request.method == 'POST' and 'filter' in request.form:
        query = request.form.get('search')
        recent_search = query
        if not recent_search == '':
            games = Item.query.filter(Item.name.contains(query), Item.is_deleted == False).where(
                Item.platform.contains('XBOX')).order_by(
                func.lower(Item.name).asc())

    if request.method == 'POST' and 'to_cart' in request.form:
        item_id = request.form.get('item_id')
        item_quantity = request.form.get('item_quantity')

        item = Item.query.filter_by(id=item_id).first()
        user = User.query.filter_by(id=current_user.get_id()).first()

        if item not in user.added_to_cart:
            if not item_quantity.isnumeric():
                flash('Helytelen mennyiség!')
            elif int(item_quantity) < 1:
                flash('A minimum rendelési mennyiség 1 db!')
            elif int(item_quantity) > 5:
                flash('A maximum rendelési mennyiség 5 db!')
            else:
                flash(f'{item.name} ({item.platform.title()}) ({item_quantity} db) kosárba helyezve', 'success')
                user.added_to_cart.append(item)
                db.session.commit()
                stmt = update(user_item).where(
                    (user_item.c.user_id == user.id) & (user_item.c.item_id == item_id)
                ).values(quantity=item_quantity)
                db.session.execute(stmt)
        else:
            stmt = select(user_item.c.quantity).where(
                (user_item.c.user_id == user.id) & (user_item.c.item_id == item_id))
            connect = db.engine.connect()
            result = connect.execute(stmt)
            quantity = result.scalar()
            connect.close()

            if not item_quantity.isnumeric():
                flash('Helytelen mennyiség!')
            elif int(item_quantity) < 1 or item_quantity == '':
                flash('A minimum rendelési mennyiség 1 db!')
            elif int(item_quantity) > 5:
                flash('A maximum rendelési mennyiség 5 db!')
            elif int(item_quantity) + quantity > 5:
                flash('A maximum rendelési mennyiség 5 db!')
            else:
                flash(f'{item.name} ({item.platform.title()}) ({item_quantity} db) kosárba helyezve', 'success')
                stmt = update(user_item).where(
                    (user_item.c.user_id == user.id) & (user_item.c.item_id == item_id)
                ).values(quantity=user_item.c.quantity + item_quantity)
                db.session.execute(stmt)

        db.session.commit()

    if request.method == 'POST' and 'game_edit' in request.form:
        item_id = request.form.get('item_id')
        item_img = request.form.get('item_img').split('/')[-1].split('.')[0]
        item_name = request.form.get('item_name')
        item_platform = request.form.get('item_platform')
        item_price = request.form.get('item_price')
        return redirect(url_for('view.game_edit', id=item_id, img=item_img, name=item_name, platform=item_platform,
                                price=item_price))

    return render_template('xbox.html', items=games, recent_search=recent_search, user=current_user)


@view.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'GET':
        if not current_user.is_authenticated:
            flash('A kosár megtekintéséhez jelentkezzen be vagy regisztráljon!')
            return render_template('login.html', user=current_user)

    user = User.query.filter_by(id=current_user.get_id()).first()
    game_quantity = {}
    connect = db.engine.connect()
    for game in user.added_to_cart:
        stmt = select(user_item.c.quantity).where((user_item.c.user_id == user.id) & (user_item.c.item_id == game.id))
        result = connect.execute(stmt)
        quantity = result.scalar()
        game_quantity[game.id] = quantity

    connect.close()

    if request.method == 'POST' and 'order' in request.form:
        new_order = Order(user_id=user.id)
        db.session.add(new_order)
        db.session.commit()

        items = []
        price = 0
        for game in user.added_to_cart:
            new_order.items_bought.append(game)
            db.session.commit()

            stmt = update(order_item).where(
                (order_item.c.order_id == new_order.id) & (order_item.c.item_id == game.id)
            ).values(quantity=game_quantity[game.id])
            db.session.execute(stmt)

            items.append(
                f'{game.name} ({game.platform}) ({game_quantity[game.id]} db) - {str(game.price * game_quantity[game.id])} Ft')
            price += game.price * game_quantity[game.id]

            new_order.order_amount = price

        db.session.commit()
        flash('Sikeres rendelés', 'success')

        newline = '\n'
        auto_email.SUBJECT = 'Sikeres vásárlás'
        auto_email.BODY = f"""
Kedves {user.last_name} {user.first_name}!

Köszönjük bizalmát, "{new_order.id}" rendelési azonosítójú rendelése beérkezett hozzánk és az alábbi termékeket tartalmazza:

{newline.join(items)}

Összesen: {price} Ft

A rendelés feldolgozását követően a futárszolgálat a megadott "{user.address}" címre szállítja 1-3 munkanapon belül.
Lemondásra 1 óra áll rendelkezésre, több idő elteltével a "konzol.world.2023@gmail.com" címen érdeklődhet a rendelése állapotáról, lemondási lehetőségéről.

Üdvözlettel,
A Konzol_World csapata
"""

        auto_email.send_email(user.email)

        user.added_to_cart.clear()
        db.session.commit()

    if request.method == 'POST' and 'add_one_to_cart' in request.form:
        item_id = request.form.get('item_id')

        stmt = update(user_item).where(
            (user_item.c.user_id == user.id) & (user_item.c.item_id == item_id)
        ).values(quantity=user_item.c.quantity + 1)
        db.session.execute(stmt)
        db.session.commit()
        return redirect(request.url)

    if request.method == 'POST' and 'remove_one_from_cart' in request.form:
        item_id = request.form.get('item_id')

        stmt = update(user_item).where(
            (user_item.c.user_id == user.id) & (user_item.c.item_id == item_id)
        ).values(quantity=user_item.c.quantity - 1)
        db.session.execute(stmt)
        db.session.commit()
        return redirect(request.url)

    if request.method == 'POST' and 'remove' in request.form:
        item_id = request.form.get('item_id')
        item_name = request.form.get('item_name')
        item_platform = request.form.get('item_platform')

        stmt = delete(user_item).where(
            (user_item.c.user_id == user.id) & (user_item.c.item_id == item_id))
        db.session.execute(stmt)
        db.session.commit()
        flash(f'{item_name} ({item_platform}) eltávolítva a kosárból')

    if request.method == 'POST' and 'remove_all' in request.form:
        stmt = delete(user_item).where(
            (user_item.c.user_id == str(user.id)))
        db.session.execute(stmt)
        db.session.commit()
        flash('A kosár kiürítve')

    return render_template('cart.html', quantity=game_quantity, user=current_user)


@view.route('/orders', methods=['GET', 'POST'])
def orders():
    if not current_user.is_authenticated or int(current_user.get_id()) != 1:
        flash('Nem jogosult a hozzáféréshez!', 'error')
        return redirect(url_for('view.home'))

    pending_orders = Order.query.filter(Order.is_completed == False, Order.is_deleted == False).all()
    fulfill_pending = {}
    for i in pending_orders:
        elapsed_time = datetime.now() - i.date
        fulfill_pending[i.id] = elapsed_time > timedelta(hours=1)

    completed_orders = Order.query.filter(Order.is_completed == True, Order.is_deleted == False).all()
    deleted_orders = Order.query.filter(Order.is_deleted == True).all()

    users = User.query.all()
    user_dict = {}
    for i in range(len(users)):
        user_dict[i + 1] = users[i]
    items = Item.query.all()
    game_list = {}
    for game in items:
        game_list[game.id] = game.name + f' ({game.platform})'

    items_in_order = db.session.query(order_item).all()
    orders_and_items = {}

    for item in items_in_order:
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

    if request.method == 'POST' and 'fulfill_order' in request.form:
        order_id = request.form.get('order_id')
        user_name = request.form.get('user_name')
        user_email = request.form.get('user_email')
        order = Order.query.filter_by(id=order_id).first()

        order.is_completed = True
        db.session.commit()
        flash(f'"{order_id}" számú rendelés teljesítve', 'success')

        auto_email.SUBJECT = f'"{order_id}" számú rendelés sikeresen feldolgozva'
        auto_email.BODY = f"""
Kedves {user_name}!

"{order_id}" számú rendelését sikeresen feldolgoztuk, a mai napon a futárszolgálat részére átadjuk!
Várhatóan 1-3 munkanapon belül szállítják a megadott címre.

Üdvözlettel,
A Konzol_World csapata
"""

        auto_email.send_email(user_email)

        return redirect(request.url)

    if request.method == 'POST' and 'delete_order' in request.form:
        order_id = request.form.get('order_id')
        order = Order.query.filter_by(id=order_id).first()

        order.is_deleted = True
        db.session.commit()
        flash(f'"{order_id}" számú rendelés törölve')
        return redirect(request.url)

    return render_template('orders.html', user=current_user, users=user_dict, orders=orders_and_items,
                           pending=pending_orders, completed=completed_orders, fulfill=fulfill_pending,
                           deleted=deleted_orders)


@view.route('/game_add', methods=['GET', 'POST'])
def game_add():
    error = False
    if not current_user.is_authenticated or int(current_user.get_id()) != 1:
        flash('Nem jogosult a hozzáféréshez!', 'error')
        return redirect(url_for('view.home'))

    save_details = [None, None, None, None]
    if request.method == 'POST' and 'game_add' in request.form:
        name = request.form.get('name')
        platform = request.form.get('platform').upper()
        price = request.form.get('price')
        img_name = request.form.get('img_name')

        save_details[0] = name
        save_details[1] = request.form.get('platform')
        save_details[2] = price
        save_details[3] = img_name

        if platform != 'PS4' and platform != 'PS5' and platform != 'XBOX ONE' and platform != 'XBOX SERIES X':
            flash('Ismeretlen platform!', 'error')
            error = True
        if price <= '0':
            flash('Helytelen ár!', 'error')
            error = True

        for i in Item.query.all():
            if i.name == name and i.platform == platform and i.is_deleted == False:
                flash('A játék már szerepel az adatbázisban!')
                error = True
            elif i.name == name and i.platform == platform and i.is_deleted == True:
                item = Item.query.filter_by(id=i.id).first()
                item.is_deleted = False
                item.price = price
                item.img_name = img_name
                flash('Játék sikeresen visszaállítva!', 'success')
                db.session.commit()
                return redirect(request.url)

        if not error:
            new_item = Item(name=name, platform=platform, price=price, img_name=img_name)
            db.session.add(new_item)
            db.session.commit()
            flash(f'{name} ({platform}) rögzítve', 'success')
            return redirect(request.url)

    if request.method == 'POST' and 'playstation_img_upload' in request.form:
        file = request.files['file']
        if file.filename == '':
            flash('Nincs kiválasztott fájl', 'error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if filename.lower().find('ps4') == -1 and filename.lower().find('ps5') == -1:
                error = True
                flash('A képfájl nevében szerepeljen a "PS4" vagy "PS5" név!', 'error')
            if filename.lower().find('xboxone') != -1 or filename.lower().find('xboxsx') != -1:
                error = True
                flash('A képfájl nevében szerepel "XboxOne" vagy "XboxSX" név, a másik feltöltést használd!', 'error')
            if not error:
                file.save(os.path.join('../flask_webapp/website/static/img/ps_games/', filename))
                flash('Sikeres feltöltés!', 'success')
        else:
            flash('Csak ".jpg" kiterjesztés támogatott!', 'error')

    if request.method == 'POST' and 'xbox_img_upload' in request.form:
        file = request.files['file']
        if file.filename == '':
            flash('Nincs kiválasztott fájl', 'error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if filename.lower().find('xboxone') == -1 and filename.lower().find('xboxsx') == -1:
                error = True
                flash('A képfájl nevében szerepeljen az "XboxOne" vagy "XboxSX" név!', 'error')
            if filename.lower().find('ps4') != -1 or filename.lower().find('ps5') != -1:
                error = True
                flash('A képfájl nevében szerepel "PS4" vagy "PS5" név, a másik feltöltést használd!', 'error')
            if not error:
                file.save(os.path.join('../flask_webapp/website/static/img/xbox_games/', filename))
                flash('Sikeres feltöltés!', 'success')
        else:
            flash('Csak ".jpg" kiterjesztés támogatott!', 'error')

    return render_template('game_add.html', user=current_user, save=save_details)


@view.route('/game_edit', methods=['GET', 'POST'])
def game_edit():
    if not current_user.is_authenticated or int(current_user.get_id()) != 1:
        flash('Nem jogosult a hozzáféréshez!', 'error')
        return redirect(url_for('view.home'))

    if current_user.is_authenticated and int(current_user.get_id()) == 1 and request.args.get('id') is None:
        flash('A játékoknál válaszd a módosítás opciót!')
        return redirect(url_for('view.home'))

    if request.method == 'POST' and 'game_add' in request.form:
        error = False
        item_id = request.args.get('id')
        item_img = request.form.get('img_name')
        item_name = request.form.get('name')
        item_platform = request.form.get('platform')
        item_price = request.form.get('price')
        if item_platform != 'PS4' and item_platform != 'PS5' and item_platform != 'XBOX ONE' and item_platform != 'XBOX SERIES X':
            flash('Ismeretlen platform!', 'error')
            error = True
        if item_price <= '0':
            flash('Helytelen ár!', 'error')
            error = True

        for i in Item.query.all():
            if str(i.name) == item_name and str(i.platform) == item_platform and int(i.price) == int(
                    item_price) and str(i.img_name) == item_img:
                flash('Nem történt módosítás!')
                error = True
                break
            elif str(i.id) != item_id and str(i.name) == item_name and str(
                    i.platform) == item_platform and i.is_deleted == True:
                flash('A megadott névvel és platformmal már szerepel játék az adatbázisban!', 'error')
                flash('Törölt játék, visszaállításhoz a "Játék hozzáadása" funkciót használd!', 'error')
                error = True
                break
            elif str(i.id) != item_id and str(i.name) == item_name and str(i.platform) == item_platform:
                flash('A megadott névvel és platformmal már szerepel játék az adatbázisban!', 'error')
                error = True
                break

        if not error:
            item = Item.query.filter_by(id=item_id).first()
            if item.name != item_name:
                item.name = item_name
            if item.platform != item_platform:
                item.platform = item_platform
            if item.price != item_price:
                item.price = item_price
            if item.img_name != item_img:
                item.img_name = item_img
            db.session.commit()
            flash('Sikeres módosítás!', 'success')
            if item.platform == 'PS4' or item.platform == 'PS5':
                return redirect(url_for('view.playstation'))
            else:
                return redirect(url_for('view.xbox'))

    if request.method == 'POST' and 'game_delete' in request.form:
        item_id = request.args.get('id')

        item = Item.query.filter_by(id=item_id).first()
        item.is_deleted = True
        db.session.commit()
        flash('Sikeres törlés!')
        if item.platform == 'PS4' or item.platform == 'PS5':
            return redirect(url_for('view.playstation'))
        else:
            return redirect(url_for('view.xbox'))

    if request.method == 'POST' and 'cancel' in request.form:
        if request.form.get('platform') == 'PS4' or request.form.get('platform') == 'PS5':
            return redirect(url_for('view.playstation'))
        else:
            return redirect(url_for('view.xbox'))

    return render_template('game_edit.html', user=current_user)
