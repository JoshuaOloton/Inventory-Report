from faker import Faker
from app.models import NewInventory
from random import randint

fake = Faker()

def generate_data():
    for i in range(1000):
        new = NewInventory(
            item=  ,
            units = 
        )
