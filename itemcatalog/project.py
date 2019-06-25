import os
from database_setup import Base, Owner, Restaurant, MenuItem
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask import Flask, render_template
from flask import url_for, request, redirect, flash, jsonify
from checker import login_required
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask import session as login_session
import random
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import string
import json
from flask import make_response
import requests
from sqlalchemy import create_engine

app = Flask(__name__)


CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']
APPLICATION_NAME = "Restaurant"

engine = create_engine("sqlite:///restaurantmenu.db",
                       connect_args={'check_same_thread': False},
                       echo=True)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# --------Login Example--------------
# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(
            string.ascii_uppercase +
            string.digits) for x in range(32))
    login_session['state'] = state
    restaurants = session.query(Restaurant).all()
    items = session.query(MenuItem).all()
    # return "The current session state is %s" % login_session['state']
    return render_template(
        'login.html',
        STATE=state,
        restaurants=restaurants,
        items=items)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
        access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return str("Hello" + response)

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
        print("***************************", user_id)
    login_session['user_id'] = user_id
    flash("LoggedIn Successfully...!", 'success')
    output = """
<div class='col-sm-offset-4'>
<div class='col-sm-5'>
<div class="panel panel-info animated bounce infinite">
<div class="panel-body">
<center>
<img src='""" + login_session['picture'] + """' style="width:\
 100px; height: 100px;border-radius: 50%;">
</center>
<h3 class="text-center text-info">"""+login_session['username'] + """ <h3>
</div>
</div>
</div>
</div>
    """
    return output

    # DISCONNECT - Revoke a current user's token and reset their login_session


def createUser(login_session):
    newUser = Owner(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(Owner).filter_by(
        email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(Owner).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(Owner).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None

# @app.route('/gdisconnect')


@app.route('/logout')
def gdisconnect():
    access_token = login_session['access_token']
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    if access_token is None:
        print('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s\
    ' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Your Logged Out Successfully...!", "info")
        return redirect('/')
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.',400))
        response.headers['Content-Type'] = 'application/json'
        return response

# ------ Ending  Login & Logout  -----------


photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/upload_files'
configure_uploads(app, photos)


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/posts')
def myposts():
    return render_template("sample.html", myPosts=posts)


@app.route("/restaurants")
def showRestaurants():
    restaurants = session.query(Restaurant).all()
    return render_template("restaurants.html", myRestaurants=restaurants)


@app.route('/restaurants/JSON')
def restaurantsJSON():
    resta = session.query(Restaurant).all()
    return jsonify(restaurant=[r.serialize for r in resta])


# To read Menus JSON
@app.route('/restaurants/<int:rest_id>/menus/JSON')

def MenuitemsListJSON(rest_id):
    restaurant = session.query(Restaurant).filter_by(id=rest_id).first()
    menus = session.query(MenuItem).filter_by(restaurant_id=rest_id).all()
    return jsonify(MenusLists=[i.serialize for i in menus])


# To read MenuItems wise of Restaurant JSON
@app.route('/restaurants/<int:rest_id>/menu/<int:menu_id>/JSON')

def restaurantListJSON(rest_id, menu_id):
    getMenu = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(menuList=getMenu.serialize)

# Users Json


@app.route('/users/JSON')
def usersJSON():
    users_list = session.query(Owner).all()
    return jsonify(restaurant=[r.serialize for r in users_list])


@app.route('/add_restaurant', methods=["GET", "POST"])

def addRestaurant():
    if request.method == "POST":
        filename = photos.save(request.files['photo'])
        restaurant = Restaurant(
            name=request.form['name'],
            image=filename,
            owner_id=login_session['user_id'])
        session.add(restaurant)
        session.commit()
        flash("New Restaurant Created", 'primary')
        return redirect('/restaurants')
    else:
        return render_template("addRestaurant.html")


@app.route('/edit_Restaurant/<int:rest_id>', methods=["GET", "POST"])

def editRestaurant(rest_id):
    editRest = session.query(Restaurant).filter_by(id=rest_id).one()
    creator = getUserInfo(editRest.owner_id)
    user = getUserInfo(login_session['user_id'])
    if creator.id != login_session['user_id']:
        flash("You cannot edit this category.This is belogs to %s",creator.name)
        return redirect(url_for('showRestaurants'))

    if request.method == "POST":
        print('------------------------------------', len(request.files))
        if 'photo' in request.files:
            filename = photos.save(request.files['photo'])
            editRest = session.query(Restaurant).filter_by(id=rest_id).one()
            editRest.name = request.form['name']
            editRest.image = filename
            editRest.owner_id = login_session['user_id']
            session.commit()
            flash("Edited Restaurant", "info")
            return redirect('/restaurants')
        else:
            
            editRest.name = request.form['name']
            editRest.owner_id = login_session['user_id']
            session.commit()
            flash("Edited Restaurant", "info")
            return redirect('/restaurants')
    else:
        editRest = session.query(Restaurant).filter_by(id=rest_id).one()
        return render_template("editRestaurant.html", editRest=editRest)


@app.route('/confirmDel_restaurant/<int:rest_id>', methods=["GET"])

def confirmDeleteRestaurant(rest_id):
    delRest = session.query(Restaurant).filter_by(id=rest_id).first()
    creator = getUserInfo(delRest.owner_id)
    user = getUserInfo(login_session['user_id'])
    if creator.id != login_session['user_id']:
        flash("You cannot edit this category.This is belongs to %s",creator.name)
        return redirect(url_for('showRestaurants'))
    deleteRes = session.query(Restaurant).filter_by(id=restaurant_id).one()
    return render_template("deleteRestaurant.html", deleteRestaurant=deleteRes)


@app.route('/del_restaurant/<int:restaurant_id>', methods=["GET"])

def deleteRestaurant(restaurant_id):
    """__________________________________________"""
    resToDelete = session.query(
        Restaurant).filter_by(name=Restaurant.name).one()
    # See if the logged in user is the owner of item
    creator = getUserInfo(resToDelete.owner_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot delete this Category."
              "This Category belongs to %s" % creator.name)
        return redirect(url_for('showRestaurants'))
    """__________________________________________"""

    # creator = getUserInfo(deleteRes.owner_id)
    # user = getUserInfo(login_session['user_id'])
    # # If logged in user != item owner redirect them
    # if creator.id != login_session['user_id']:
    #     flash("You cannot delete this Category."
    #           "This Category belongs to %s" % creator.name)
    #     return redirect(url_for('showRestaurants'))
    try:
        imagePath = './static/upload_files/' + delFolderImage.image
        os.remove(imagePath)
    except Exception as e:
        return redirect('/restaurants')
    flash("Deleted Restaurant", "info")
    return redirect('/restaurants')


@app.route("/menuItems/<int:restaurant_id>", methods=["GET"])

def RestaurantMenuItems(restaurant_id):
    menuItems = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)

    return render_template(
        "menuItems.html",
        items=menuItems,
        restaurant_id=restaurant_id)


@app.route("/addMenuItems/<int:rest_id>", methods=["POST", "GET"])

def addMenuItems(rest_id):
    if request.method == "POST":
        items = MenuItem(name=request.form['name'],
                         price=request.form['price'],
                         description=request.form['description'],
                         restaurant_id=request.form['restId'],
                         owner_id=login_session['user_id']
                         )
        # print("------------------",items)
        session.add(items)
        session.commit()
        return redirect('/menuItems/' + str(rest_id))
    else:
        getRes = session.query(Restaurant).filter_by(id=rest_id).first()
        if getRes.owner_id == login_session['user_id']:
            return render_template("add_menu_item.html", rest_id=rest_id)
        else:
            flash("Your Not Authorize Person to do this Operation...! ")
            return redirect('/menuItems/' + str(rest_id))


@app.route("/editMenuItems/<int:item_id>", methods=["POST", "GET"])

def editMenuItems(item_id):
    itemsData = session.query(MenuItem).filter_by(id=item_id).first()
    creator = getUserInfo(itemsData.owner_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this item. "
              "This item belongs to %s" % creator.name)
        return redirect(url_for('showRestaurants'))
    if request.method == "POST":
        items = session.query(MenuItem).filter_by(id=item_id).one()
        items.name = request.form['name']
        items.price = request.form['price']
        items.description = request.form['description']
        items.restaurant_id = request.form['restId']

        session.commit()
        # print("------------------",items)
        # session.add(items)
        # session.commit()
        return redirect('/menuItems/' + str(request.form['restId']))
    else:
        itemsData = session.query(MenuItem).filter_by(id=item_id).first()
        return render_template("edit_menu_item.html", itemsData=itemsData)


@app.route('/confirmDel_MenuItem/<int:item_id>', methods=["GET"])

def confirmDeleteMenu(item_id):
    deleteItem = session.query(MenuItem).filter_by(id=item_id).one()
    return render_template("confirmDeleteMenu.html", itemDelete=deleteItem)


@app.route('/Del_MenuItem/<int:item_id>', methods=["GET"])

def deleteMenu(item_id):
    deleteRest = session.query(MenuItem).filter_by(id=item_id).one()
    deleteRestId = deleteRest.restaurant_id
    deleteItem = session.query(MenuItem).filter_by(id=item_id)
    deleteItem.delete()
    session.commit()
    creator = getUserInfo(deleteRest.owner_id)
    user = getUserInfo(login_session['user_id'])
    # If logged in user != item owner redirect them
    if creator.id != login_session['user_id']:
        flash("You cannot edit this item. "
              "This item belongs to %s" % creator.name)
        return redirect(url_for('showRestaurants'))
    return redirect('/menuItems/' + str(deleteRestId))


if __name__ == "__main__":
    app.config['SECRET_KEY'] = 'e7a9804ba98684deefd88d6a6c8cd0db'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
