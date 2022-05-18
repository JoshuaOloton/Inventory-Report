from flask import render_template, redirect, url_for, session, flash, make_response, request, current_app
from app.main import main
from app.models import NewInventory, DisbursedInventory, InStock
from app.main.forms import ChooseDateForm
from app import db
from sqlalchemy import func, and_
import pandas as pd
from tkinter import Tk, filedialog
import os
from datetime import date, datetime

@main.route('/')
@main.route('/report')
def report():
    incoming = NewInventory.query.all()
    outgoing = DisbursedInventory.query.all()
    instock = InStock.query.all()
    resp = make_response(render_template('report.html', incoming=incoming, outgoing=outgoing, instock=instock))
    if request.cookies.get('start_date'):
        resp.set_cookie('start_date', '', 0)
    if request.cookies.get('end_date'):
        resp.set_cookie('end_date', '', 0)
    return resp

@main.route('/report/filter', methods=['GET','POST'])
def set_date():
    form = ChooseDateForm()
    instock = InStock.query.all()
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        # ADD START AND END DATES TO FLASK SESSION FOR USE LATER
        session['start_date'] = start_date
        session['end_date'] = end_date

        # AND SET THEM AS COOKIES AS WELL
        resp = make_response(redirect(url_for('.report_period')))
        
        resp.set_cookie('start_date', start_date.strftime("%m-%d-%y"))
        resp.set_cookie('end_date', end_date.strftime("%m-%d-%y"))
        return resp
    return render_template('set_date.html', form=form)


@main.route('/report/summary', methods=['GET','POST'])
def report_summary():
    page = request.args.get('page', 1, type=int)
    pagination = InStock.query.paginate(page, per_page=current_app.config['RECORDS_PER_PAGE'], error_out=False)
    instock = pagination.items
    return render_template('report_summary.html',pagination=pagination,instock=instock)


@main.route('/report/period', methods=['GET','POST'])
def report_period():
    n_filtr = func.date(NewInventory.date_added)
    d_filtr = func.date(DisbursedInventory.date_disbursed)

    start_date = request.cookies.get('start_date')
    end_date = request.cookies.get('end_date')

    format = "%m-%d-%y"

    start_date = datetime.strptime(start_date, format).date()
    end_date = datetime.strptime(end_date, format).date()

    print(f"Start datee: {start_date}, type: {type(start_date)}")
    print(f'End datee: {end_date}, type: {type(end_date)}')
    
    # if both date limits are provided, filter between dates
    if start_date and end_date:
        if start_date > end_date:
            flash('Start date must be earlier than end date', 'danger')
        incoming = NewInventory.query.filter(and_(n_filtr >= start_date,n_filtr <= end_date)).all()
        outgoing = DisbursedInventory.query.filter(and_(d_filtr >= start_date, d_filtr <= end_date)).all()
    # if only end date is provided, filter out all queries after end date
    elif not start_date and end_date:
        incoming = NewInventory.query.filter(n_filtr <= end_date).all()
        outgoing = DisbursedInventory.query.filter(d_filtr <= end_date).all()
    # if only start date is provided, filter out all queries before start date
    elif start_date and not end_date:
        incoming = NewInventory.query.filter(n_filtr >= start_date).all()
        outgoing = DisbursedInventory.query.filter(d_filtr >= start_date).all()
    elif not start_date and not end_date:   # if both dates are skipped, then query all records
        incoming=NewInventory.query.all()
        outgoing = DisbursedInventory.query.all()
        
    # total reimbursed and total disbursed within specified timeframe
    incoming_dict = {}
    outgoing_dict = {}
    for new in incoming:
        if new.item not in incoming_dict:
            incoming_dict[new.item] = new.units
        else:
            incoming_dict[new.item] += new.units
    for disbursed in outgoing:
        if disbursed.item not in outgoing_dict:
            outgoing_dict[disbursed.item] = disbursed.units
        else:
            outgoing_dict[disbursed.item] += disbursed.units
    return render_template('report_period.html',incoming=incoming, outgoing=outgoing, incoming_dict=incoming_dict, outgoing_dict=outgoing_dict)
    

@main.route('/download/<process>/<int:filter>')
def download(process, filter):
    # dynamic route process value indicates wich route to read html tables from
    root = Tk() # initialize Tk
    root.withdraw() # hides small tkinter window
    root.attributes('-topmost', True)

    base_url = 'http://127.0.0.1:5000'
    
    # these variables are used if filter is set to 1
    start_date = request.cookies.get('start_date')
    end_date = request.cookies.get('end_date')
    
    if process == 'reimburse':
        if filter == 0:
            next_url = '/inventory/new/report/full'
        else:
            print(f'{start_date}///{type(start_date)}')
            next_url = f'/inventory/new/report/full/{start_date}/{end_date}'
            print(f'next url: {next_url}')
    else:
        if filter == 0:
            next_url = '/inventory/disburse/report/full'
        else:
            next_url = f'/inventory/disburse/report/full/{start_date}/{end_date}'

    table = pd.read_html(f'{base_url}{next_url}')[0]
    filename = filedialog.asksaveasfile(defaultextension=".xlsx", 
                                        filetypes=[
                                            ("Excel File", ".xlsx"),
                                            ("CSV File", ".csv")
                                        ])
    try:
        table.to_excel(f'{filename.name}')
        flash(f'{os.path.basename(filename.name)}  successfully downloaded!', 'success')
        root.destroy()
    except AttributeError:
        return redirect(url_for('main.set_date'))
    # close file
    filename.close()
    root.mainloop()

    return redirect(url_for('main.report'))
