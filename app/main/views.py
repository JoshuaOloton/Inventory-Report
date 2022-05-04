from flask import render_template, redirect, url_for, session, flash
from app.main import main
from app.models import NewInventory, DisbursedInventory, InStock
from app.main.forms import NewInventoryForm, DisburseInventoryForm
from app import db
from wtforms.validators import NumberRange, InputRequired

@main.route('/')
@main.route('/report')
def report():
    incoming = NewInventory.query.all()
    outgoing = DisbursedInventory.query.all()
    instock = InStock.query.all()
    return render_template('report.html', incoming=incoming, outgoing=outgoing, instock=instock)

@main.route('/inventory/new', methods=['GET', 'POST'])
def reimburse():
    form = NewInventoryForm()
    if form.validate_on_submit():
        inventory = NewInventory(item=form.item.data, units=form.units.data)
        db.session.add(inventory)
        # increment no of units in stock
        stock = InStock.query.filter_by(item=form.item.data).first()
        if not stock:
            stock = InStock(item=form.item.data, units = form.units.data)
            db.session.add(stock)
        else:
            stock.units += form.units.data
        db.session.commit()
        flash('Inventory has been reimbursed', 'success')
        return redirect(url_for('main.report'))
    return render_template('new_inventory.html', form=form)


@main.route('/inventory/disburse', methods=['GET', 'POST'])
def disburse():
    form = DisburseInventoryForm()
    if form.validate_on_submit():
        
        inventory = DisbursedInventory(item=form.item.data, units=form.units.data,
            destination = form.destination.data)
        db.session.add(inventory)
        stock = InStock.query.filter_by(item=form.item.data).first()
        if not stock:
            pass
        else:
            stock.units -= form.units.data
        db.session.commit()
        flash(f'{form.units.data} units of {form.item.data} has been disbursed to {form.destination.data}', 'success')
        return redirect(url_for('main.report'))
    return render_template('disburse_inventory.html', form=form)