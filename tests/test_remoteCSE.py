#!/usr/local/bin/python3

#
#	test_remoteCSE.py
#
#	(c) 2018 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	Unit test for the <remoteCSE> reource implementation.
#

import unittest
import os, sys, time
sys.path.append('..')



from onem2mlib import *
import onem2mlib.constants as CON
import onem2mlib.exceptions as EXC
import onem2mlib.notifications as NOT
from conf import *


class TestRemoteCSE(unittest.TestCase):
	session = None
	cse = None
	rsession = None
	rcse = None
	remoteCSE = None
	cseLocalRemoteCSE = None
	cseRemoteRemoteCSE = None
	ae = None


	@classmethod
	def setUpClass(self):
		TestRemoteCSE.session = Session(host, originator, encoding)
		TestRemoteCSE.cse = CSEBase(TestRemoteCSE.session, CSE_ID)
		try:
			TestRemoteCSE.rsession = Session(rhost, originator, encoding)
			TestRemoteCSE.rcse = CSEBase(TestRemoteCSE.rsession, CSE_RID)
		except Exception as e:
			print('*** Remote CSE (' + CSE_RNAME + ') must be running at ' + rhost + ' .')
			raise e


	@classmethod
	def tearDownClass(self):
		if TestRemoteCSE.ae is not None:
			TestRemoteCSE.ae.deleteFromCSE()


	def test_init(self):
		self.assertIsNotNone(TestRemoteCSE.session)
		self.assertIsNotNone(TestRemoteCSE.cse)
		self.assertIsNotNone(TestRemoteCSE.cse.resourceID)
		self.assertIsNotNone(TestRemoteCSE.rsession)
		self.assertIsNotNone(TestRemoteCSE.rcse)
		self.assertIsNotNone(TestRemoteCSE.rcse.resourceID)


	def test_getRemoteCSE(self):
		TestRemoteCSE.remoteCSE = TestRemoteCSE.cse.findRemoteCSE(CSE_RNAME)
		self.assertIsNotNone(TestRemoteCSE.remoteCSE)
		self.assertEqual(TestRemoteCSE.remoteCSE.resourceName, CSE_RNAME)


	def test_getAllRemoteCSEs(self):
		rcs = TestRemoteCSE.cse.remoteCSEs()
		self.assertIsNotNone(rcs)
		self.assertTrue(len(rcs) > 0)

		# find at least the designed test in-cse
		found = False
		for rc in rcs:
			if rc.resourceName == CSE_RNAME:
				found = True
		self.assertTrue(found)


	def test_getCseFromLocalCSE(self):
		self.assertIsNotNone(TestRemoteCSE.remoteCSE)

		# Get the remote CSE from the local CSE
		TestRemoteCSE.cseLocalRemoteCSE = TestRemoteCSE.remoteCSE.cseFromLocalCSE()
		self.assertIsNotNone(TestRemoteCSE.cseLocalRemoteCSE)
		self.assertEqual(TestRemoteCSE.cseLocalRemoteCSE.resourceName, CSE_RNAME)


	def test_getCseFromRemoteCSE(self):
		self.assertIsNotNone(TestRemoteCSE.remoteCSE)
		self.assertIsNotNone(TestRemoteCSE.cseLocalRemoteCSE)

		# Get the remote CSE from the remote CSE
		TestRemoteCSE.cseRemoteRemoteCSE = TestRemoteCSE.remoteCSE.cseFromRemoteCSE()
		self.assertIsNotNone(TestRemoteCSE.cseRemoteRemoteCSE)
		self.assertEqual(TestRemoteCSE.cseRemoteRemoteCSE.resourceName, CSE_RNAME)
		self.assertEqual(TestRemoteCSE.cseLocalRemoteCSE.resourceID, TestRemoteCSE.cseRemoteRemoteCSE.resourceID)
	

	def test_createRemoteAE(self):
		self.assertIsNotNone(TestRemoteCSE.cseLocalRemoteCSE)
		self.assertIsNotNone(TestRemoteCSE.cseRemoteRemoteCSE)

		# create a remote AE via the "local" remote CSE
		TestRemoteCSE.ae = TestRemoteCSE.cseLocalRemoteCSE.addAE(resourceName=AE_NAME)
		self.assertIsNotNone(TestRemoteCSE.ae)
		self.assertIsNotNone(TestRemoteCSE.ae.resourceID)
		self.assertEqual(TestRemoteCSE.ae.resourceName, AE_NAME)

		# get the same AE through the "remote" remote CSE
		rae = TestRemoteCSE.cseRemoteRemoteCSE.findAE(AE_NAME)
		self.assertIsNotNone(rae)
		self.assertIsNotNone(rae.resourceID)
		self.assertEqual(rae.resourceName, AE_NAME)
		self.assertEqual(TestRemoteCSE.ae.resourceID, rae.resourceID)


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestRemoteCSE('test_init'))
	suite.addTest(TestRemoteCSE('test_getRemoteCSE'))
	suite.addTest(TestRemoteCSE('test_getAllRemoteCSEs'))
	suite.addTest(TestRemoteCSE('test_getCseFromLocalCSE'))
	suite.addTest(TestRemoteCSE('test_getCseFromRemoteCSE'))
	suite.addTest(TestRemoteCSE('test_createRemoteAE'))

	unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
