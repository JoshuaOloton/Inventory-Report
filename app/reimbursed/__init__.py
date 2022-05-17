from flask import Blueprint

reimbursed = Blueprint('reimbursed', __name__)

from app.reimbursed import views