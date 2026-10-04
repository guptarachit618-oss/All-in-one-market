from run import app, Item

with app.app_context():
    for item in Item.query.all():
        print(item.name, item.price)