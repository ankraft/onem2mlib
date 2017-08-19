#!/usr/local/bin/python3

#
#	test_container.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	Unit test for the <container> reource implementation.
#

import unittest
import os, sys, time
sys.path.append('..')

import onem2mlib.session as SE
from onem2mlib.resources import *

from conf import *


class TestContainer(unittest.TestCase):
	session = None
	cse = None
	ae = None
	cnt = None
	cnt2 = None
	cin = None


	@classmethod
	def setUpClass(self):
		TestContainer.session = SE.Session(host, username, password)
		TestContainer.cse = CSEBase(TestContainer.session, CSE_NAME)
		if TestContainer.cse.findAE(AE_NAME):
			print('*** AE with name "' + AE_NAME + '" already present in CSE. Please remove it first.')
			exit()
		TestContainer.ae = AE(TestContainer.cse, resourceName=AE_NAME)
		TestContainer.ae.createInCSE()


	@classmethod
	def tearDownClass(self):
		if TestContainer.ae:
			TestContainer.ae.deleteFromCSE()
			TestContainer.ae = None


	def test_init(self): 
		self.assertTrue(TestContainer.session.connected)
		self.assertIsNotNone(TestContainer.session)
		self.assertIsNotNone(TestContainer.cse)
		self.assertIsNotNone(TestContainer.cse.resourceID)
		self.assertIsNotNone(TestContainer.ae)
		self.assertIsNotNone(TestContainer.ae.resourceID)


	def test_createContainer(self):
		TestContainer.cnt = Container(TestContainer.ae, resourceName=CNT_NAME, labels=CNT_LABELS)
		self.assertEqual(TestContainer.cnt.type, CON.Type_Container)
		self.assertTrue(TestContainer.cnt.createInCSE())
		self.assertEqual(TestContainer.cnt.resourceName, CNT_NAME)


	def test_retrieveContainer(self):
		id = TestContainer.cnt.resourceID
		TestContainer.cnt = None
		TestContainer.cnt = Container(TestContainer.ae, resourceID=id)
		self.assertTrue(TestContainer.cnt.retrieveFromCSE())
		self.assertEqual(TestContainer.cnt.resourceName, CNT_NAME)


	def test_findContentInstance(self):
		# Create contentInstance
		TestContainer.cin = ContentInstance(TestContainer.cnt, CIN_NAME, content=CIN_CONTENT)
		self.assertTrue(TestContainer.cin.createInCSE())

		# then find the CI
		cin = TestContainer.cnt.findContentInstance(CIN_NAME)
		self.assertIsNotNone(cin)
		self.assertEqual(cin.resourceName, TestContainer.cin.resourceName)
		self.assertEqual(cin.resourceID, TestContainer.cin.resourceID)
		self.assertEqual(cin.content, CIN_CONTENT)

		# remove cin again
		self.assertTrue(cin.deleteFromCSE())


	def test_updateContainer(self):
		# Labels
		oldLabels = TestContainer.cnt.labels
		TestContainer.cnt.labels = ['new/label']
		self.assertTrue(TestContainer.cnt.updateInCSE())
		self.assertEqual(TestContainer.cnt.resourceName, CNT_NAME)
		self.assertNotEqual(TestContainer.cnt.labels, oldLabels)

		# maxNrOfInstances
		TestContainer.cnt.maxNrOfInstances = 99
		self.assertTrue(TestContainer.cnt.updateInCSE())
		self.assertEqual(TestContainer.cnt.resourceName, CNT_NAME)
		self.assertEqual(TestContainer.cnt.maxNrOfInstances, 99)

		# maxByteSize
		TestContainer.cnt.maxByteSize = 999
		self.assertTrue(TestContainer.cnt.updateInCSE())
		self.assertEqual(TestContainer.cnt.resourceName, CNT_NAME)
		self.assertEqual(TestContainer.cnt.maxByteSize, 999)

		# maxInstanceAge
		TestContainer.cnt.maxInstanceAge = 9999
		self.assertTrue(TestContainer.cnt.updateInCSE())
		self.assertEqual(TestContainer.cnt.resourceName, CNT_NAME)
		self.assertEqual(TestContainer.cnt.maxInstanceAge, 9999)


	def test_containerInContainer(self):
		# Test empty sub-container in the beginning
		self.assertEqual(len(TestContainer.cnt.containers()), 0)

		# Add a sub-container
		scnt = Container(TestContainer.cnt, CNT_NAME + '1')
		self.assertTrue(scnt.createInCSE())
		self.assertEqual(scnt.resourceName, CNT_NAME + '1')
		self.assertEqual(len(TestContainer.cnt.containers()), 1)

		# Remove sub-container
		self.assertTrue(scnt.deleteFromCSE())
		self.assertEqual(len(TestContainer.cnt.containers()), 0)


	def test_getContainer(self):
		self.assertIsNotNone(TestContainer.cse)
		self.assertIsNotNone(TestContainer.ae)
		self.assertIsNone(TestContainer.ae.findContainer(CNT_NAME+'2'))

		# create a <container> by using the get() method
		TestContainer.cnt2 = Container(TestContainer.ae, resourceName=CNT_NAME+'2')
		self.assertIsNotNone(TestContainer.cnt2)
		self.assertTrue(TestContainer.cnt2.get())

		# Check whether it was really created in the CSE
		cnt2 = TestContainer.ae.findContainer(CNT_NAME+'2')
		self.assertIsNotNone(cnt2)
		self.assertEqual(TestContainer.cnt2.resourceID, cnt2.resourceID)

		# Delete the new <container> again
		self.assertTrue(TestContainer.cnt2.deleteFromCSE())
		self.assertIsNone(TestContainer.ae.findContainer(CNT_NAME+'2'))


	def  test_createInstantly(self):
		self.assertIsNotNone(TestContainer.cse)
		self.assertIsNotNone(TestContainer.ae)
		self.assertIsNone(TestContainer.ae.findContainer(CNT_NAME+'2'))

		# create an <container> while init
		TestContainer.cnt2 = Container(TestContainer.ae, resourceName=CNT_NAME+'2', instantly=True)
		self.assertIsNotNone(TestContainer.cnt2)

		# Check whether it was really created in the CSE
		cnt2 = TestContainer.ae.findContainer(CNT_NAME+'2')
		self.assertIsNotNone(cnt2)
		self.assertEqual(TestContainer.cnt2.resourceID, cnt2.resourceID)

		# Delete the new <container> again
		self.assertTrue(TestContainer.cnt2.deleteFromCSE())
		self.assertIsNone(TestContainer.ae.findContainer(CNT_NAME+'2'))


	def test_addContentInstance1(self):
		# Test empty contentInstances
		self.assertEqual(len(TestContainer.cnt.contentInstances()), 0)

		# Create contentInstance
		TestContainer.cin = ContentInstance(TestContainer.cnt, CIN_NAME, content=CIN_CONTENT)
		self.assertTrue(TestContainer.cin.createInCSE())

		# Test number of contentInstances (1)
		self.assertEqual(len(TestContainer.cnt.contentInstances()), 1)


	def test_testLatest1(self):
		la = TestContainer.cnt.latestContentInstance()
		self.assertIsNotNone(la)
		self.assertEqual(TestContainer.cin.resourceID, la.resourceID)


	def test_testOldest1(self):
		ol = TestContainer.cnt.oldestContentInstance()
		self.assertIsNotNone(ol)
		self.assertEqual(TestContainer.cin.resourceID, ol.resourceID)


	def test_testLatestOldest1(self):
		ol = TestContainer.cnt.oldestContentInstance()
		self.assertIsNotNone(ol)
		la = TestContainer.cnt.latestContentInstance()
		self.assertIsNotNone(la)
		self.assertEqual(la.resourceID, ol.resourceID)


	def test_addContentInstance2(self):
		# Wait a moment before add a new contentInstance
		time.sleep(1)

		# Test number of contentInstances (1)
		self.assertEqual(len(TestContainer.cnt.contentInstances()), 1)

		# Create another contentInstance
		cin = ContentInstance(TestContainer.cnt,content=CIN_CONTENT)
		self.assertTrue(cin.createInCSE())

		# Test number of contentInstances (2)
		self.assertEqual(len(TestContainer.cnt.contentInstances()), 2)


	def test_testLatest2(self):
		la = TestContainer.cnt.latestContentInstance()
		self.assertIsNotNone(la)
		self.assertNotEqual(TestContainer.cin.resourceID, la.resourceID)


	def test_testOldest2(self):
		ol = TestContainer.cnt.oldestContentInstance()
		self.assertIsNotNone(ol)
		self.assertEqual(TestContainer.cin.resourceID, ol.resourceID)


	def test_testLatestOldest2(self):
		ol = TestContainer.cnt.oldestContentInstance()
		self.assertIsNotNone(ol)
		la = TestContainer.cnt.latestContentInstance()
		self.assertIsNotNone(la)
		self.assertNotEqual(la.resourceID, ol.resourceID)


	def test_maxContentInstances(self):
		max = 5
		# create an empty sub-container with max 'max' ci
		scnt = Container(TestContainer.cnt, maxNrOfInstances=max)
		self.assertTrue(scnt.createInCSE())
		self.assertEquals(scnt.maxNrOfInstances, max)
		for i in range(0,5):
			ci = ContentInstance(scnt, content=str(i))
			self.assertTrue(ci.createInCSE())
			time.sleep(1)

		# check size, oldest, latest
		cis = scnt.contentInstances()
		self.assertEqual(len(cis), max)
		ol = scnt.oldestContentInstance()
		self.assertEqual(ol.content, str(0))
		self.assertEqual(ol.content, cis[0].content)
		la = scnt.latestContentInstance()
		self.assertEqual(la.content, str(max-1))
		self.assertEqual(la.content, cis[max-1].content)

		# add another ci
		ci = ContentInstance(scnt, content=str(max))
		self.assertTrue(ci.createInCSE())

		# check size, oldest, latest
		cis = scnt.contentInstances()
		self.assertEqual(len(cis), max)
		ol = scnt.oldestContentInstance()
		self.assertEqual(ol.content, str(1))
		self.assertEqual(ol.content, cis[0].content)
		la = scnt.latestContentInstance()
		self.assertEqual(la.content, str(max))
		self.assertEqual(la.content, cis[max-1].content)


	def test_finit(self):
		self.assertIsNotNone(TestContainer.cnt)
		self.assertIsNotNone(TestContainer.ae)
		self.assertTrue(TestContainer.cnt.deleteFromCSE())
		self.assertIsNone(TestContainer.ae.findContainer(CNT_NAME))
		TestContainer.cnt = None
		self.assertTrue(TestContainer.ae.deleteFromCSE())
		self.assertIsNone(TestContainer.cse.findAE(AE_NAME))
		TestContainer.ae = None



if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestContainer('test_init'))
	suite.addTest(TestContainer('test_createContainer'))
	suite.addTest(TestContainer('test_retrieveContainer'))
	suite.addTest(TestContainer('test_findContentInstance'))
	suite.addTest(TestContainer('test_updateContainer'))
	suite.addTest(TestContainer('test_containerInContainer'))
	suite.addTest(TestContainer('test_addContentInstance1'))
	suite.addTest(TestContainer('test_getContainer'))
	suite.addTest(TestContainer('test_createInstantly'))
	suite.addTest(TestContainer('test_testLatest1'))
	suite.addTest(TestContainer('test_testOldest1'))
	suite.addTest(TestContainer('test_testLatestOldest1'))
	suite.addTest(TestContainer('test_addContentInstance2'))
	suite.addTest(TestContainer('test_testLatest2'))
	suite.addTest(TestContainer('test_testOldest2'))
	suite.addTest(TestContainer('test_testLatestOldest2'))
	suite.addTest(TestContainer('test_maxContentInstances'))
	suite.addTest(TestContainer('test_finit'))
	unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
