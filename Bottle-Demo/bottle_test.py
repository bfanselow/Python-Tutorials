#!/usr/bin/env python
"""

  File: bottle_test.py
  Description:
    Simple demonstration of Bottle micro-web framework's basic functionality
    For more in-depth: https://bottlepy.org/docs/dev/index.html

"""
import os     
import bottle
from bottle import route, run, template, get, post, request
from bottle import static_file, redirect, view  

## custom libs
from controllers import *

## Views/template location
## Bottle will look for templates in the ./views/ dir or any dir specified in bottle.TEMPLATE_PATH 
## We can set these as relative paths (by default) or absolute paths. 
abs_app_dir_path = os.path.dirname(os.path.realpath(__file__))
abs_views_path = os.path.join(abs_app_dir_path, 'templates')
bottle.TEMPLATE_PATH.insert(0, abs_views_path )
 
##-----------------------------------------------------------------
## Supporting methods 
## (alternatively, can also put these into an imported file
##-----------------------------------------------------------------
#def check_login(name,pw):
#  status = False
#  if name == pw:
#    status = True
#  return( status )


##-----------------------------------------------------------------
## ROUTES
##-----------------------------------------------------------------
@route('/')
def index():
  return( "Welcome to bottle test")

##--------------------------
@route('/hello')
def hello():
  return( "Hello World!")

##--------------------------
## dynamic route
@route('/hello/<user>')
def hello(user):
  return( "Hello there: %s" % (user))

##--------------------------
## Overly dynamic route! Don't do this unless it is the very last route on the page.
## Route matching uses a first-match logic so any subsequent routes which also match 
## this "/<wildcard>/<wildcard>" pattern will be unusable.
##@route('/<greeting>/<user>')
##def greet(greeting, user):
##  return( "Hey %s, %s" % (user, greeting))

##--------------------------
## static files
@get('/login') # or @route('/login')
def login():
  return static_file('login_form.html', root='./static')

##--------------------------
## POST, form-handling
@post('/login') # or @route('/login', method='POST')
def do_login():
  username = request.forms.get('username')
  password = request.forms.get('password')
  if check_login(username, password):
    return "<p>Your login information was correct.</p>"
  else:
    return "<p>Login failed.</p>"

##--------------------------
## Serving up a static fil3
@route('/images/<filename:re:.*\.jpg>')
def send_image(filename):
  return static_file(filename, root='./static/images', mimetype='image/jpg')

##--------------------------
## Redirects
@route('/wrong/url')
def wrong():
  redirect("/right/url")
@route('/right/url')
def right():
  return( "Good job!")

##--------------------------
## Query strings: ./qstr?id=23&page=80
@route('/qstr')
def display_qstr():
  id = request.query.id
  page = request.query.page or '1'
  return template('Query Params:  ID={{id}} page={{page}}', id=id, page=page)

##--------------------------
## Request object attributes
@route('/my_ip')
def show_ip():
  ip = request.environ.get('REMOTE_ADDR')
  # or ip = request.get('REMOTE_ADDR')
  # or ip = request['REMOTE_ADDR']
  return template("Your IP is: {{ip}}", ip=ip) 

##--------------------------
## Simple-Teamplate-Engine
@route('/template')
@route('/template/<name>')
@view('hello_template')
def tpl_hello(name='World'):
  return dict(name=name) 

##-----------------------------------------------------------------
run(host='0.0.0.0', port=8080, debug=True)
