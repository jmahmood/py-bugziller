#!/usr/bin/env python
# -*- coding: utf8 -*-

import xmlrpclib
import datetime
from cookie_transport import CookieTransport
from ConfigParser import ConfigParser

"""
A connection singleton-like object that will
be passed among various commands.

This could be useful if you are syncing between
one system and a bugzilla install.

ie: Your in-house ticket system needs to connect
to a bugzilla instance once a day to sync changes.

How to use:
===========
try:
    conn = BugzillaConnection()
except:
    print "could not connect blah blah, here is why, blah blah"

"""
class BugzillaConnection(object):
    def __init__(self):
        self.read_config()
        self.server = xmlrpclib.Server(self.url, 
            transport=CookieTransport());
        success, cause = self.server_login()
        if not success:
            print "Error while logging in."
            print cause

    def read_config(self):
        config = ConfigParser()
        config.read('bugzilla.config')
        self.login = config.get('bugzilla', 'login')
        self.password = config.get('bugzilla', 'password')
        self.url = config.get('bugzilla', 'url')

    def server_login(self):
        try:
            self.server.User.login({
                'login': self.login,
                'password': self.password,
                'remember':1
            })
            return True, None
        except xmlrpclib.Fault, err:
            return False, err
