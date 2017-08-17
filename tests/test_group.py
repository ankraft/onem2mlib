#!/usr/local/bin/python3

#
#	test_group.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	Unit test for the <group> reource implementation.
#

import unittest
import os, sys, time
sys.path.append('..')

import onem2mlib.session as SE
import onem2mlib.constants as CON
from onem2mlib.resources import *

from conf import *


class TestGroup(unittest.TestCase):
	session = None
	cse = None
	ae = None
	grp = None
	cnt0 = None
	cnt1 = None
	cnt2 = None



	@classmethod
	def setUpClass(self):
		TestGroup.session = SE.Session(host, username, password)
		TestGroup.cse = CSEBase(TestGroup.session, CSE_NAME)
		if TestGroup.cse.findAE(AE_NAME):
			print('*** AE with name "' + AE_NAME + '" already present in CSE. Please remove it first.')
			exit()
		TestGroup.ae = AE(TestGroup.cse, resourceName=AE_NAME)
		TestGroup.ae.createInCSE()
		TestGroup.cnt0 = Container(TestGroup.ae, resourceName=CNT_NAME+'0')
		TestGroup.cnt0.createInCSE()
		TestGroup.cnt1 = Container(TestGroup.ae, resourceName=CNT_NAME+'1')
		TestGroup.cnt1.createInCSE()
		TestGroup.cnt2 = Container(TestGroup.ae, resourceName=CNT_NAME+'2')
		TestGroup.cnt2.createInCSE()


	@classmethod
	def tearDownClass(self):
		if TestGroup.ae:
			TestGroup.ae.deleteFromCSE()
			TestGroup.ae = None


	def test_init(self):
		self.assertTrue(TestGroup.session.connected)
		self.assertIsNotNone(TestGroup.session)
		self.assertIsNotNone(TestGroup.cse)
		self.assertIsNotNone(TestGroup.cse.resourceID)
		self.assertIsNotNone(TestGroup.ae)
		self.assertIsNotNone(TestGroup.ae.resourceID)
		self.assertIsNotNone(TestGroup.cnt0)
		self.assertIsNotNone(TestGroup.cnt0.resourceID)
		self.assertIsNotNone(TestGroup.cnt1)
		self.assertIsNotNone(TestGroup.cnt1.resourceID)
		self.assertIsNotNone(TestGroup.cnt2)
		self.assertIsNotNone(TestGroup.cnt2.resourceID)


	def test_createGroup(self):
		containers = TestGroup.ae.containers()
		self.assertIsNotNone(containers)
		self.assertTrue(len(containers) == 3)
		TestGroup.grp = Group(TestGroup.ae, resourceName=GRP_NAME, resources=containers)
		self.assertEqual(TestGroup.grp.type, CON.Type_Group)
		TestGroup.grp.createInCSE()
		self.assertEqual(TestGroup.grp.resourceName, GRP_NAME)
		self.assertTrue(TestGroup.grp.memberTypeValidated)
		self.assertEqual(TestGroup.grp.currentNrOfMembers, len(containers))
		self.assertTrue(TestGroup.grp.currentNrOfMembers <= TestGroup.grp.maxNrOfMembers)
		self.assertEqual(TestGroup.grp.memberType, CON.Type_Container)
		self.assertEqual(TestGroup.grp.consistencyStrategy, CON.Grp_ABANDON_MEMBER)
		self.assertIsNotNone(TestGroup.grp.fanOutPoint)
		for cont in containers:
			self.assertTrue(cont.resourceID in TestGroup.grp.memberIDs)


	def test_retrieveGroup(self):
		self.assertIsNotNone(TestGroup.grp)
		ri = TestGroup.grp.resourceID
		rn = TestGroup.grp.resourceName
		mm = TestGroup.grp.memberIDs
		TestGroup.grp = TestGroup.cse.retrieveResource(ri)
		self.assertIsNotNone(TestGroup.grp)
		self.assertEqual(TestGroup.grp.resourceID, ri)
		self.assertEqual(TestGroup.grp.resourceName, rn)
		self.assertEqual(TestGroup.grp.memberIDs, mm)


	def test_findGroup(self):
		self.assertIsNotNone(TestGroup.ae)
		grp = TestGroup.ae.findGroup(GRP_NAME)
		self.assertIsNotNone(grp)
		self.assertEqual(TestGroup.grp.resourceID, grp.resourceID)


	def test_updateGroup(self):
		self.assertIsNotNone(TestGroup.grp)
		del TestGroup.grp.memberIDs[-1:]		# remove last element
		self.assertEqual(len(TestGroup.grp.memberIDs), 2)
		self.assertTrue(TestGroup.grp.updateInCSE())
		self.assertEqual(len(TestGroup.grp.memberIDs), 2)


	def getGroupResources(self):
		self.assertIsNotNone(TestGroup.grp)
		resources = TestGroup.grp.getGroupResources()
		self.assertIsNotNone(resources)
		self.assertEqual(len(resources), 2)
		self.assertEqual(resources[0].resourceID, TestGroup.cnt0.resourceID)
		self.assertEqual(resources[1].resourceID, TestGroup.cnt1.resourceID)


	def updateGroupResources(self):
		self.assertIsNotNone(TestGroup.grp)
		self.assertTrue(TestGroup.cnt0.retrieveFromCSE())	# <container> cnt0 and cnt1 should be retrievable
		self.assertTrue(TestGroup.cnt1.retrieveFromCSE())
		cnt = Container()
		cnt.maxNrOfInstances = 99
		self.assertIsNotNone(TestGroup.grp.updateGroupResources(cnt))
		self.assertTrue(TestGroup.cnt0.retrieveFromCSE())	# Retrieve updated versions from the CSE
		self.assertTrue(TestGroup.cnt1.retrieveFromCSE())
		self.assertEqual(TestGroup.cnt0.maxNrOfInstances, 99)
		self.assertEqual(TestGroup.cnt1.maxNrOfInstances, 99)


	def createGroupResources(self):
		self.assertIsNotNone(TestGroup.grp)
		cin = ContentInstance(content=CIN_CONTENT)
		self.assertIsNotNone(cin)
		cins = TestGroup.grp.createGroupResources(cin)
		cin0 = TestGroup.cnt0.latestContentInstance()
		self.assertIsNotNone(cin0)
		cin1 = TestGroup.cnt1.latestContentInstance()
		self.assertIsNotNone(cin1)
		self.assertEqual(cins[0].resourceID, cin0.resourceID)
		self.assertEqual(cins[0].content, CIN_CONTENT)
		self.assertEqual(cins[1].resourceID, cin1.resourceID)
		self.assertEqual(cins[1].content, CIN_CONTENT)


	def deleteGroupResources(self):
		self.assertIsNotNone(TestGroup.grp)
		self.assertTrue(TestGroup.cnt0.retrieveFromCSE())	# <container> cnt0 and cnt1 should be retrievable
		self.assertTrue(TestGroup.cnt1.retrieveFromCSE())
		self.assertTrue(TestGroup.grp.deleteGroupResources())
		self.assertFalse(TestGroup.cnt0.retrieveFromCSE())	# <container> cnt0 and cnt1 should be deleted now
		self.assertFalse(TestGroup.cnt1.retrieveFromCSE())


	def test_deleteGroup(self):
		self.assertIsNotNone(TestGroup.grp)
		self.assertTrue(TestGroup.grp.deleteFromCSE())
		self.assertEqual(len(TestGroup.ae.groups()), 0)


	def test_finit(self):
		self.assertIsNotNone(TestGroup.ae)
		self.assertTrue(TestGroup.ae.deleteFromCSE())
		TestGroup.ae = None


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestGroup('test_init'))
	suite.addTest(TestGroup('test_createGroup'))
	suite.addTest(TestGroup('test_retrieveGroup'))
	suite.addTest(TestGroup('test_findGroup'))
	suite.addTest(TestGroup('test_updateGroup'))
	suite.addTest(TestGroup('getGroupResources'))	
	suite.addTest(TestGroup('updateGroupResources'))	
	suite.addTest(TestGroup('createGroupResources'))	
	suite.addTest(TestGroup('deleteGroupResources'))	
	suite.addTest(TestGroup('test_deleteGroup'))
	suite.addTest(TestGroup('test_finit'))

	unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
