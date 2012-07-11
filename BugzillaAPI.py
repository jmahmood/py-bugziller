#!/usr/bin/env python
# -*- coding: utf8 -*-

import xmlrpclib
import datetime


class genericBugzillaFunction(object):
    def __init__(self, connection):
        self.connection = connection

    def validation_functions_init(self):
        self.validation_functions = {
            'alias':partial(isinstance, type=basestring),
            'assigned_to':partial(isinstance, type=basestring),
            'blocks':partial(isinstance, type=dict), #add, remove, set
            'depends_on':partial(isinstance, type=dict), #add, remove, set
            'cc':partial(isinstance, type=dict), #add, remove
            'is_cc_accessible':partial(isinstance, type=bool),
            'comment':partial(isinstance, type=dict), #body, is_private
            'comment_is_private':partial(isinstance, type=bool),
            'component':partial(isinstance, type=basestring),
            'deadline':partial(isinstance, type=datetime.datetime),
            'dupe_of':partial(isinstance, type=int),
            'estimated_time':partial(isinstance, type=float),
            'groups':partial(isinstance, type=dict), #add, remove
            'keywords':partial(isinstance, type=dict), #add, remove, set
            'op_sys':partial(isinstance, type=basestring),
            'platform':partial(isinstance, type=basestring),
            'priority':partial(isinstance, type=basestring),
            'product':partial(isinstance, type=basestring),
            'qa_contact':partial(isinstance, type=basestring),
            'is_creator_accessible':partial(isinstance, type=bool),
            'remaining_time':partial(isinstance, type=float), #hours
            'reset_assigned_to':partial(isinstance, type=bool),
            'reset_qa_contact':partial(isinstance, type=bool),
            'resolution':partial(isinstance, type=basestring),
            'see_also':partial(isinstance, type=dict), #add, remove
            'severity':partial(isinstance, type=basestring),
            'status':partial(isinstance, type=basestring),
            'summary':partial(isinstance, type=basestring),
            'target_milestone':partial(isinstance, type=basestring),
            'url':partial(isinstance, type=basestring),
            'version':partial(isinstance, type=basestring),
            'whiteboard':partial(isinstance, type=basestring),
            'work_time':partial(isinstance, type=float),
        }

    def valid_args(self, kwargs):
        if len(self.missing_args(kwargs)) > 0:
            return False
        return True

    def required_args(self):
        return []

    def method(self, method, args):
        f = getattr(self.connection.server, method)
        return f(args)

    def missing_args(self, kwargs):
        required_args = self.required_args()
        if len(required_args) == 0:
            return []
        return [arg for arg in required_args if arg not in kwargs]

    def execute(self, **kwargs):
        raise NotImplementedError

    def valueErrorText(self):
        return "To call this function, you must pass the following: %s. \n\n\nYou only passed %s"

    def __call__(self, **kwargs):
        if not self.valid_args(kwargs):
            raise ValueError( self.valueErrorText() % (
                    self.required_args(), self.missing_args(kwargs)))
        return self.execute(**kwargs)


class userGet(genericBugzillaFunction):
    def required_args(self):
        return ['email', 'id', 'match']

    def missing_args(self, kwargs):
        required_args = set(self.required_args)
        passed_args = set(kwargs)

        # There is an OR requirement here.  If you pass
        # one or more of the required arguments, you are fine.
        if len(required_args & passed_args) > 0:
            return []
        return required_args

    def execute(self, **kwargs):
        return self.method("User.get", kwargs)


class userExists(userGet):
    def execute(self, **kwargs):
        return len(self.method("User.get", kwargs)) > 0


class userCreate(genericBugzillaFunction):
    def required_args(self):
        return ['email']

    def execute(self, **kwargs):
        email = kwargs['email']
        try:
            ret = self.method("User.offer_account_by_email", kwargs)
            return True, ret
        except xmlrpclib.Fault, err:
            return False, err


class userOfferAccountByEmail(genericBugzillaFunction):
    def required_args(self):
        return ['email']

    def execute(self, **kwargs):
        email = kwargs['email']
        try:
            ret = self.method("User.offer_account_by_email", kwargs)
            return True, ret
        except xmlrpclib.Fault, err:
            return False, err


class bugCreate(genericBugzillaFunction):
    def required_args(self):
        return ["product", "component", "summary", "version", 
        "description", "op_sys", "platform", "severity", "priority"]

    def execute(self, **kwargs):

        try:
            ret = self.method("Bug.create", kwargs)
            return True, ret
        except xmlrpclib.Fault, err:
            return False, err


class bugAddComment(genericBugzillaFunction):
    def required_args(self):
        return ['id', 'comment']

    def execute(self, **kwargs):
        try:
            self.method("Bug.add_comment", kwargs)
            return True, None
        except xmlrpclib.Fault, err:
            return False, err


class bugGet(genericBugzillaFunction):
    def required_args(self):
        return ['id', 'comment']

    def execute(self, **kwargs):
        try:
            self.method("Bug.get", kwargs)
            return True, None
        except xmlrpclib.Fault, err:
            return False, err


class bugUpdate(genericBugzillaFunction):
    def required_args(self):
        return ['ids']

    def additional_validation(self, kwargs):
        self.validation_functions_init()
        for k,v in kwargs:
            if k not in validation_functions:
                raise ValueError("%s is not a valid argument for the update function" % k)
            if not validation_functions[k](v):
                raise ValueError("Invalid value for %s" % k)

    def execute(self, **kwargs):
        self.additional_validation(kwargs)
        try:
            ret = self.method("Bug.update", kwargs)
            return True, ret
        except xmlrpclib.Fault, err:
            return False, err
