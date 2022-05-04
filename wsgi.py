from app import create_app, db
from app.models import NewInventory, DisbursedInventory, InStock

app = create_app('default')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, NewInventory=NewInventory, DisbursedInventory=DisbursedInventory, InStock=InStock, app=app)

if __name__ == "__main__":
    app.run(debug=True)