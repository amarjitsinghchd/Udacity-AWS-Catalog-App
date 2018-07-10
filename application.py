from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, CatalogItems, User
from forms import AddItemForm, AddCatalogForm
import requests

import os, sys

# New imports. These are for log in 
from flask import session as login_session
import random
import string

# IMPORTS FOR Oauth2.0
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response

import google.oauth2.credentials
import google.auth

# Added to support Google APIs fro token verification.
# This results will conflict with http results from
# python
from google.oauth2 import id_token
#from google.auth.transport import requests

app = Flask(__name__)

app.config['SECRET_KEY'] = "this is temp store in env for prod"


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu App"

engine = create_engine('sqlite:///catalog.db', echo = True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    print "statedr log in with state as %s", state
    return render_template('login.html', STATE=state)
    

@app.route('/gconnect', methods=['POST'])
def gconnect():
    
  #print "Entered GConnect"
  #token = data.get('id_token')
  #state = data.get('state')
  
  state = request.args.get('state') 

   # Validate state token
    # Verify the state key for Cross site forgery attack
  if state != login_session['state']:
    response = make_response(json.dumps('Invalid state parameter.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response


  # Obtain authorization code
  #code = data.get('code')
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
  url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
  h = httplib2.Http()
  result = json.loads(h.request(url, 'GET')[1])
  # If there was an error in the access token info, abort.
  if result.get('error') is not None:
    response = make_response(json.dumps(result.get('error')), 500)
    response.headers['Content-Type'] = 'application/json'
    return response

    # Verify that the access token is used for the intended user.
  google_id = credentials.id_token['sub']
  if result['user_id'] != google_id:
    response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
    response.headers['Content-Type'] = 'application/json'
    return response

  # Verify that the access token is valid for this app.
  if result['issued_to'] != CLIENT_ID:
    response = make_response(json.dumps("Token's client ID does not match app's."), 401)
    print "Token's client ID does not match app's."
    response.headers['Content-Type'] = 'application/json'
    return response


  stored_access_token = login_session.get('access_token')
  stored_google_id = login_session.get('google_id')
  if stored_access_token is not None and google_id == stored_google_id:
    response = make_response(json.dumps('Current user is already connected.'),200)
    response.headers['Content-Type'] = 'application/json'
    return response

  # Store the access token in the session for later use.
  login_session['access_token'] = credentials.access_token
  login_session['google_id'] = google_id
  
  # Get user info
  userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
  params = {'access_token': credentials.access_token, 'alt': 'json'}
  answer = requests.get(userinfo_url, params)

  data = answer.json()

  login_session['username'] = data['name']
  login_session['picture'] = data['picture']
  login_session['email'] = data['email']
  login_session['provider'] = 'google'

  # see if user exists, if it doesn't make a new one
  user_id = getUserID(data["email"])
  if not user_id:
    user_id = createUser()
  
  login_session['user_id'] = user_id

  output = ''
  output += '<h1>Welcome, '
  output += login_session['username']
  output += '!</h1>'
  output += '<img src="'
  output += login_session['picture']
  output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
  flash("you are now logged in as %s" % login_session['username'])
  print "done!"
  return output


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
      response = make_response(json.dumps('Current user not connected.'), 401)
      response.headers['Content-Type'] = 'application/json'
      return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
      response = make_response(json.dumps('Successfully disconnected.'), 200)
      response.headers['Content-Type'] = 'application/json'
      return response
    else:
      response = make_response(json.dumps('Failed to revoke token for given user.', 400))
      response.headers['Content-Type'] = 'application/json'
      return response

@app.route('/')
def catalog_main():
  catalogs = session.query(Catalog).all()
  catalog_id = catalogs[0].id
  items = session.query(CatalogItems).filter_by(catalog_id=catalog_id).all()
  active_catalog = session.query(Catalog).filter_by(id = catalog_id).all()
  creator = getUserInfo(catalogs[0].user_id)
  if 'username' not in login_session:
    user_logged = False
    user_edit = False
  elif creator.id != login_session['user_id']:
    user_logged = True
    user_edit = False
  else:
    user_logged = True
    user_edit = True
  
  return render_template('main.html', catalogs=catalogs, items=items,catalog_id = catalog_id, 
    active_catalog=active_catalog, user_logged = user_logged, user_edit = user_edit)
  
@app.route('/catalog/<int:catalog_id>')
def catalog_select(catalog_id):
	# catalogs = session.query(Catalog).filter_by(id = catalog_id).one()
  catalogs = session.query(Catalog).all()
  items = session.query(CatalogItems).filter_by(catalog_id=catalog_id).all()
  active_catalog = session.query(Catalog).filter_by(id = catalog_id).all()
  creator = getUserInfo(active_catalog[0].user_id)
 
  if 'username' not in login_session:
    user_logged = False
    user_edit = False
  elif creator.id != login_session['user_id']:
    user_logged = True
    user_edit = False
  else:
    user_logged = True
    user_edit = True
  return render_template('main.html', catalogs=catalogs, items=items,catalog_id = catalog_id, active_catalog=active_catalog, user_logged = user_logged, user_edit = user_edit)

@app.route('/catalog/deleteMenu')
def delete_catalogmenu():
  
  if 'username' not in login_session:
    return redirect(url_for('showLogin'))
  
  catalogs = session.query(Catalog).all()
  for icatalog in catalogs:
    if icatalog.user_id == login_session['user_id']:
      icatalog.delete_allowed = 1
    else:
      icatalog.delete_allowed = 0
  return render_template('catalogdelete.html', catalogs = catalogs)
   


@app.route('/delete/catalog/<int:catalog_id>')
def delete_catalog(catalog_id):
   # catalogs = session.query(Catalog).filter_by(id = catalog_id).one()

  catalogtodelete = session.query(Catalog).filter_by(id=catalog_id).one()
  if 'username' not in login_session:
    return redirect(url_for('showLogin'))
  if catalogtodelete.user_id != login_session['user_id']:
    return "<script>function myFunction() {alert('You are not authorized to delete this catalog. Please create your own catalog in order to delete.');}</script><body onload='myFunction()'>"

  try:
    items = session.query(Catalog).filter_by(id=catalog_id).delete(synchronize_session=False)
    session.commit()
  except:
    session.rollback()
  finally:
    return redirect(url_for('catalog_main'))
      #session.close()

@app.route('/delete/<int:catalog_id>/<int:item_id>/')
def delete_item(catalog_id, item_id):
   # catalogs = session.query(Catalog).filter_by(id = catalog_id).one()

  catalogtodelete = session.query(Catalog).filter_by(id=catalog_id).one()
  if 'username' not in login_session:
    return redirect(url_for('showLogin'))
  if catalogtodelete.user_id != login_session['user_id']:
    return "<script>function myFunction() {alert('You are not authorized to delete this catalog. Please create your own catalog in order to delete.');}</script><body onload='myFunction()'>"

  try:
    items = session.query(CatalogItems).filter_by(id=item_id).delete(synchronize_session=False)
    session.commit()
  except:
    session.rollback()
  finally:
    return redirect(url_for('catalog_select', catalog_id = catalog_id))
      #session.close()


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token


    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]


    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v3.0/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v3.0/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v3.0/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]


    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser()
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
  if 'provider' in login_session:
    if login_session['provider'] == 'google':
      gdisconnect()
      del login_session['access_token']
      del login_session['google_id']
    
    if login_session['provider'] == 'facebook':
      fbdisconnect()
      del login_session['facebook_id']

    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['provider']
    flash("You have successfully been logged out.")
    return redirect(url_for('catalog_main'))
  else:
    flash("You were not logged in")
    return redirect(url_for('catalog_main'))


@app.route('/addcatalog/', methods = ['GET', 'POST'])
def add_catalog():
   
  if 'username' not in login_session:
    return redirect(url_for('showLogin'))
  
  form = AddCatalogForm()


  if form.validate_on_submit():
      #print "form ok"
      #print form.name.data
      #print form.description.data
#      temp = CatalogItems(name = form.name, description = form.description,
 #        catalog_id = catalog_id)
      temp = Catalog(name = form.name.data, user_id = login_session['user_id'])
      session.add(temp)
      session.commit()
      current_catalog = session.query(Catalog).filter_by(name= form.name.data).all()
      catalog_id = current_catalog[0].id
      # print "item saved"
      return redirect(url_for('catalog_select', catalog_id = catalog_id))
      #return render_template('additemsuccess.html')
  else:
      #print "first time form render"
      return render_template('addcatalog.html', form = form)
   
      #session.close()

  catalogs = session.query(Catalog).all()
  items = session.query(CatalogItems).filter_by(catalog_id=catalog_id).all()
  return render_template('main.html', catalogs=catalogs,items=items,catalog_id = catalog_id, active_catalog=active_catalog)

@app.route('/editcatalog/<int:catalog_id>/', methods=['GET', 'POST'])
def edit_catalog(catalog_id):

  active_catalog = session.query(Catalog).filter_by(id = catalog_id).all()
   
  if 'username' not in login_session:
    return redirect(url_for('showLogin'))
  
  if active_catalog[0].user_id != login_session['user_id']:
    return "<script>function myFunction() {alert('You are not authorized to edit this item. Please create your own catalog in order to add.');}</script><body onload='myFunction()'>"

  form = AddCatalogForm(request.values, item_id = active_catalog[0].id, name = active_catalog[0].name)
  
  if form.validate_on_submit():

    try:
      session.query(Catalog).filter(Catalog.id == form.item_id.data).update({'name': form.name.data})
      session.commit()
      flash('Item Successfully Edited')
    except:
      session.rollback
      flash('Item edit Aborted')
    
    return redirect(url_for('catalog_select', catalog_id = catalog_id))
  else:
    return render_template('addcatalog.html', form = form)


@app.route('/additem/<int:catalog_id>/', methods = ['GET', 'POST'])
def add_item(catalog_id):
   # catalogs = session.query(Catalog).filter_by(id = catalog_id).one()
  active_catalog = session.query(Catalog).filter_by(id = catalog_id).all()
   
  if 'username' not in login_session:
    return redirect(url_for('showLogin'))

  if active_catalog[0].user_id != login_session['user_id']:
    return "<script>function myFunction() {alert('You are not authorized to add item to this catalog. Please create your own catalog in order to add.');}</script><body onload='myFunction()'>"

  
  form = AddItemForm()

  if form.validate_on_submit():
      #print "form ok"
      #print form.name.data
      #print form.description.data
#      temp = CatalogItems(name = form.name, description = form.description,
 #        catalog_id = catalog_id)
    temp = CatalogItems(name = form.name.data, description = form.description.data,catalog_id = catalog_id)
    session.add(temp)
    session.commit()

      # print "item saved"
    return redirect(url_for('catalog_select', catalog_id = catalog_id))
      #return render_template('additemsuccess.html')
  else:
      #print "first time form render"
    return render_template('additem.html', form = form, active_catalog = active_catalog)
   
      #session.close()

  catalogs = session.query(Catalog).all()
  items = session.query(CatalogItems).filter_by(catalog_id=catalog_id).all()
  return render_template('main.html', catalogs=catalogs,items=items,catalog_id = catalog_id, active_catalog=active_catalog)

@app.route('/edititem/<int:catalog_id>/menu/<int:item_id>/', methods=['GET', 'POST'])
def edit_item(catalog_id, item_id):
  active_catalog = session.query(Catalog).filter_by(id = catalog_id).all()
   
  if 'username' not in login_session:
    return redirect(url_for('showLogin'))
  
  if active_catalog[0].user_id != login_session['user_id']:
    return "<script>function myFunction() {alert('You are not authorized to edit this item. Please create your own catalog in order to add.');}</script><body onload='myFunction()'>"

  editedItem = session.query(CatalogItems).filter_by(catalog_id=catalog_id, id = item_id).one()
  
  form = AddItemForm(request.values, item_id = item_id, name = editedItem.name, description = editedItem.description)
  #if request.method == 'GET':
  #  form.item_id.data = item_id
   # form.name.data = editedItem.name
  #  form.description.data = editedItem.description

  if form.validate_on_submit():

    try:
      session.query(CatalogItems).filter(CatalogItems.id == form.item_id.data).update({'name': form.name.data, 'description':form.description.data})
      session.commit()
      flash('Item Successfully Edited')
    except:
      session.rollback
      flash('Item edit Aborted')
    
    return redirect(url_for('catalog_select', catalog_id = catalog_id))
  else:
    return render_template('additem.html', form = form, active_catalog = active_catalog)


# User Helper functions

def createUser():
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

#session.close()

# JSON APIs to view Catalog Information
@app.route('/catalog/<int:catalog_id>/JSON')
@app.route('/catalog/<int:catalog_id>/json')
def catalogitemsJSON(catalog_id):
  items = session.query(CatalogItems).filter_by(catalog_id=catalog_id).all()
  return jsonify(CatalogItems=[i.serialize for i in items])


@app.route('/catalog/<catalog_name>/JSON')
@app.route('/catalog/<catalog_name>/json')
def catalogitemnameJSON(catalog_name):
  catalog = session.query(Catalog).filter(func.lower(Catalog.name)==func.lower(catalog_name)).one()
  catalog_id = catalog.id
  items = session.query(CatalogItems).filter_by(catalog_id=catalog_id).all()
  return jsonify(CatalogItems=[i.serialize for i in items])

@app.route('/catalog/<int:catalog_id>/<int:item_id>/JSON')
@app.route('/catalog/<int:catalog_id>/<int:item_id>/json')
def catalogItemJSON(catalog_id, item_id):
  items = session.query(CatalogItems).filter_by(catalog_id=catalog_id, id = item_id).all()
  return jsonify(CatalogItems=[i.serialize for i in items])

@app.route('/catalog/<catalog_name>/<item_name>/JSON')
@app.route('/catalog/<catalog_name>/<item_name>/json')
def catalogItemnameJSON(catalog_name, item_name):
  catalog_name = catalog_name.lower()
  item_name = item_name.lower()
  catalog = session.query(Catalog).filter(func.lower(Catalog.name)==catalog_name).one()
  catalog_id = catalog.id
  items = session.query(CatalogItems).filter((CatalogItems.catalog_id==catalog_id) & (func.lower(CatalogItems.name) == item_name)).all()
  return jsonify(CatalogItems=[i.serialize for i in items])


@app.route('/catalogs/JSON')
@app.route('/catalogs/json')
def catalogsJSON():
    catalogs = session.query(Catalog).all()
    return jsonify(catalogs=[r.serialize for r in catalogs])


if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
 