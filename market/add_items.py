from market import app, db
from market.models import Item
with app.app_context():
    item1 = Item(name='IPhone 17', price=1000, description='Latest flagship phone', barcode='893212299897', image_file='iphone.png')
    item2 = Item(name='HP Victus', price=1000, description='Gaming laptop', barcode='1345765454', image_file='victus.png')
    item3 = Item(name='Samsung S24', price=800, description='Flagship phone with great camera', barcode='111222333444',image_file='s24.png')
    item4 = Item(name='Dell XPS', price=1200, description='Dell Laptop', barcode='555666777888',image_file='xps.png')
    db.session.add(item1)
    db.session.add(item2)
    db.session.add(item3)
    db.session.add(item4)
    db.session.commit()
    print("Items added!")