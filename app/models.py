from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class NewInventory(db.Model):
    __tablename__ = 'new_inventory'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(20), nullable=False)
    units = db.Column(db.Integer, nullable=False)
    date_added = db.Column(db.DateTime, default = datetime.utcnow)

class DisbursedInventory(db.Model):
    __tablename__ = 'disbursed_inventory'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(20), nullable=False)
    units = db.Column(db.Integer, nullable=False)
    date_disbursed = db.Column(db.DateTime, default = datetime.utcnow)
    destination = db.Column(db.String(64), nullable=False)

class InStock(db.Model):
    __tablename__ = 'in_stock'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(20), nullable=False)
    units = db.Column(db.Integer, nullable=False)