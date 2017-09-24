
#
#	test_discovery.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	Unit test for discovery functionality.
#

import unittest
import os, sys, time
sys.path.append('..')

import onem2mlib.session as SE
import onem2mlib.constants as CON
from onem2mlib.resources import *
import onem2mlib.exceptions
import onem2mlib.utilities as UT

from conf import *


class TestDiscovery(unittest.TestCase):
	session = None
	cse = None
	ae = None
	cnt = None
	cin1 = None
	cin2 = None
	c1n3 = None
	cin4 = None


	@classmethod
	def setUpClass(self):
		TestDiscovery.session = SE.Session(host, originator, encoding)
		TestDiscovery.cse = CSEBase(TestDiscovery.session, CSE_ID)
		if not TestDiscovery.session.connected:
			print('*** Not connected to CSE')
			exit()
		if TestDiscovery.cse.findAE(AE_NAME):
			print('*** AE with name "' + AE_NAME + '" already present in CSE. Please remove it first.')
			exit()
		

	@classmethod
	def tearDownClass(self):
		if TestDiscovery.ae:
			TestDiscovery.ae.deleteFromCSE()
			TestDiscovery.ae = None


	def test_init(self):
		TestDiscovery.ae = AE(TestDiscovery.cse, resourceName=AE_NAME)
		TestDiscovery.ae.createInCSE()
		TestDiscovery.cnt = Container(TestDiscovery.ae, resourceName=CNT_NAME)
		TestDiscovery.cnt.createInCSE()
		TestDiscovery.cin1 = ContentInstance(TestDiscovery.cnt, resourceName=CIN_NAME+'1', content='value1', labels=[CIN_LABELS[0], CIN_LABELS[1]], instantly=True)	# both labels
		TestDiscovery.cin2 = ContentInstance(TestDiscovery.cnt, resourceName=CIN_NAME+'2', content='value2', labels=[CIN_LABELS[0]], instantly=True)				# only label 1
		TestDiscovery.cin3 = ContentInstance(TestDiscovery.cnt, resourceName=CIN_NAME+'3', content='value3', labels=[CIN_LABELS[1]], instantly=True)				# only label 2
		TestDiscovery.cin4 = ContentInstance(TestDiscovery.cnt, resourceName=CIN_NAME+'4', content='value4', instantly=True) 										# no label
		self.assertTrue(TestDiscovery.session.connected)
		self.assertIsNotNone(TestDiscovery.session)
		self.assertIsNotNone(TestDiscovery.cse)
		self.assertIsNotNone(TestDiscovery.cse.resourceID)
		self.assertIsNotNone(TestDiscovery.ae)
		self.assertIsNotNone(TestDiscovery.ae.resourceID)
		self.assertIsNotNone(TestDiscovery.cnt)
		self.assertIsNotNone(TestDiscovery.cnt.resourceID)
		self.assertIsNotNone(TestDiscovery.cin1)
		self.assertIsNotNone(TestDiscovery.cin1.resourceID)
		self.assertIsNotNone(TestDiscovery.cin2)
		self.assertIsNotNone(TestDiscovery.cin2.resourceID)
		self.assertIsNotNone(TestDiscovery.cin3)
		self.assertIsNotNone(TestDiscovery.cin3.resourceID)
		self.assertIsNotNone(TestDiscovery.cin4)
		self.assertIsNotNone(TestDiscovery.cin4.resourceID)


	def test_discoverContainer(self):
		self.assertIsNotNone(TestDiscovery.ae)
		containers = TestDiscovery.ae.discover( [UT.newTypeFilterCriteria(CON.Type_Container)] )
		self.assertIsNotNone(containers)
		self.assertIsInstance(containers, list)
		self.assertEqual(len(containers), 1)
		self.assertIsInstance(containers[0], Container)
		self.assertEqual(containers[0].resourceName, CNT_NAME)


	def test_discoverLabel1(self):
		self.assertIsNotNone(TestDiscovery.ae)
		cins = TestDiscovery.ae.discover( [UT.newLabelFilterCriteria(CIN_LABELS[0])] )
		self.assertIsNotNone(cins)
		self.assertIsInstance(cins, list)
		self.assertEqual(len(cins), 2)
		self.assertIsInstance(cins[0], ContentInstance)
		self.assertEqual(cins[0].resourceName, CIN_NAME+'1')
		self.assertIsInstance(cins[1], ContentInstance)
		self.assertEqual(cins[1].resourceName, CIN_NAME+'2')


	def test_discoverLabel2(self):
		self.assertIsNotNone(TestDiscovery.ae)
		cins = TestDiscovery.ae.discover( [UT.newLabelFilterCriteria(CIN_LABELS[1])] )
		self.assertIsNotNone(cins)
		self.assertIsInstance(cins, list)
		self.assertEqual(len(cins), 2)
		self.assertIsInstance(cins[0], ContentInstance)
		self.assertEqual(cins[0].resourceName, CIN_NAME+'1')
		self.assertIsInstance(cins[1], ContentInstance)
		self.assertEqual(cins[1].resourceName, CIN_NAME+'3')


	def test_discoverLabel3(self):
		self.assertIsNotNone(TestDiscovery.ae)
		cins = TestDiscovery.ae.discover( [UT.newLabelFilterCriteria(CIN_LABELS[0]), UT.newLabelFilterCriteria(CIN_LABELS[1])] )
		self.assertIsNotNone(cins)
		self.assertIsInstance(cins, list)
		try:
			self.assertEqual(len(cins), 3)
			self.assertIsInstance(cins[0], ContentInstance)
			self.assertEqual(cins[0].resourceName, CIN_NAME+'1')
			self.assertIsInstance(cins[1], ContentInstance)
			self.assertEqual(cins[1].resourceName, CIN_NAME+'2')
			self.assertIsInstance(cins[2], ContentInstance)
			self.assertEqual(cins[2].resourceName, CIN_NAME+'3')
		except (AssertionError):
			print('WARNING: discovery of multiple labels might be wrong in Eclipse om2m" ... ', end='', flush=True)


	def test_finit(self):
		self.assertIsNotNone(TestDiscovery.ae)
		self.assertTrue(TestDiscovery.ae.deleteFromCSE())
		TestDiscovery.ae = None


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestDiscovery('test_init'))
	suite.addTest(TestDiscovery('test_discoverContainer'))
	suite.addTest(TestDiscovery('test_discoverLabel1'))
	suite.addTest(TestDiscovery('test_discoverLabel2'))
	suite.addTest(TestDiscovery('test_discoverLabel3'))
	suite.addTest(TestDiscovery('test_finit'))

	unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
