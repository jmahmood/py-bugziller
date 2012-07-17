#!/usr/bin/env python
# -*- coding: utf8 -*-

import xmlrpclib
import datetime

# isinstance doesn't let us use keyword arguments; this makes
# it harder to pass it as a partial function, etc...
def kw_instance(obj, type, keys=None):
    if not keys:
        return isinstance(obj, type)
    else:
        # obj is a dict.
        # all keys for obj must be in the list "keys".
        return isinstance(obj, type) and all([k in keys for k in list(obj)])



class genericBugzillaFunction(object):
    REMOTE_METHOD_NAME = "unknown"

    def __init__(self, connection):
        self.connection = connection

    def validation_functions_init(self):
        self.validation_functions = {
            'alias':partial(kw_instance, type=basestring),
            'assigned_to':partial(kw_instance, type=basestring),
            'blocks':partial(kw_instance, type=dict, keys=["add", "remove", "set"]), #add, remove, set
            'depends_on':partial(kw_instance, type=dict, keys=["add", "remove", "set"]), #add, remove, set
            'cc':partial(kw_instance, type=dict, keys=["add", "remove"]), #add, remove
            'ids':partial(kw_instance, type=list),
            'is_cc_accessible':partial(kw_instance, type=bool),
            'comment':partial(kw_instance, type=dict, keys=["body", "is_private"]), #body, is_private
            'comment_is_private':partial(kw_instance, type=bool),
            'component':partial(kw_instance, type=basestring),
            'deadline':partial(kw_instance, type=datetime.datetime),
            'dupe_of':partial(kw_instance, type=int),
            'estimated_time':partial(kw_instance, type=float),
            'groups':partial(kw_instance, type=dict, keys=["add", "remove"]), #add, remove
            'keywords':partial(kw_instance, type=dict, keys=["add", "remove", "set"]), #add, remove, set
            'op_sys':partial(kw_instance, type=basestring),
            'platform':partial(kw_instance, type=basestring),
            'priority':partial(kw_instance, type=basestring),
            'product':partial(kw_instance, type=basestring),
            'qa_contact':partial(kw_instance, type=basestring),
            'is_creator_accessible':partial(kw_instance, type=bool),
            'remaining_time':partial(kw_instance, type=float), #hours
            'reset_assigned_to':partial(kw_instance, type=bool),
            'reset_qa_contact':partial(kw_instance, type=bool),
            'resolution':partial(kw_instance, type=basestring),
            'see_also':partial(kw_instance, type=dict, keys=["add", "remove"]), #add, remove
            'severity':partial(kw_instance, type=basestring),
            'status':partial(kw_instance, type=basestring),
            'summary':partial(kw_instance, type=basestring),
            'target_milestone':partial(kw_instance, type=basestring),
            'url':partial(kw_instance, type=basestring),
            'version':partial(kw_instance, type=basestring),
            'whiteboard':partial(kw_instance, type=basestring),
            'work_time':partial(kw_instance, type=float),
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

    def valueErrorText(self):
        return "To call this function, you must pass the following: %s. \n\n\nYou only passed %s"

    def execute(self, **kwargs):
        try:
            ret = self.method(self.REMOTE_METHOD_NAME, kwargs)
            return True, ret
        except xmlrpclib.Fault, err:
            return False, err

    def __call__(self, **kwargs):
        if not self.valid_args(kwargs):
            raise ValueError( self.valueErrorText() % (
                    self.required_args(), self.missing_args(kwargs)))
        return self.execute(**kwargs)


class userGet(genericBugzillaFunction):
    REMOTE_METHOD_NAME = "User.get"

    def required_args(self):
        return ['names', 'ids', 'match']

    def missing_args(self, kwargs):
        required_args = set(self.required_args())
        passed_args = kwargs
        if any([pa in required_args for pa in passed_args]):
            return []
        return passed_args


class userExists(userGet):
    REMOTE_METHOD_NAME = "User.get"

    def execute(self, **kwargs):
        return len(self.method(userExists.REMOTE_METHOD_NAME, kwargs)) > 0


class userCreate(genericBugzillaFunction):
    REMOTE_METHOD_NAME = "User.create"

    def required_args(self):
        return ['email']

class userUpdate(userGet):
    REMOTE_METHOD_NAME = "User.create"

    def required_args(self):
        return ['ids', 'names']


class userOfferAccountByEmail(genericBugzillaFunction):
    REMOTE_METHOD_NAME = "User.offer_account_by_email"

    def required_args(self):
        return ['email']


class bugCreate(genericBugzillaFunction):
    REMOTE_METHOD_NAME = "Bug.create"

    def required_args(self):
        return ["product", "component", "summary", "version", 
        "description", "op_sys", "platform", "severity", "priority"]


class bugAddComment(genericBugzillaFunction):
    REMOTE_METHOD_NAME = "Bug.add_comment"

    def required_args(self):
        return ['id', 'comment']


class bugGet(genericBugzillaFunction):
    REMOTE_METHOD_NAME = "Bug.get"

    def required_args(self):
        return ['id', 'comment']


class bugUpdate(genericBugzillaFunction):
    REMOTE_METHOD_NAME = "Bug.update"

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
        return super(bugUpdate, self).execute(kwargs)