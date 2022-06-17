from flask import render_template, redirect, url_for, session, flash, make_response, request, current_app
from app.main import main
from app.models import NewInventory, DisbursedInventory, InStock
from app.main.forms import ChooseDateForm
from app import db
from sqlalchemy import func, and_
from datetime import date, datetime
import pandas as pd
import numpy as np
import os

@main.route('/')
@main.route('/report')
def report():
    incoming = NewInventory.query.all()
    outgoing = DisbursedInventory.query.all()
    instock = InStock.query.all()
    resp = make_response(render_template('report.html', incoming=incoming, outgoing=outgoing, instock=instock))

    # clear start and end date cookies
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

    # set cookie of current url that'll be used by the download function to download the appopriate table
    resp = make_response(render_template('report_summary.html',pagination=pagination,instock=instock, filter=0))
    resp.set_cookie('url', request.url)
    return resp

    
@main.route('/report/summary/full', methods=['GET','POST'])
def report_summary_full():
    instock = InStock.query.all()
    return render_template('full_report_summary.html', instock=instock)


@main.route('/report/period', methods=['GET','POST'])
def report_period():
    n_filtr = func.date(NewInventory.date_added)
    d_filtr = func.date(DisbursedInventory.date_disbursed)

    start_date = request.cookies.get('start_date')
    end_date = request.cookies.get('end_date')

    format = "%m-%d-%y"

    # if both date limits are provided, filter between dates
    if start_date and end_date:
        start_date = datetime.strptime(start_date, format).date()
        end_date = datetime.strptime(end_date, format).date()
        if start_date > end_date:
            flash('Start date must be earlier than end date', 'danger')
        incoming = NewInventory.query.filter(and_(n_filtr >= start_date,n_filtr <= end_date)).all()
        outgoing = DisbursedInventory.query.filter(and_(d_filtr >= start_date, d_filtr <= end_date)).all()
    # if only end date is provided, filter out all queries after end date
    elif not start_date and end_date:
        end_date = datetime.strptime(end_date, format).date()
        incoming = NewInventory.query.filter(n_filtr <= end_date).all()
        outgoing = DisbursedInventory.query.filter(d_filtr <= end_date).all()
    # if only start date is provided, filter out all queries before start date
    elif start_date and not end_date:
        start_date = datetime.strptime(start_date, format).date()
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
    
    url = request.cookies.get('url')
    print(f'URL before: {url}')
    if '?' in url:
        index = url.index('?')
        url = url[:index]
    print(f'URL after: {url}')
    print(f'URL FULL: {url}/full')
    table = pd.read_html(f'{url}/full')[0]  # table is of type dataframe
    table.index = np.arange(1, len(table)+1)
    
    path=os.path.expanduser("~")+'\Downloads'
    
    if process == 'reimburse':
        filename = 'reimbursed.xlsx'
    elif process == 'disburse':
        filename = 'disbursed.xlsx'
    elif process == 'incoming':
        filename = 'incoming_inventory.xlsx'
    elif process == 'outgoing':
        filename = 'disbursed_inventory.xlsx'
    else:
        filename = 'report.xlsx'
    
    format = '%d-%b-%y_%H.%M.%S'
    now = datetime.now()
    filename = now.strftime(format) + '_' + filename

    table.to_excel(f'{path}\{filename}')
    flash(f'{filename} successfully downloaded!', 'success')

    if filter == 0:
        resp = make_response(redirect(url_for('main.report')))
    else:
        resp = make_response(redirect(url_for('main.report_period')))
    resp.set_cookie('url', '', 0)   # clear url cookie
    print(7)
    return resp
