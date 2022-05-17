from app.models import DisbursedInventory, InStock
from app.disbursed.forms import DisburseInventoryForm
from flask import flash, render_template, redirect, url_for, current_app, url_for, request, session
from app import db
from app.disbursed import disbursed
from sqlalchemy import func, and_
from datetime import datetime

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


@disbursed.route('/inventory/disburse/report')
def disbursed_summary():
    page = request.args.get('page', 1, type=int)
    pagination = DisbursedInventory.query.paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    outgoing = pagination.items
    # print(DisbursedInventory.query.all())
    return render_template('disbursed_summary.html', pagination=pagination, outgoing=outgoing, filter=0)
    # a 0 value of filter indicates that record are not date filtered, we pass this value to the download function to indicate the kind of records to be downloaded

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
    print(f'outgoing: {outgoing}')
    return render_template('disbursed_summary.html', pagination=pagination, outgoing=outgoing, filter = 1)
    # a 1 value of filter indicates that record are not date filtered, we pass this value to the download function to indicate the kind of records to be downloaded


@disbursed.route('/inventory/disburse/report/full/<start_date>/<end_date>')
def disbursed_summary_period_full(start_date, end_date):
    page = request.args.get('page', 1, type=int)
    d_filtr = func.date(DisbursedInventory.date_disbursed)

    format = "%m-%d-%y"
    start_date = datetime.strptime(start_date, format).date()
    end_date = datetime.strptime(end_date, format).date()

    if start_date and end_date:
        outgoing = DisbursedInventory.query.filter(and_(d_filtr >= start_date, d_filtr <= end_date)).all()

    elif start_date and not end_date:
        outgoing = DisbursedInventory.query.filter(d_filtr >= start_date).all()

    elif not start_date and end_date:
        outgoing = DisbursedInventory.query.filter(d_filtr <= end_date).all()

    elif not start_date and not end_date:
        outgoing = DisbursedInventory.query.all()

    return render_template('full_disbursed_summary.html', outgoing=outgoing, filter=1)
