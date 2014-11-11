import os.path
import logging
from datetime import datetime
from time import strptime, mktime

import webapp2
import jinja2
from google.appengine.ext import ndb

import foo


template_dir = os.path.join(os.path.dirname(__file__), "templates").replace("\\", "/")
templateEnv = jinja2.Environment(
				loader=jinja2.FileSystemLoader(
				searchpath=template_dir), autoescape=True)


class User(ndb.Model):
	username = ndb.StringProperty(required=True)
	password = ndb.StringProperty(required=True)
	email = ndb.StringProperty()
	register = ndb.DateTimeProperty(auto_now_add=True)

class Task(ndb.Model):
	name = ndb.StringProperty(required=True)
	body = ndb.TextProperty(required=True)
	user = ndb.StringProperty(required=True)
	finish_time = ndb.DateTimeProperty(required=True)
	posted = ndb.DateTimeProperty(auto_now_add=True)
	checked = ndb.StringProperty(default="")

class Handler(webapp2.RequestHandler):
	def render(self, template, **params):
		temp = templateEnv.get_template(template)
		self.response.out.write(temp.render(**params))

	def user_get_current(self):
		return self.request.cookies.get("user_id")

	def user_login(self, username):
		self.response.set_cookie("user_id", value=username, path='/', )

	def user_logout(self):
		self.response.delete_cookie("user_id")

	def username_exists(self, name):
		pass


class MainPage(Handler):
	def get(self):
		self.render("main.html", username=self.user_get_current(), tasks = Task.query(Task.user == self.user_get_current()).order(-Task.posted).fetch())

	

class LoginPage(Handler):
	def get(self):
		if self.user_get_current():
			self.redirect("/")
		self.render("login.html")

	def post(self):
		if self.user_get_current():
			self.redirect("/")
		username = self.request.get("username")
		password = self.request.get("password")
		u_err, p_err = ("",)*2
		there_is_an_error = False
		user = User.query(User.username == username).fetch(1)

		if user:
			if user[0].password != password:
				p_err = "Wrong password!"
				there_is_an_error = True
		else:
			u_err = "Username not registered"
			there_is_an_error = True

		if there_is_an_error:
			self.render("login.html", username_post=username,
										username_error=u_err,
										password_error=p_err)
		else:
			self.user_login(username)
			self.redirect('/')




class RegisterPage(Handler):
	def get(self):
		if self.user_get_current():
			self.redirect("/")
		self.render("register.html")

	def post(self):
		if self.user_get_current():
			self.redirect("/")
		username = self.request.get("username")
		password = self.request.get("password")
		verify = self.request.get("verify")
		email = self.request.get("email")

		u_err, p_err, v_err, e_err= ('',)*4
		there_is_an_error = False
		if not foo.valid_username(username):
			u_err = "Invalid username"
			there_is_an_error = True
		if self.username_exists(username):
			u_err = "Username already exists"
			there_is_an_error = True
		if not foo.valid_password(password):
			p_err = "Invalid password"
			there_is_an_error = True
		if not p_err and password!=verify:
			v_err = "Doesn't match"
			there_is_an_error = True
		if not foo.valid_email(email):
			e_err = "Invalid email"
			there_is_an_error = True

		if there_is_an_error:
			self.render("register.html", username_post=username,
										username_error=u_err, 
										password_error=p_err, 
										verify_error=v_err, 
										email_error=e_err,
										email_post=email,
										)
		else:
			user = User(username=username, 
						password=password, 
						email=email,
						)
			user.put()
			self.user_login(username)
			self.redirect("/welcome")


class LogoutPage(Handler):
	def get(self):
		self.user_logout()
		self.redirect("/")


class WelcomePage(Handler):
	def get(self):
		self.render("welcome.html", username=self.user_get_current())

class UserPage(Handler):

	def get(self):
		user_id = self.user_get_current()
		user = User.query(User.username == user_id).fetch(1)

		if user:
			self.render("userpage.html", username=user[0].username, registered = user[0].register.strftime("%c"))
		else:
			self.render("userpage.html", registered = "No such user")

class NewtaskPage(Handler):
	def get(self):
		if not self.user_get_current():
			self.redirect('/login')
		self.render("newtask.html", username=self.user_get_current())

	def post(self):
		if not self.user_get_current():
			self.redirect('/login')
		task_name = self.request.get("task_name")
		task_body = self.request.get("task_body")
		finish_time = self.request.get("finish_date")

		# converting date string into datetime object
		ft = datetime.fromtimestamp(mktime(strptime(finish_time, "%Y-%m-%d")))
		
		task = Task(name=task_name, body=task_body, finish_time=ft, user=self.user_get_current())
		task.put()

		self.redirect('/')

app = webapp2.WSGIApplication([
	('/', MainPage),
	('/login', LoginPage),
	('/register', RegisterPage),
	('/logout', LogoutPage),
	('/welcome', WelcomePage),
	('/newtask', NewtaskPage),
	('/user/[a-zA-Z][a-zA-Z0-9_-]{2,19}$', UserPage),
	], debug=True)