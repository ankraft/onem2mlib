#
#	conf.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This is the configuration file for the unit tests. 
#	Change the settings for *host*, *username*, and *password* according to your setup.

import sys
sys.path.append('..')
import onem2mlib.constants as CON

host		= 'http://localhost:8282'
originator	= 'admin:admin'
#encoding	= CON.Encoding_XML
encoding	= CON.Encoding_JSON
delayInSec	= 1

CSE_NAME	= 'mn-name'
CSE_ID		= 'mn-cse'

AE_NAME		= 'TEST_AE'
AE_APPID	= 'test_appid'
AE_AEID		= None
AE_LABELS	= ['test/test', 'aLabel/Another%20Label']

ACP_NAME	= 'TEST_ACP'

ACP_LIMITED = 'limited:limited'


CNT_NAME	= 'TEST_CONTAINER'
CNT_LABELS	= ['test/test', 'aLabel/AnotherLabel']
CNT_MNI		= 1

CIN_NAME	= 'TEST_CONTENTINSTANCE'
CIN_LABELS	= ['test/test', 'aLabel/AnotherLabel']
CIN_CONTENT	= 'Hello, World'

GRP_NAME	= 'TEST_GROUP'


FCNT_NAME	= 'TEST_FLEXCONTAINER'

