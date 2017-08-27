#!/usr/local/bin/python3

#
#	test_acp.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	Unit test for the <ACP> reource implementation.
#

import unittest
import os, sys
sys.path.append('..')

import onem2mlib.session as SE
from onem2mlib.resources import *

from conf import *


class TestACP(unittest.TestCase):
	session = None
	cse = None
	ae = None
	acp = None
	privileges = None


	@classmethod
	def setUpClass(self):
		TestACP.session = SE.Session(host, username, password)
		TestACP.cse = CSEBase(TestACP.session, CSE_NAME)
		if TestACP.cse.findAE(AE_NAME):
			print('*** AE with name "' + AE_NAME + '" already present in CSE. Please remove it first.')
			exit()
		if TestACP.cse.findAcp(ACP_NAME):
			print('*** ACP with name "' + ACP_NAME + '" already present in CSE. Please remove it first.')
			exit()
		TestACP.ae = AE(TestACP.cse, resourceName=AE_NAME)
		TestACP.ae.createInCSE()


	@classmethod
	def tearDownClass(self):
		if TestACP.ae:
			TestACP.ae.deleteFromCSE()
			TestACP.ae = None
		if TestACP.acp:
			TestACP.acp.deleteFromCSE()
			TestACP.acp = None


	def test_init(self): 
		self.assertTrue(TestACP.session.connected)
		self.assertIsNotNone(TestACP.session)
		self.assertIsNotNone(TestACP.cse)
		self.assertIsNotNone(TestACP.cse.resourceID)
		TestACP.privileges = [ 
			AccessControlRule(['admin:admin', '/'+CSE_NAME], CON.Acp_ALL),
			AccessControlRule(['limited:limited',], CON.Acp_CREATE+CON.Acp_RETRIEVE)
		]
		TestACP.selfPrivileges = [ 
			AccessControlRule([username+':'+password], CON.Acp_ALL)
		]



	def test_createAcp(self):
		TestACP.acp = AccessControlPolicy(TestACP.cse, resourceName=ACP_NAME, privileges=TestACP.privileges, selfPrivileges=TestACP.selfPrivileges)
		self.assertIsNotNone(TestACP.acp)
		self.assertEqual(TestACP.acp.type, CON.Type_ACP)
		self.assertTrue(TestACP.acp.createInCSE())
		self.assertEqual(TestACP.acp.resourceName, ACP_NAME)


	def  test_createInstantly(self):
		pass

# delete an acp
# create an acp with other privileges, but pvs correct. try to access it
# get all acp from cse
# find specific acp
# parent not cse

	def test_finit(self):
		self.assertIsNotNone(TestACP.acp)
		self.assertTrue(TestACP.acp.deleteFromCSE())
		self.assertIsNone(TestACP.cse.findAcp(ACP_NAME))
		self.assertIsNotNone(TestACP.ae)
		self.assertTrue(TestACP.ae.deleteFromCSE())
		self.assertIsNone(TestACP.cse.findAE(AE_NAME))
		TestACP.ae = None
		TestACP.acp = None


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestACP('test_init'))
	suite.addTest(TestACP('test_createAcp'))
	suite.addTest(TestACP('test_createInstantly')) #TODO
	suite.addTest(TestACP('test_finit'))
	unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)

