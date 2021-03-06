#!/usr/local/bin/python3

#
#	test_cse.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	Unit test for the <CSEBase> reource implementation.
#

import unittest
import os, sys
sys.path.append('..')

from onem2mlib import *
from conf import *


class TestCSE(unittest.TestCase,):
	session = None
	ae = None
	cse = None


	@classmethod
	def setUpClass(cls):
		TestCSE.session = Session(host, originator, encoding)


	@classmethod
	def tearDownClass(cls):
		if TestCSE.ae:
			TestCSE.ae.deleteFromCSE()
			TestCSE.ae = None


	def test_init(self):
		self.assertIsNotNone(TestCSE.session)
		self.assertEqual(TestCSE.session.address, host)
		self.assertEqual(TestCSE.session.originator, originator)
		self.assertEqual(TestCSE.session.encoding, encoding)


	def test_cseGet(self):
		TestCSE.cse = CSEBase(TestCSE.session, CSE_ID)
		self.assertIsNotNone(TestCSE.cse)
		self.assertEqual(TestCSE.cse.type, CON.Type_CSEBase)
		if TestCSE.cse.findAE(AE_NAME):
			self.fail('*** AE with name "' + AE_NAME + '" already present in CSE. Please remove it first.')


	def test_createAEInCSE(self):
		TestCSE.ae = AE(TestCSE.cse, resourceName=AE_NAME, labels=AE_LABELS, instantly=False)
		self.assertTrue(TestCSE.ae.createInCSE())
		self.assertEqual(TestCSE.ae.resourceName, AE_NAME)


	def test_findAEInCSE(self):
		aef = TestCSE.cse.findAE(AE_NAME)
		self.assertIsNotNone(aef)
		self.assertEqual(aef.resourceID, TestCSE.ae.resourceID)


	def test_aesInCSE(self):
		aes = TestCSE.cse.aes()
		self.assertTrue(len(aes) > 0)
		found = False 
		for ae in aes:
			if ae.resourceID == TestCSE.ae.resourceID:
				found = True
				break
		self.assertTrue(found)


	def test_containersInCSE(self):
		self.assertIsNotNone(TestCSE.cse)
		# add a container
		cnt = TestCSE.cse.addContainer(CNT_NAME)
		self.assertIsNotNone(cnt)
		# check the container
		cnts = TestCSE.cse.containers()
		self.assertTrue(len(cnts) == 1)
		found = False
		for c in cnts:
			if c.resourceID == cnt.resourceID:
				found = True
				break
		self.assertTrue(found)


	def test_addFindAE(self):
		self.assertIsNotNone(TestCSE.cse)
		# create an AE
		ae = TestCSE.cse.addAE(AE_NAME + '_1')
		self.assertIsNotNone(ae)
		# try to retrieve it
		a = TestCSE.cse.findAE(AE_NAME + '_1')
		self.assertIsNotNone(a)
		self.assertEqual(a.resourceID, ae.resourceID)


	def test_addFindGroup(self):
		self.assertIsNotNone(TestCSE.cse)
		# create a group
		grp = TestCSE.cse.addGroup(GRP_NAME, [TestCSE.ae])
		self.assertIsNotNone(grp)
		# try to retrieve it
		g = TestCSE.cse.findGroup(GRP_NAME)
		self.assertIsNotNone(g)
		self.assertEqual(g.resourceID, grp.resourceID)


	def test_finit(self):
		self.assertIsNotNone(TestCSE.ae)
		self.assertTrue(TestCSE.ae.deleteFromCSE())
		TestCSE.ae = None


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestCSE('test_init'))
	suite.addTest(TestCSE('test_cseGet'))
	suite.addTest(TestCSE('test_createAEInCSE'))
	suite.addTest(TestCSE('test_findAEInCSE'))
	suite.addTest(TestCSE('test_aesInCSE'))
	suite.addTest(TestCSE('test_containersInCSE'))
	suite.addTest(TestCSE('test_addFindAE'))
	suite.addTest(TestCSE('test_addFindGroup'))
	suite.addTest(TestCSE('test_finit'))

	unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
