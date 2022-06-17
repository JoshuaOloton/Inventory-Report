from app.models import DisbursedInventory, InStock
from app.disbursed.forms import DisburseInventoryForm
from flask import flash, render_template, redirect, url_for, current_app, url_for, request, session, make_response
from app import db
from app.disbursed import disbursed
from sqlalchemy import func, and_
from datetime import datetime
from flask_sqlalchemy import Pagination

def format_date(date, format):
    f = date.replace(' GMT', '')
    return datetime.strptime(f, format).date()

@disbursed.route('/inventory/disburse', methods=['GET', 'POST'])
def disburse():
    form = DisburseInventoryForm()
    if form.validate_on_submit():
        inventory = DisbursedInventory(item=form.item.data, units=form.units.data, destination = form.destination.data, description=form.description.data)
        db.session.add(inventory)
        stock = InStock.query.filter_by(item=form.item.data).first()
        if not stock:   # technically this line isn't needed because we can only select items currently in stock
            pass
        else:
            stock.units -= form.units.data
        db.session.commit()
        flash(f'{form.units.data} units of {form.item.data} has been disbursed to {form.destination.data}', 'success')
        return redirect(url_for('main.report'))
    return render_template('disburse_inventory.html', form=form)


@disbursed.route('/inventory/disbursed/<start_date>/<end_date>')
def inventory_disbursed(start_date, end_date):
    d_filtr = func.date(DisbursedInventory.date_disbursed)

    format = "%m-%d-%y"
    # if both date limits are provided, filter between dates
    if start_date and end_date:
        start_date = datetime.strptime(start_date, format).date()
        end_date = datetime.strptime(end_date, format).date()
        if start_date > end_date:
            flash('Start date must be earlier than end date', 'danger')
        outgoing = DisbursedInventory.query.filter(and_(d_filtr >= start_date,d_filtr <= end_date)).all()
    # if only end date is provided, filter out all queries after end date
    elif not start_date and end_date:
        end_date = datetime.strptime(end_date, format).date()
        outgoing = DisbursedInventory.query.filter(d_filtr <= end_date).all()
    # if only start date is provided, filter out all queries before start date
    elif start_date and not end_date:
        start_date = datetime.strptime(start_date, format).date()
        outgoing = DisbursedInventory.query.filter(d_filtr >= start_date).all()
    elif not start_date and not end_date:   # if both dates are skipped, then query all records
        outgoing=DisbursedInventory.query.all()

    outgoing_dict = {}
    for disbursed in outgoing:
        if disbursed.item not in outgoing_dict:
            outgoing_dict[disbursed.item] = disbursed.units
        else:
            outgoing_dict[disbursed.item] += disbursed.units

    # convert dictionary into lists of dictionaries
    outgoing_list = []
    for item in outgoing_dict:
        data_dict = {}
        data_dict['item'] = item
        data_dict['units'] = outgoing_dict[item]
        outgoing_list.append(data_dict)

    page = request.args.get('page', 1, type=int) 
    per_page=current_app.config['RECORDS_PER_PAGE']
    # get start and end index based on page number
    start = (page - 1) * per_page
    end = page * per_page
    items = outgoing_list[start:end]
    pagination = Pagination(None, page, per_page, total=len(outgoing_list),items=items)

    # set cookie of current url that'll be used by the download function to download the appopriate table
    resp = make_response(render_template('total_disbursed.html', pagination=pagination))
    resp.set_cookie('url',request.url)
    return resp


@disbursed.route('/inventory/disbursed/<start_date>/<end_date>/full')
def inventory_disbursed_full(start_date, end_date):
    d_filtr = func.date(DisbursedInventory.date_disbursed)

    format = "%m-%d-%y"
    # if both date limits are provided, filter between dates
    if start_date and end_date:
        start_date = datetime.strptime(start_date, format).date()
        end_date = datetime.strptime(end_date, format).date()
        if start_date > end_date:
            flash('Start date must be earlier than end date', 'danger')
        outgoing = DisbursedInventory.query.filter(and_(d_filtr >= start_date,d_filtr <= end_date)).all()
    # if only end date is provided, filter out all queries after end date
    elif not start_date and end_date:
        end_date = datetime.strptime(end_date, format).date()
        outgoing = DisbursedInventory.query.filter(d_filtr <= end_date).all()
    # if only start date is provided, filter out all queries before start date
    elif start_date and not end_date:
        start_date = datetime.strptime(start_date, format).date()
        outgoing = DisbursedInventory.query.filter(d_filtr >= start_date).all()
    elif not start_date and not end_date:   # if both dates are skipped, then query all records
        outgoing=DisbursedInventory.query.all()

    outgoing_dict = {}
    for disbursed in outgoing:
        if disbursed.item not in outgoing_dict:
            outgoing_dict[disbursed.item] = disbursed.units
        else:
            outgoing_dict[disbursed.item] += disbursed.units

        
    return render_template('full_total_disbursed.html', outgoing_dict=outgoing_dict)


@disbursed.route('/inventory/disburse/report')
def disbursed_summary():
    page = request.args.get('page', 1, type=int)
    pagination = DisbursedInventory.query.paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    outgoing = pagination.items

    print(request.cookies.get('start_date'))
    # a 0 value of filter indicates that record are not date filtered, we pass this value to the download function to indicate the kind of records to be downloaded
    resp = make_response(render_template('disbursed_summary.html', pagination=pagination, outgoing=outgoing, filter=0))
    resp.set_cookie('url', request.url)
    return resp

# full unpaginated route read_html reads tables from
@disbursed.route('/inventory/disburse/report/full')
def disbursed_summary_full():
    outgoing = DisbursedInventory.query.all()
    return render_template('full_disbursed_summary.html', outgoing=outgoing, filter=0)

    
@disbursed.route('/inventory/disburse/report/<start_date>/<end_date>')
def disbursed_summary_period(start_date, end_date):
    page = request.args.get('page', 1, type=int)
    d_filtr = func.date(DisbursedInventory.date_disbursed)
   
    # convert string date objects back to datetype
    format = "%m-%d-%y"
    start_date = datetime.strptime(start_date, format).date()
    end_date = datetime.strptime(end_date, format).date()

    if start_date and end_date:
        pagination = DisbursedInventory.query.filter(and_(d_filtr >= start_date, d_filtr <= end_date)).paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)

    elif start_date and not end_date:
        pagination = DisbursedInventory.query.filter(d_filtr >= start_date).paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)

    elif not start_date and end_date:
        pagination = DisbursedInventory.query.filter(d_filtr <= end_date).paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
        
    elif not start_date and not end_date:
        pagination = DisbursedInventory.query.paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)

    outgoing = pagination.items
    # set cookie of current url that'll be used by the download function to download the appopriate table
    resp = make_response(render_template('disbursed_summary.html', pagination=pagination, outgoing=outgoing, filter = 1))
    resp.set_cookie('url', request.url)
    return resp
    # a 1 value of filter indicates that record are not date filtered, we pass this value to the download function to indicate the kind of records to be downloaded


@disbursed.route('/inventory/disburse/report/<start_date>/<end_date>/full')
def disbursed_summary_period_full(start_date, end_date):
    page = request.args.get('page', 1, type=int)
    d_filtr = func.date(DisbursedInventory.date_disbursed)

    format = "%m-%d-%y"

    if start_date and end_date:
        start_date = datetime.strptime(start_date, format).date()
        end_date = datetime.strptime(end_date, format).date()
        outgoing = DisbursedInventory.query.filter(and_(d_filtr >= start_date, d_filtr <= end_date)).all()

    elif start_date and not end_date:
        start_date = datetime.strptime(start_date, format).date()
        outgoing = DisbursedInventory.query.filter(d_filtr >= start_date).all()

    elif not start_date and end_date:
        end_date = datetime.strptime(end_date, format).date()
        outgoing = DisbursedInventory.query.filter(d_filtr <= end_date).all()

    elif not start_date and not end_date:
        outgoing = DisbursedInventory.query.all()

    return render_template('full_disbursed_summary.html', outgoing=outgoing, filter=1)
