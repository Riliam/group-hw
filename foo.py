import re




USERNAME = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]{2,19}$')
PASSWORD = re.compile(r'^.{6,20}$')
EMAIL = re.compile(r'^\S+@\S+\.\S+$')
# USERNAME = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")

def valid_username(name):
	return USERNAME.match(name)

def valid_password(passwd):
	return PASSWORD.match(passwd)

def valid_email(email):
	return not email or EMAIL.match(email)
