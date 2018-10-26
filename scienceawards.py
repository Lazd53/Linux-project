from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from databaseSetup import Base, Award, Bio, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# create engine and connect to database
engine = create_engine('sqlite:///sciawards.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Awards in Science"


# Login page
@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Connection for Google
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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('User already connected.'), 200)
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

    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if user_id:
        login_session['user_id'] = user_id
    if not user_id:
        user_id = createUser(login_session)
        login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    # output += login_session['user_id']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 200px; height: 200px; border-radius: 100px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    return output

# User Helper Functions


def createUser(login_session):
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
    except NoResultFound:
        return None


# Disconnect from Google
@app.route('/gdisconnect/')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    print(url)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('startPage'))
    else:
        # If the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Home/Welcome page
@app.route('/')
@app.route('/awards/')
def startPage():
    awards = session.query(Award).order_by(Award.name)
    if 'username' not in login_session:
        return render_template('home.html', awards=awards)
    else:
        return render_template(
            'home.html', awards=awards,
            # provide login information to user
            # similar in all further functions
            loginName=login_session['username'],
            loginPic=login_session['picture'],
            loginID=login_session['user_id'],)


# newAward
@app.route('/awards/new/', methods=['GET', 'POST'])
def newAward():
    awards = session.query(Award).order_by(Award.name)
    if 'user_id' not in login_session:
        return redirect('/login/')
    if request.method == 'POST':
        newAward = Award(name=request.form['name'],
                         description=request.form['description'],
                         user_id=login_session['user_id'])
        session.add(newAward)
        session.commit()
        return redirect(url_for('startPage'))
    else:
        return render_template('newAward.html', awards=awards)


# Individual award
@app.route('/awards/<int:award_id>/')
def award(award_id):
    awards = session.query(Award).order_by(Award.name)
    award = session.query(Award).filter_by(id=award_id).one()
    bios = session.query(Bio).filter_by(award_id=award_id).order_by(Bio.year)
    if 'username' not in login_session:
        return render_template('awards.html',
                               awards=awards, award=award, bios=bios)
    else:
        return render_template('awards.html',
                               awards=awards, award=award,
                               bios=bios,
                               loginName=login_session['username'],
                               loginPic=login_session['picture'],
                               loginID=login_session['user_id'])


# Edit individual award
@app.route('/awards/<int:award_id>/edit', methods=['GET', 'POST'])
def editAward(award_id):
    awards = session.query(Award).order_by(Award.name)
    award = session.query(Award).filter_by(id=award_id).one()
    userID = award.user_id
    if 'user_id' not in login_session:
        return redirect('/login/')
    if login_session['user_id'] != userID:
        return redirect(url_for('award', award_id=award.id))
    if request.method == 'POST':
        if request.form['name']:
            award.name = request.form['name']
        if request.form['description']:
            award.description = request.form['description']
        session.add(award)
        session.commit()
        return redirect(url_for('award', award_id=award.id))
    else:
        return render_template('editaward.html',
                               awards=awards, award=award,
                               loginName=login_session['username'],
                               loginPic=login_session['picture'],
                               loginID=login_session['user_id'])


# Delete individual award
@app.route('/awards/<int:award_id>/delete', methods=['GET', 'POST'])
def deleteAward(award_id):
    awards = session.query(Award).order_by(Award.name)
    award = session.query(Award).filter_by(id=award_id).one()
    userID = award.user_id
    affectedBios = session.query(Bio).filter_by(award_id=award_id).all()
    if 'user_id' not in login_session:
        return redirect('/login/')
    if login_session['user_id'] != userID:
        return redirect(url_for('award', award_id=award.id))
    if request.method == 'POST':
        session.delete(award)
        affectedBios = session.query(Bio).filter_by(award_id=award_id).delete()
        session.commit()
        return redirect(url_for('startPage'))
    else:
        return render_template('deleteAward.html',
                               awards=awards, award=award,
                               loginName=login_session['username'],
                               loginPic=login_session['picture'],
                               loginID=login_session['user_id'])


# See biography page
@app.route('/awards/<int:award_id>/bio/<int:bio_id>/')
def bio(award_id, bio_id):
    awards = session.query(Award).order_by(Award.name)
    award = session.query(Award).filter_by(id=award_id).one()
    bio = session.query(Bio).filter_by(id=bio_id).one()
    if 'user_id' not in login_session:
        return render_template('bio.html', awards=awards, award=award, bio=bio)
    else:
        return render_template('bio.html',
                               awards=awards, award=award, bio=bio,
                               loginName=login_session['username'],
                               loginPic=login_session['picture'],
                               loginID=login_session['user_id'])


# New biography page
@app.route('/awards/<int:award_id>/newbio/', methods=['GET', 'POST'])
def newbio(award_id):
    awards = session.query(Award).order_by(Award.name)
    award = session.query(Award).filter_by(id=award_id).one()
    if 'user_id' not in login_session:
        return redirect('/login/')
    if request.method == 'POST':
        newBio = Bio(name=request.form['name'],
                     year=request.form['year'],
                     description=request.form['description'],
                     discipline=request.form['discipline'],
                     award_id=award_id,
                     user_id=login_session['user_id'])
        session.add(newBio)
        session.commit()
        return redirect(url_for('award', award_id=award_id))
    else:
        return render_template('newbio.html',
                               awards=awards, award=award,
                               loginName=login_session['username'],
                               loginPic=login_session['picture'],
                               loginID=login_session['user_id'])


# Edit biography page
@app.route('/awards/<int:award_id>/bio/<int:bio_id>/edit/',
           methods=['GET', 'POST'])
def editBio(award_id, bio_id):
    awards = session.query(Award).order_by(Award.name)
    award = session.query(Award).filter_by(id=award_id).one()
    bio = session.query(Bio).filter_by(id=bio_id).one()
    userID = bio.user_id
    if 'user_id' not in login_session:
        return redirect('/login/')
    if login_session['user_id'] != userID:
        return redirect(url_for('bio', award_id=award.id, bio_id=bio_id))
    if request.method == 'POST':
        if request.form['name']:
            bio.name = request.form['name']
        if request.form['year']:
            bio.year = request.form['year']
        if request.form['description']:
            bio.description = request.form['description']
        if request.form['discipline']:
            bio.discipline = request.form['discipline']
        session.add(bio)
        session.commit()
        return redirect(url_for('bio', award_id=award_id, bio_id=bio_id))
    else:
        return render_template('editbio.html',
                               awards=awards, award=award,
                               bio=bio, loginName=login_session['username'],
                               loginPic=login_session['picture'],
                               loginID=login_session['user_id'])


# Delete biography page
@app.route('/awards/<int:award_id>/bio/<int:bio_id>/delete/',
           methods=['GET', 'POST'])
def deleteBio(award_id, bio_id):
    awards = session.query(Award).order_by(Award.name)
    award = session.query(Award).filter_by(id=award_id).one()
    bio = session.query(Bio).filter_by(id=bio_id).one()
    userID = bio.user_id
    if 'user_id' not in login_session:
        return redirect('/login/')
    if login_session['user_id'] != userID:
        return redirect(url_for('award', award_id=award_id))
    if request.method == 'POST':
        session.delete(bio)
        session.commit()
        return redirect(url_for('award', award_id=award_id))

    else:
        return render_template(
            'deleteBio.html', awards=awards, award=award,
            bio=bio, loginName=login_session['username'],
            loginPic=login_session['picture'],
            loginID=login_session['user_id'])


# JSON APIs
@app.route('/awards/json/')
def awardsJSON():
    awards = session.query(Award).all()
    return jsonify(awards=[a.serialize for a in awards])


@app.route('/awards/<int:award_id>/json/')
def awardJSON(award_id):
    award = session.query(Award).filter_by(id=award_id).one()
    bios = session.query(Bio).filter_by(award_id=award_id).all()
    return jsonify(Bio=[bio.serialize for bio in bios])


@app.route('/awards/<int:award_id>/bio/<int:bio_id>/json/')
def bioJSON(award_id, bio_id):
    bio = session.query(Bio).filter_by(id=bio_id).one()
    return jsonify(bio=bio.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run()
