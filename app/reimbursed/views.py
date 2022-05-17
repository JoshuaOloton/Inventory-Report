from app.models import NewInventory, InStock
from app.reimbursed.forms import NewInventoryForm
from flask import flash, render_template, redirect, url_for, current_app, url_for, request, session
from app import db
from app.reimbursed import reimbursed
from sqlalchemy import func, and_
from datetime import datetime


def format_date(date, format):
    f = date.replace(' GMT', '')
    return datetime.strptime(f, format).date()

@reimbursed.route('/inventory/new', methods=['GET', 'POST'])
def reimburse():
    form = NewInventoryForm()
    if form.validate_on_submit():
        inventory = NewInventory(item=form.item.data.upper(), units=form.units.data, description=form.description.data)
        if not form.description.data:
            inventory.description = f'{form.units.data} units of {form.item.data}\'s'
        db.session.add(inventory)
        # increment no of units in stock
        stock = InStock.query.filter_by(item=form.item.data.upper()).first()
        if not stock:
            stock = InStock(item=form.item.data.upper(), units=form.units.data)
            db.session.add(stock)
        else:
            stock.units += form.units.data
        db.session.commit()
        flash(f'Inventory has been reimbursed with {form.units.data} units of {form.item.data.upper()}  ', 'success')
        return redirect(url_for('main.report'))
    return render_template('new_inventory.html', form=form)

@reimbursed.route('/inventory/new/report')
def reimbursed_summary():
    page = request.args.get('page', 1, type=int)
    pagination = NewInventory.query.paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    incoming = pagination.items
    return render_template('reimbursed_summary.html', pagination=pagination, incoming=incoming, filter=0)

# full unpaginated route read_html reads tables from
@reimbursed.route('/inventory/new/report/full')
def reimbursed_summary_full():
    incoming = NewInventory.query.all()
    return render_template('full_reimbursed_summary.html', incoming=incoming, filter=0)


@reimbursed.route('/inventory/new/report/<start_date>/<end_date>')
def reimbursed_summary_period(start_date, end_date):
    page = request.args.get('page', 1, type=int)
    n_filtr = func.date(NewInventory.date_added)

    # convert string date objects back to datetype
    format = "%m-%d-%y"
    start_date = datetime.strptime(start_date, format).date()
    end_date = datetime.strptime(end_date, format).date()

    print(f"Start datee: {start_date}, tyYpe: {type(start_date)}")
    print(f'End datee: {end_date}, tYype: {type(end_date)}')
    # format = "%a, %d %b %Y %H:%M:%S"

    if start_date and end_date:
        pagination = NewInventory.query.filter(and_(n_filtr >= start_date, n_filtr <= end_date)).paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)

    elif start_date and not end_date:
        # start_date = format_date(start_date, format)
        pagination = NewInventory.query.filter(n_filtr >= start_date).paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)

    elif not start_date and end_date:
        pagination = NewInventory.query.filter(n_filtr <= end_date).paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    elif not start_date and not end_date:
        pagination = NewInventory.query.paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)

    print(f"Start date: {start_date}, type: {type(start_date)}")
    print(f"End date: {end_date}, type: {type(end_date)}")
    incoming = pagination.items
    print(f'incoming: {incoming}')
    return render_template('reimbursed_summary.html', pagination=pagination, incoming=incoming, filter=1)


@reimbursed.route('/inventory/new/report/full/<start_date>/<end_date>')
def reimbursed_summary_period_full(start_date, end_date):
    page = request.args.get('page', 1, type=int)
    n_filtr = func.date(NewInventory.date_added)
    

    format = "%m-%d-%y"

    if start_date and end_date:
        start_date = datetime.strptime(start_date, format).date()
        end_date = datetime.strptime(end_date, format).date()
        print(f'{start_date}/{type(start_date)}')
        print(f'{end_date}/{type(end_date)}')
        incoming = NewInventory.query.filter(and_(n_filtr >= start_date, n_filtr <= end_date)).all()

    elif start_date and not end_date:
        start_date = datetime.strptime(start_date, format).date()
        incoming = NewInventory.query.filter(n_filtr >= start_date).all()

    elif not start_date and end_date:
        end_date = datetime.strptime(end_date, format).date()
        incoming = NewInventory.query.filter(n_filtr <= end_date).all()

    elif not start_date and not end_date:
        incoming = NewInventory.query.all()

    return render_template('full_reimbursed_summary.html', incoming=incoming, filter=1)