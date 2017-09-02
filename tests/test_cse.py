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

import onem2mlib.session as SE
from onem2mlib.resources import *

from conf import *


class TestCSE(unittest.TestCase):
	session = None
	ae = None
	cse = None


	@classmethod
	def setUpClass(self):
		TestCSE.session = SE.Session(host, originator)


	@classmethod
	def tearDownClass(self):
		if TestCSE.ae:
			TestCSE.ae.deleteFromCSE()
			TestCSE.ae = None


	def test_init(self):
		self.assertIsNotNone(TestCSE.session)
		self.assertFalse(TestCSE.session.connected)
		self.assertEqual(TestCSE.session.address, host)
		self.assertEqual(TestCSE.session.originator, originator)


	def test_cseGet(self):
		TestCSE.cse = CSEBase(TestCSE.session, CSE_ID)
		self.assertTrue(TestCSE.session.connected)
		self.assertIsNotNone(TestCSE.cse)
		self.assertEqual(TestCSE.cse.type, CON.Type_CSEBase)
		if TestCSE.cse.findAE(AE_NAME):
			self.fail('*** AE with name "' + AE_NAME + '" already present in CSE. Please remove it first.')


	def test_isConnectedAfterwards(self):
		self.assertTrue(TestCSE.session.connected)


	def test_createAEInCSE(self):
		TestCSE.ae = AE(TestCSE.cse, resourceName=AE_NAME, labels=AE_LABELS)
		self.assertTrue(TestCSE.ae.createInCSE())
		self.assertEqual(TestCSE.ae.resourceName, AE_NAME)


	def test_findAEInCSE(self):
		aef = TestCSE.cse.findAE(AE_NAME)
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


	def test_finit(self):
		self.assertIsNotNone(TestCSE.ae)
		self.assertTrue(TestCSE.ae.deleteFromCSE())
		TestCSE.ae = None


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestCSE('test_init'))
	suite.addTest(TestCSE('test_cseGet'))
	suite.addTest(TestCSE('test_isConnectedAfterwards'))
	suite.addTest(TestCSE('test_createAEInCSE'))
	suite.addTest(TestCSE('test_findAEInCSE'))
	suite.addTest(TestCSE('test_aesInCSE'))
	suite.addTest(TestCSE('test_finit'))

	unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
