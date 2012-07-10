#!/usr/bin/env python
# -*- coding: utf8 -*-

from BugzillaConnection import BugzillaConnection
from BugzillaAPI import *

conn = BugzillaConnection()
create_bug = bugCreate(conn)

vals = {
	'product': "TestProduct",
	'component': "TestComponent",
	'summary': "UNGH, AMAZING SUMMARY OF BUG",
	'version': "unspecified",
	'description': "Very long and boring description that everyone will ignore.",
	'op_sys': "All",
	'platform': "All",
	'severity': "enhancement",
	'priority': "Normal",
}

print repr(create_bug(**vals))
