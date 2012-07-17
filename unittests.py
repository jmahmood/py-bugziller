#!/usr/bin/env python
# -*- coding: utf8 -*-

from BugzillaAPI import *
from BugzillaConnection import BugzillaConnection
from random import randrange
import unittest

class TestUserFunctions(unittest.TestCase):
	def setUp(self):
		self.connection = BugzillaConnection()
		self.invalid_mail_address = "LOLmrj@duurrdurr@"
		self.mail_address = "testemail@ordisante.com"
		new_mail_address_number = randrange(1,40000)
		self.new_mail_address = "%d@example.com" % new_mail_address_number
		self.new_rename_mail_address = "%d@examp.com" % new_mail_address_number
		self.new_mail_address_2 = "%d@example.com" % randrange(1,40000)
		self.new_user_password = "password"

	def create_user(self, d):
		userCreateFn = userCreate(self.connection)
		return userCreateFn(**d)


	def test_createuser(self):
		print "create user"
		d = {
			"email":self.new_mail_address,
			"full_name":"Test User",
			"password":self.new_user_password
		}
		success, additional_info = self.create_user(d)
		self.assertTrue(success)
		self.assertTrue("id" in list(additional_info) )

	def test_recreate_existing_user(self):
		print "recreate user"
		d = {
			"email":self.mail_address,
			"full_name":"Test User",
			"password":self.new_user_password
		}
		success, additional_info = self.create_user(d)
		self.assertFalse(success)
		self.assertTrue(additional_info.faultCode == 500)

	def test_invalid_new_user_email(self):
		print "invalid new user email"
		d = {
			"email":self.invalid_mail_address,
			"full_name":"Test User",
			"password":self.new_user_password
		}
		success, additional_info = self.create_user(d)
		self.assertFalse(success)
		self.assertTrue(additional_info.faultCode == 501)

	def test_invalid_new_user_password(self):
		print "invalid new user password"
		d = {
			"email":self.new_mail_address_2,
			"full_name":"Test User",
			"password":"aa" # something shorter than 3 characters
		}
		success, additional_info = self.create_user(d)
		self.assertFalse(success)
		self.assertTrue(additional_info.faultCode == 502)


	def test_get_existing_user(self):
		print "get existing user"
		ret_vals = ['id', 'real_name', 'email', 'email', 'name', 'can_login', 'email_enabled', 'login_denied_text', 'groups']
		d = {
			"names": [self.mail_address]
		}
		userGetFn = userGet(self.connection)
		success, additional_info = userGetFn(**d)
		self.assertTrue(success)
		self.assertTrue(all([k in list(additional_info) for k in ret_vals]))


	def test_modify_existing_user(self):
		print "modify existing user"
		ret_vals = ['id', 'changes']

		d = {
			"email":self.new_mail_address_2,
			"full_name":"Test User",
			"password":self.new_user_password # something shorter than 3 characters
		}
		success, additional_info = self.create_user(d)

		d = {
			"names": [self.new_mail_address_2],
			"email": self.new_rename_mail_address,
			"email_enabled": False,
			"login_denied_text": "This is a test account"
		}

		temporary_connection = BugzillaConnection(self.new_mail_address, self.new_user_password)
		userUpdateFn = userUpdate(temporary_connection)
		success, additional_info = userUpdateFn(**d)
		self.assertTrue(success)
		self.assertTrue(all([k in list(additional_info) for k in ret_vals]))









if __name__ == '__main__':
    unittest.main()
