#!/usr/local/bin/python3

#
#	test_contentInstance.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	Unit test for the <contentInstance> reource implementation.
#

import unittest
import os, sys, time
sys.path.append('..')

import onem2mlib.session as SE
from onem2mlib.resources import *

from conf import *


class TestContentInstance(unittest.TestCase):
	session = None
	cse = None
	ae = None
	cnt = None
	cin = None


	@classmethod
	def setUpClass(self):
		TestContentInstance.session = SE.Session(host, username, password)
		TestContentInstance.cse = CSEBase(TestContentInstance.session, CSE_NAME)
		if TestContentInstance.cse.findAE(AE_NAME):
			print('*** AE with name "' + AE_NAME + '" already present in CSE. Please remove it first.')
			exit()
		TestContentInstance.ae = AE(TestContentInstance.cse, resourceName=AE_NAME)
		TestContentInstance.ae.createInCSE()
		TestContentInstance.cnt = Container(TestContentInstance.ae, resourceName=CNT_NAME)
		TestContentInstance.cnt.createInCSE()


	@classmethod
	def tearDownClass(self):
		if TestContentInstance.ae:
			TestContentInstance.ae.deleteFromCSE()
			TestContentInstance.ae = None


	def test_init(self): 
		self.assertTrue(TestContentInstance.session.connected)
		self.assertIsNotNone(TestContentInstance.session)
		self.assertIsNotNone(TestContentInstance.cse)
		self.assertIsNotNone(TestContentInstance.cse.resourceID)
		self.assertIsNotNone(TestContentInstance.ae)
		self.assertIsNotNone(TestContentInstance.ae.resourceID)
		self.assertIsNotNone(TestContentInstance.cnt)
		self.assertIsNotNone(TestContentInstance.cnt.resourceID)


	def test_createContentInstance(self):
		TestContentInstance.cin = ContentInstance(TestContentInstance.cnt, resourceName=CIN_NAME, content=CIN_CONTENT, labels=CIN_LABELS)
		self.assertEqual(TestContentInstance.cin.type, CON.Type_ContentInstance)
		self.assertTrue(TestContentInstance.cin.createInCSE())
		self.assertEqual(TestContentInstance.cin.resourceName, CIN_NAME)
		self.assertEqual(len(TestContentInstance.cnt.contentInstances()), 1)


	def test_retrieveContentInstance(self):
		cin = ContentInstance(TestContentInstance.cnt, resourceID=TestContentInstance.cin. resourceID)
		self.assertTrue(cin.retrieveFromCSE())
		self.assertEqual(cin.content, CIN_CONTENT)


	def test_deleteContentInstance(self):
		self.assertTrue(TestContentInstance.cin.deleteFromCSE())
		self.assertEqual(TestContentInstance.cin.resourceName, CIN_NAME)
		self.assertEqual(len(TestContentInstance.cnt.contentInstances()), 0)


	def test_getContentInstance(self):
		self.assertIsNotNone(TestContentInstance.cse)
		self.assertIsNotNone(TestContentInstance.ae)

		# create a <contentInstane> by using the get() method
		cin = ContentInstance(TestContentInstance.cnt, content=CIN_CONTENT)
		self.assertIsNotNone(cin)
		self.assertTrue(cin.get())

		# Check whether it was really created in the CSE
		cin2 = TestContentInstance.cnt.findContentInstance(cin.resourceName)
		self.assertIsNotNone(cin2)
		self.assertEqual(cin.resourceID, cin2.resourceID)


	def  test_createInstantly(self):
		self.assertIsNotNone(TestContentInstance.cse)
		self.assertIsNotNone(TestContentInstance.ae)

		# create an <contentInstane> while init
		cin = ContentInstance(TestContentInstance.cnt, content=CIN_CONTENT, instantly=True)
		self.assertIsNotNone(cin)

		# Check whether it was really created in the CSE
		cin2 = TestContentInstance.cnt.findContentInstance(cin.resourceName)
		self.assertIsNotNone(cin2)
		self.assertEqual(cin.resourceID, cin2.resourceID)


	def test_finit(self):
		self.assertTrue(TestContentInstance.ae.deleteFromCSE())
		self.assertIsNone(TestContentInstance.cse.findAE(AE_NAME))
		TestContentInstance.ae = None


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestContentInstance('test_init'))
	suite.addTest(TestContentInstance('test_createContentInstance'))
	suite.addTest(TestContentInstance('test_retrieveContentInstance'))
	suite.addTest(TestContentInstance('test_deleteContentInstance'))
	suite.addTest(TestContentInstance('test_getContentInstance'))
	suite.addTest(TestContentInstance('test_createInstantly'))
	suite.addTest(TestContentInstance('test_finit'))
	unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
