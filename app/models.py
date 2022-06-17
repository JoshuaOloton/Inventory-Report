from datetime import datetime
from app import db

class NewInventory(db.Model):
    __tablename__ = 'new_inventory'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(20), nullable=False)
    units = db.Column(db.Integer, nullable=False)
    date_added = db.Column(db.DateTime, default = datetime.now)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'NewInv: {self.item}'

class DisbursedInventory(db.Model):
    __tablename__ = 'disbursed_inventory'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(20), nullable=False)
    units = db.Column(db.Integer, nullable=False)
    date_disbursed = db.Column(db.DateTime, default = datetime.now)
    destination = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'DisbInv: {self.item}'

class InStock(db.Model):
    __tablename__ = 'in_stock'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(20), nullable=False)
    units = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'Stock: {self.item}'