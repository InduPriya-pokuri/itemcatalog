from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Owner, Restaurant, MenuItem, Base
engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loades into the
# database session object. Any change made against the objests in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()

session = DBSession()

# Deleting OurUsers if existing.
session.query(Owner).delete()

# Deleting Restaurent if exisitng.
session.query(Restaurant).delete()

# Deleting MenuItem if exisitng.
session.query(MenuItem).delete()


# Dummy User
Owner1 = Owner(
    name="Indu Priya",
    email="pokuriindupriya36@gmail.com",
    picture="https://lh5.googleusercontent.com/\
            -R2p-y5sZ9RI/AAAAAAAAAAI/AAAAAAAAPsQ/\
            WZUQ0Htjijc/photo.jpg"
)
session.add(Owner1)
session.commit()

# Menu(list of Menu_Items) in  Ganesha  Restaurent

restaurent1 = Restaurant(
    name="Ganesha Restaurent",
    image='rec1.jpg',
    owner_id=1)
session.add(restaurent1)
session.commit()

# Pizza Menu_Item info
menu_item1 = MenuItem(
    name="Pizza",
    price=250,
    description="Pizza is another menu favorite that can be served"
    "plain with cheese and tomato sauce or topped with"
    "a variety of items. Traditional toppings include,"
    "pepperoni, sausage, and vegetables; while more"
    "trendy toppings include buffalo chicken, french"
    "fries, and salad. For those with more expensive"
    "tastes, there are gourmet pizzas available that"
    "feature truffles, caviar, gold, and diamonds."
    "Generally, pizza is a low cost, easily prepared"
    "menu item that is well suited for a casual dinner"
    "any night of the week.",
    restaurant_id=1,
    owner_id=1)
session.add(menu_item1)
session.commit()


# South_Indian mimi meals Menu_Item  info

menu_item2 = MenuItem(name="South_Indian mini meals",
                      price=250,
                      description="1/4 kg white rice ,Pappu,Pickel,"
                      "Sambar,Rasam,Papad,Curd,Special"
                      "Curries",
                      restaurant_id=1,
                      owner_id=1)
session.add(menu_item2)
session.commit()

menu_item3 = MenuItem(name="Pizza",
                      price=250,
                      description="1/4 kg white rice ,Pappu,Pickel,"
                      "Sambar,Rasam,Papad,Curd,Special"
                      "Curries",
                      restaurant_id=1,
                      owner_id=1)
session.add(menu_item3)
session.commit()

print("All dump data added...!")
