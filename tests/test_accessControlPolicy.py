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
import os, sys, time
sys.path.append('..')

import onem2mlib.session as SE
from onem2mlib.resources import *

from conf import *


class TestACP(unittest.TestCase):
	session = None
	cse = None
	acp = None
	privileges = None
	selfPrivileges = None


	@classmethod
	def setUpClass(self):
		TestACP.session = SE.Session(host, originator)
		TestACP.cse = CSEBase(TestACP.session, CSE_ID)
		if not TestACP.session.connected:
			print('*** Not connected to CSE')
			exit()
		if TestACP.cse.findAE(AE_NAME):
			print('*** AE with name "' + AE_NAME + '" already present in CSE. Please remove it first.')
			exit()
		if TestACP.cse.findAccessControlPolicy(ACP_NAME):
			print('*** ACP with name "' + ACP_NAME + '" already present in CSE. Please remove it first.')
			exit()


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
			AccessControlRule([originator], CON.Acp_ALL),
			AccessControlRule([ACP_LIMITED, '/'+CSE_ID], CON.Acp_RETRIEVE+CON.Acp_DISCOVER)
		]
		TestACP.selfPrivileges = [ 
			AccessControlRule([originator], CON.Acp_ALL)
		]


	def test_createAcp(self):
		TestACP.acp = AccessControlPolicy(TestACP.cse, resourceName=ACP_NAME, privileges=TestACP.privileges, selfPrivileges=TestACP.selfPrivileges)
		self.assertIsNotNone(TestACP.acp)
		self.assertEqual(TestACP.acp.type, CON.Type_ACP)
		self.assertTrue(TestACP.acp.createInCSE())
		self.assertEqual(TestACP.acp.resourceName, ACP_NAME)


	def test_findACP(self):
		self.assertIsNotNone(TestACP.acp)
		acp = TestACP.cse.findAccessControlPolicy(ACP_NAME)
		self.assertIsNotNone(acp)
		self.assertEqual(acp.resourceName, ACP_NAME)
		self.assertEqual(len(acp.privileges), 2)
		originatorFound = False
		operationFound = False
		for p in acp.privileges:
			if originator in p.accessControlOriginators:
				self.assertEqual(p.accessControlOperations, CON.Acp_ALL)
				originatorFound = True
			if ACP_LIMITED in p.accessControlOriginators:
				self.assertEqual(p.accessControlOperations, CON.Acp_RETRIEVE+CON.Acp_DISCOVER)
				operationFound = True
		self.assertTrue(originatorFound)
		self.assertTrue(operationFound)
		self.assertEqual(len(acp.selfPrivileges), 1)
		self.assertEqual(len(acp.selfPrivileges[0].accessControlOriginators), 1)
		self.assertEqual(acp.selfPrivileges[0].accessControlOriginators[0], originator)
		self.assertEqual(acp.selfPrivileges[0].accessControlOperations, CON.Acp_ALL)


	def test_deleteACP(self):
		self.assertIsNotNone(TestACP.acp)
		self.assertTrue(TestACP.acp.deleteFromCSE())
		self.assertIsNone(TestACP.cse.findAccessControlPolicy(ACP_NAME))


	def  test_createInstantly(self):
		# ACP was deleted during the last test
		TestACP.acp = AccessControlPolicy(TestACP.cse, resourceName=ACP_NAME, privileges=TestACP.privileges, selfPrivileges=TestACP.selfPrivileges, instantly=True)
		self.assertIsNotNone(TestACP.acp)
		self.assertEqual(TestACP.acp.type, CON.Type_ACP)
		self.assertEqual(TestACP.acp.resourceName, ACP_NAME)


# create an acp with other privileges, but pvs correct. try to access it

	def test_createAELimited1(self):
		# create a limited session, try to ceate an AE with that. This should fail
		sessionLimited = SE.Session(host, ACP_LIMITED)
		self.assertIsNotNone(sessionLimited)
		cseLimited = CSEBase(sessionLimited, CSE_ID)
		self.assertIsNotNone(cseLimited)
		self.assertTrue(sessionLimited.connected)
		aeLimited = AE(cseLimited, resourceName=AE_NAME+'L')
		self.assertIsNotNone(aeLimited)
		#aeLimited.accessControlPolicyIDs = [ TestACP.acp ]
		self.assertFalse(aeLimited.createInCSE())


	def test_createAELimited2(self):
		# create an AE with the ACP assigned.
		TestACP.ae = AE(TestACP.cse, resourceName=AE_NAME)
		self.assertIsNotNone(TestACP.ae)
		TestACP.ae.setAccessControlPolicies(TestACP.acp)
		self.assertTrue(TestACP.ae.createInCSE())

		# Now try to retrieve it with a limited acp
		sessionLimited = SE.Session(host, ACP_LIMITED)
		self.assertIsNotNone(sessionLimited)
		cseLimited = CSEBase(sessionLimited, CSE_ID)
		self.assertIsNotNone(cseLimited)
		self.assertTrue(sessionLimited.connected)
		aeLimited = AE(cseLimited, resourceName=AE_NAME)
		self.assertTrue(aeLimited.retrieveFromCSE())

		# Now try to delete this limited AE
		self.assertFalse(aeLimited.deleteFromCSE())


	def test_findAllACP(self):
		self.assertIsNotNone(TestACP.cse)
		acps = TestACP.cse.accessControlPolicies() 
		self.assertIsNotNone(acps)
		self.assertTrue( len(acps) > 0)


	def test_updateACP(self):
		print('WARNING: Skip updateTest. om2m cannot delete updated acp yet ... ', end='', flush=True)
		return

		self.assertIsNotNone(TestACP.acp)
		rule = AccessControlRule(['another:another'], CON.Acp_RETRIEVE)
		TestACP.acp.privileges.append(rule)
		TestACP.acp.updateInCSE()
		#print(TestACP.acp)


	def test_finit(self):
		# First delete the ae, not the ACP!!
		self.assertTrue(TestACP.ae.deleteFromCSE())
		self.assertIsNone(TestACP.cse.findAE(AE_NAME))
		self.assertIsNotNone(TestACP.acp)
		self.assertTrue(TestACP.acp.deleteFromCSE())
		self.assertIsNone(TestACP.cse.findAccessControlPolicy(ACP_NAME))
		self.assertIsNotNone(TestACP.ae)
		TestACP.ae = None
		TestACP.acp = None


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestACP('test_init'))
	suite.addTest(TestACP('test_createAcp'))
	suite.addTest(TestACP('test_findACP'))
	suite.addTest(TestACP('test_deleteACP'))
	suite.addTest(TestACP('test_createInstantly'))	
	suite.addTest(TestACP('test_createAELimited1'))
	suite.addTest(TestACP('test_createAELimited2'))
	suite.addTest(TestACP('test_findAllACP'))
	suite.addTest(TestACP('test_updateACP'))
	suite.addTest(TestACP('test_finit'))
	unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)

