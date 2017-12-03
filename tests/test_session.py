#!/usr/local/bin/python3

#
#	test_session.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	Unit test for session.
#


import unittest
import os, sys
sys.path.append('..')

from onem2mlib import *

from conf import *


class TestSession(unittest.TestCase):
	session = None


	def test_init(self): 
		TestSession.session = Session(host, originator, encoding)
		self.assertIsNotNone(TestSession.session)
		self.assertEqual(TestSession.session.address, host)
		self.assertEqual(TestSession.session.originator, originator)


	def test_connect(self):
		cse = CSEBase(TestSession.session, CSE_ID)
		self.assertIsNotNone(cse)


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestSession('test_init'))
	suite.addTest(TestSession('test_connect'))
	unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
