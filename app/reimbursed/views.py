from app.models import NewInventory, InStock
from app.reimbursed.forms import NewInventoryForm
from flask import flash, render_template, redirect, url_for, current_app, url_for, request, session, make_response
from app import db
from app.reimbursed import reimbursed
from sqlalchemy import func, and_
from datetime import datetime
from flask_sqlalchemy import Pagination


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




@reimbursed.route('/inventory/recieved/<start_date>/<end_date>')
def inventory_recieved(start_date, end_date):
    n_filtr = func.date(NewInventory.date_added)

    format = "%m-%d-%y"
    # if both date limits are provided, filter between dates
    if start_date and end_date:
        start_date = datetime.strptime(start_date, format).date()
        end_date = datetime.strptime(end_date, format).date()
        if start_date > end_date:
            flash('Start date must be earlier than end date', 'danger')
        incoming = NewInventory.query.filter(and_(n_filtr >= start_date,n_filtr <= end_date)).all()
    # if only end date is provided, filter out all queries after end date
    elif not start_date and end_date:
        end_date = datetime.strptime(end_date, format).date()   
        incoming = NewInventory.query.filter(n_filtr <= end_date).all()
    # if only start date is provided, filter out all queries before start date
    elif start_date and not end_date:
        start_date = datetime.strptime(start_date, format).date()
        incoming = NewInventory.query.filter(n_filtr >= start_date).all()
    elif not start_date and not end_date:   # if both dates are skipped, then query all records
        incoming=NewInventory.query.all()

    incoming_dict = {}
   
    for new in incoming:
        if new.item not in incoming_dict:
            incoming_dict[new.item] = new.units
        else:
            incoming_dict[new.item] += new.units

    # convert dictionary into lists of dictionaries
    incoming_list = []
    for item in incoming_dict:
        data_dict = {}
        data_dict['item'] = item
        data_dict['units'] = incoming_dict[item]
        incoming_list.append(data_dict)
    
    page = request.args.get('page', 1, type=int) 
    per_page=current_app.config['RECORDS_PER_PAGE']
    # get start and end index based on page number
    start = (page - 1) * per_page
    end = page * per_page
    items = incoming_list[start:end]
    pagination = Pagination(None, page, per_page, total=len(incoming_list),items=items)

    # set cookie of current url that'll be used by the download function to download the appopriate table
    resp = make_response(render_template('total_recieved.html', pagination=pagination))
    resp.set_cookie('url',request.url)
    return resp

@reimbursed.route('/inventory/recieved/<start_date>/<end_date>/full')
def inventory_recieved_full(start_date, end_date):
    n_filtr = func.date(NewInventory.date_added)

    format = "%m-%d-%y"

    # if both date limits are provided, filter between dates
    if start_date and end_date:
        start_date = datetime.strptime(start_date, format).date()
        end_date = datetime.strptime(end_date, format).date()
        if start_date > end_date:
            flash('Start date must be earlier than end date', 'danger')
        incoming = NewInventory.query.filter(and_(n_filtr >= start_date,n_filtr <= end_date)).all()
    # if only end date is provided, filter out all queries after end date
    elif not start_date and end_date:
        end_date = datetime.strptime(end_date, format).date()
        incoming = NewInventory.query.filter(n_filtr <= end_date).all()
    # if only start date is provided, filter out all queries before start date
    elif start_date and not end_date:
        start_date = datetime.strptime(start_date, format).date()
        incoming = NewInventory.query.filter(n_filtr >= start_date).all()
    elif not start_date and not end_date:   # if both dates are skipped, then query all records
        incoming=NewInventory.query.all()

    incoming_dict = {}
    for new in incoming:
        if new.item not in incoming_dict:
            incoming_dict[new.item] = new.units
        else:
            incoming_dict[new.item] += new.units
    return render_template('full_total_recieved.html', incoming_dict=incoming_dict)

@reimbursed.route('/inventory/new/report')
def reimbursed_summary():
    page = request.args.get('page', 1, type=int)
    pagination = NewInventory.query.paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    incoming = pagination.items

    # set cookie of current url that'll be used by the download function to download the appopriate table
    resp = make_response(render_template('reimbursed_summary.html', pagination=pagination, incoming=incoming, filter=0))
    resp.set_cookie('url', request.url)
    return resp

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

    if start_date and end_date:
        pagination = NewInventory.query.filter(and_(n_filtr >= start_date, n_filtr <= end_date)).paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)

    elif start_date and not end_date:
        # start_date = format_date(start_date, format)
        pagination = NewInventory.query.filter(n_filtr >= start_date).paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)

    elif not start_date and end_date:
        pagination = NewInventory.query.filter(n_filtr <= end_date).paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    elif not start_date and not end_date:
        pagination = NewInventory.query.paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)

    incoming = pagination.items
    # set cookie of current url that'll be used by the download function to download the appopriate table
    resp = make_response(render_template('reimbursed_summary.html', pagination=pagination, incoming=incoming, filter=1))
    resp.set_cookie('url', request.url)
    return resp


@reimbursed.route('/inventory/new/report/<start_date>/<end_date>/full')
def reimbursed_summary_period_full(start_date, end_date):
    page = request.args.get('page', 1, type=int)
    n_filtr = func.date(NewInventory.date_added)

    format = "%m-%d-%y"

    if start_date and end_date:
        start_date = datetime.strptime(start_date, format).date()
        end_date = datetime.strptime(end_date, format).date()
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