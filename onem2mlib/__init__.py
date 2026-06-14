"""
This Python3 module implements a library to access and manage resources on a oneM2M CSE.

(c) 2017-2019 by Andreas Kraft  
Licensed under the BSD 3-Clause License. See the LICENSE file for further details.

"""
import json, logging, uuid

import onem2mlib.constants as CON
import onem2mlib.exceptions
import onem2mlib.utilities as UT
import onem2mlib.mcarequests as MCA
import onem2mlib.internal as INT
import onem2mlib.exceptions as EXC
import onem2mlib.notifications as NOT
from .resources.Session import *
from .resources.ResourceBase import *
from .resources.AccessControlPolicy import *
from .resources.AE import *
from .resources.Container import *
from .resources.ContentInstance import *
from .resources.CSEBase import *
from .resources.FlexContainer import *
from .resources.Group import *
from .resources.Node import *
from .resources.RemoteCSE import *
from .resources.Subscription import *


__all__ = [	'AccessControlPolicy', 'AccessControlRule', 'AE', 'Container',
			'ContentInstance', 'CSEBase', 'FlexContainer', 'Group', 'Node',
			'RemoteCSE', 'Subscription', 'ResourceBase', 'Session',
			'constants', 'exceptions', 'utilities', 'notifications']

logger = logging.getLogger(__name__)

# TODO:
# - Test remoteCSE
