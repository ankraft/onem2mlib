#!/usr/local/bin/python3

#
#	test_ae.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	Unit test for the <AE> reource implementation.
#


import unittest
import os, sys
sys.path.append('..')

import onem2mlib.session as SE
from onem2mlib.resources import *

from conf import *


class TestAE(unittest.TestCase):
	session = None
	cse = None
	ae = None


	@classmethod
	def setUpClass(self):
		TestAE.session = SE.Session(host, username, password)
		TestAE.cse = CSEBase(TestAE.session, CSE_NAME)
		if TestAE.cse.findAE(AE_NAME):
			print('*** AE with name "' + AE_NAME + '" already present in CSE. Please remove it first.')
			exit()


	@classmethod
	def tearDownClass(self):
		if TestAE.ae:
			TestAE.ae.deleteFromCSE()
			TestAE.ae = None


	def test_init(self): 
		self.assertTrue(TestAE.session.connected)
		self.assertIsNotNone(TestAE.session)
		self.assertIsNotNone(TestAE.cse)
		self.assertIsNotNone(TestAE.cse.resourceID)


	def test_createAE(self):
		TestAE.ae = AE(TestAE.cse, resourceName=AE_NAME, labels=AE_LABELS)
		self.assertEqual(TestAE.ae.type, CON.Type_AE)
		self.assertTrue(TestAE.ae.createInCSE())
		self.assertEqual(TestAE.ae.resourceName, AE_NAME)


	def test_retrieveAE(self):
		id = TestAE.ae.resourceID
		TestAE.ae = None
		TestAE.ae = AE(TestAE.cse, resourceID=id)
		self.assertEqual(TestAE.ae.type, CON.Type_AE)
		self.assertTrue(TestAE.ae.retrieveFromCSE())
		self.assertEqual(TestAE.ae.resourceName, AE_NAME)


	def test_updateAE(self):
		# Labels
		oldLabels = TestAE.ae.labels
		TestAE.ae.labels = ['new/label']
		self.assertTrue(TestAE.ae.updateInCSE())
		self.assertEqual(TestAE.ae.resourceName, AE_NAME)
		self.assertNotEqual(TestAE.ae.labels, oldLabels)


	def test_containersInAE(self):
		# Test empty list
		cnts = TestAE.ae.containers()
		self.assertIsNotNone(cnts)
		self.assertTrue(len(cnts) == 0) 

		# Create some containers
		cnt1 = Container(TestAE.ae, CNT_NAME+'_1')
		self.assertIsNotNone(cnt1)
		self.assertTrue(cnt1.createInCSE())
		cnt2 = Container(TestAE.ae, CNT_NAME+'_2')
		self.assertIsNotNone(cnt2)
		self.assertTrue(cnt2.createInCSE())

		# Test list with 2 containers
		cnts = TestAE.ae.containers()
		self.assertIsNotNone(cnts)
		self.assertTrue(len(cnts) == 2) 


	def test_flexContainersInAE(self):
		print('\nT O D O')
		return
		# Test empty list
		fcnts = TestAE.ae.flexContainers()
		self.assertIsNotNone(fcnts)
		self.assertTrue(len(fcnts) == 0) 

		# Create some flexContainers
		fcnt1 = FlexContainer(TestAE.ae, FCNT_NAME+'_1')
		self.assertIsNotNone(fcnt1)
		self.assertTrue(fcnt1.createInCSE())
		fcnt2 = FlexContainer(TestAE.ae, FCNT_NAME+'_2')
		self.assertIsNotNone(fcnt2)
		self.assertTrue(fcnt2.createInCSE())

		# Test list with 2 containers
		fcnts = TestAE.ae.flexContainers()
		self.assertIsNotNone(fcnts)
		self.assertTrue(len(fcnts) == 2) 


	def test_groupsInAE(self):
		grp = Group(TestAE.ae, resourceName=GRP_NAME, resources=TestAE.ae.containers())
		self.assertTrue(grp.createInCSE())
		grps = TestAE.ae.groups()
		self.assertIsNotNone(grps)
		self.assertEqual(len(grps), 1)
		self.assertEqual(grps[0].resourceID, grp.resourceID)


	def test_finit(self):
		self.assertIsNotNone(TestAE.ae)
		self.assertTrue(TestAE.ae.deleteFromCSE())
		self.assertIsNone(TestAE.cse.findAE(AE_NAME))
		TestAE.ae = None


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestAE('test_init'))
	suite.addTest(TestAE('test_createAE'))
	suite.addTest(TestAE('test_retrieveAE'))
	suite.addTest(TestAE('test_updateAE'))
	suite.addTest(TestAE('test_containersInAE'))
	suite.addTest(TestAE('test_flexContainersInAE'))
	suite.addTest(TestAE('test_groupsInAE'))
	suite.addTest(TestAE('test_finit'))
	unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
