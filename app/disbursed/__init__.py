from flask import Blueprint

disbursed = Blueprint('disbursed', __name__)

from app.disbursed import views