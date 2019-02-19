"""
This Python3 module implements a library to access and manage resources on a oneM2M CSE.

(c) 2017-2019 by Andreas Kraft  
Licensed under the BSD 3-Clause License. See the LICENSE file for further details.

"""
import json, logging, uuid

import onem2mlib.constants as CON
import onem2mlib.exceptions
import onem2mlib.utilities as UT
import onem2mlib.marshalling as M
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

###############################################################################
#
#	Exclude some docstrings to keep the documentation leaner.

__pdoc__                                                 = {}
__pdoc__['CSEBase.createInCSE']                 	     = None
__pdoc__['CSEBase.deleteFromCSE']                        = None
__pdoc__['CSEBase.updateInCSE']                 	     = None
__pdoc__['CSEBase.retrieveFromCSE']                      = None
__pdoc__['CSEBase.get']                                  = None
__pdoc__['CSEBase.discover']                             = None
__pdoc__['CSEBase.setAccessControlPolicies']             = None
__pdoc__['CSEBase.subscribe']                            = None
__pdoc__['CSEBase.unsubscribe']                          = None
__pdoc__['CSEBase.subscriptions']                        = None
__pdoc__['CSEBase.findAccessControlPolicy']              = None
__pdoc__['CSEBase.findAE']                               = None
__pdoc__['CSEBase.findContainer']                        = None
__pdoc__['CSEBase.findContentInstance']                  = None
__pdoc__['CSEBase.findGroup']                            = None
__pdoc__['CSEBase.findSubscription']                     = None
__pdoc__['CSEBase.findRemoteCSE']                        = None

__pdoc__['AE.createInCSE']                               = None
__pdoc__['AE.deleteFromCSE']                             = None
__pdoc__['AE.updateInCSE']                               = None
__pdoc__['AE.retrieveFromCSE']                           = None
__pdoc__['AE.get']                                       = None
__pdoc__['AE.discover']                                  = None
__pdoc__['AE.setAccessControlPolicies']                  = None
__pdoc__['AE.subscribe']                                 = None
__pdoc__['AE.unsubscribe']                               = None
__pdoc__['AE.subscriptions']                             = None
__pdoc__['AE.findAccessControlPolicy']                   = None
__pdoc__['AE.findAE']                                    = None
__pdoc__['AE.findContainer']                             = None
__pdoc__['AE.findContentInstance']                       = None
__pdoc__['AE.findGroup']                                 = None
__pdoc__['AE.findSubscription']                          = None
__pdoc__['AE.findRemoteCSE']                             = None

__pdoc__['AccessControlPolicy.createInCSE']              = None
__pdoc__['AccessControlPolicy.deleteFromCSE']            = None
__pdoc__['AccessControlPolicy.updateInCSE']              = None
__pdoc__['AccessControlPolicy.retrieveFromCSE']          = None
__pdoc__['AccessControlPolicy.get']                      = None
__pdoc__['AccessControlPolicy.discover']                 = None
__pdoc__['AccessControlPolicy.setAccessControlPolicies'] = None
__pdoc__['AccessControlPolicy.subscribe']                = None
__pdoc__['AccessControlPolicy.unsubscribe']              = None
__pdoc__['AccessControlPolicy.subscriptions']            = None
__pdoc__['AccessControlPolicy.findAccessControlPolicy']  = None
__pdoc__['AccessControlPolicy.findAE']                   = None
__pdoc__['AccessControlPolicy.findContainer']            = None
__pdoc__['AccessControlPolicy.findContentInstance']      = None
__pdoc__['AccessControlPolicy.findGroup']                = None
__pdoc__['AccessControlPolicy.findSubscription']         = None
__pdoc__['AccessControlPolicy.findRemoteCSE']            = None

__pdoc__['Container.createInCSE']                        = None
__pdoc__['Container.deleteFromCSE']                      = None
__pdoc__['Container.updateInCSE']                        = None
__pdoc__['Container.retrieveFromCSE']                    = None
__pdoc__['Container.get']                                = None
__pdoc__['Container.discover']                           = None
__pdoc__['Container.setAccessControlPolicies']           = None
__pdoc__['Container.subscribe']                          = None
__pdoc__['Container.unsubscribe']                        = None
__pdoc__['Container.subscriptions']                      = None
__pdoc__['Container.findAccessControlPolicy']            = None
__pdoc__['Container.findAE']                             = None
__pdoc__['Container.findContainer']                      = None
__pdoc__['Container.findContentInstance']                = None
__pdoc__['Container.findGroup']                          = None
__pdoc__['Container.findSubscription']                   = None
__pdoc__['Container.findRemoteCSE']                      = None

__pdoc__['ContentInstance.createInCSE']                  = None
__pdoc__['ContentInstance.deleteFromCSE']                = None
__pdoc__['ContentInstance.updateInCSE']                  = None
__pdoc__['ContentInstance.retrieveFromCSE']              = None
__pdoc__['ContentInstance.get']                          = None
__pdoc__['ContentInstance.discover']                     = None
__pdoc__['ContentInstance.setAccessControlPolicies']     = None
__pdoc__['ContentInstance.subscribe']                    = None
__pdoc__['ContentInstance.unsubscribe']                  = None
__pdoc__['ContentInstance.subscriptions']                = None
__pdoc__['ContentInstance.findAccessControlPolicy']      = None
__pdoc__['ContentInstance.findAE']                       = None
__pdoc__['ContentInstance.findContainer']                = None
__pdoc__['ContentInstance.findContentInstance']          = None
__pdoc__['ContentInstance.findGroup']                    = None
__pdoc__['ContentInstance.findSubscription']             = None
__pdoc__['ContentInstance.findRemoteCSE']                = None

__pdoc__['FlexContainer.createInCSE']         		     = None
__pdoc__['FlexContainer.deleteFromCSE']  		         = None
__pdoc__['FlexContainer.updateInCSE']     		         = None
__pdoc__['FlexContainer.retrieveFromCSE'] 		         = None
__pdoc__['FlexContainer.get']              			     = None
__pdoc__['FlexContainer.discover']            		     = None
__pdoc__['FlexContainer.setAccessControlPolicies']		 = None
__pdoc__['FlexContainer.subscribe']                       = None
__pdoc__['FlexContainer.unsubscribe']                     = None
__pdoc__['FlexContainer.subscriptions']       		     = None
__pdoc__['FlexContainer.findAccessControlPolicy']         = None
__pdoc__['FlexContainer.findAE']                          = None
__pdoc__['FlexContainer.findContainer']                   = None
__pdoc__['FlexContainer.findContentInstance']             = None
__pdoc__['FlexContainer.findGroup']                       = None
__pdoc__['FlexContainer.findSubscription']                = None
__pdoc__['FlexContainer.findRemoteCSE']                   = None

__pdoc__['Group.createInCSE']                            = None
__pdoc__['Group.deleteFromCSE']                          = None
__pdoc__['Group.updateInCSE']                            = None
__pdoc__['Group.retrieveFromCSE']                        = None
__pdoc__['Group.get']                                    = None
__pdoc__['Group.discover']                               = None
__pdoc__['Group.setAccessControlPolicies']       		 = None
__pdoc__['Group.subscribe']                              = None
__pdoc__['Group.unsubscribe']                            = None
__pdoc__['Group.subscriptions']                          = None
__pdoc__['Group.findAccessControlPolicy']                = None
__pdoc__['Group.findAE']                                 = None
__pdoc__['Group.findContainer']                          = None
__pdoc__['Group.findContentInstance']                    = None
__pdoc__['Group.findGroup']                              = None
__pdoc__['Group.findSubscription']                       = None
__pdoc__['Group.findRemoteCSE']                          = None

__pdoc__['RemoteCSE.createInCSE']         		 		 = None
__pdoc__['RemoteCSE.deleteFromCSE']  		             = None
__pdoc__['RemoteCSE.updateInCSE']     		             = None
__pdoc__['RemoteCSE.retrieveFromCSE'] 		             = None
__pdoc__['RemoteCSE.get']              			         = None
__pdoc__['RemoteCSE.discover']            		         = None
__pdoc__['RemoteCSE.setAccessControlPolicies']		     = None
__pdoc__['RemoteCSE.subscribe']                          = None
__pdoc__['RemoteCSE.unsubscribe']                        = None
__pdoc__['RemoteCSE.subscriptions']                      = None
__pdoc__['RemoteCSE.findAccessControlPolicy']            = None
__pdoc__['RemoteCSE.findAE']                             = None
__pdoc__['RemoteCSE.findContainer']                      = None
__pdoc__['RemoteCSE.findContentInstance']                = None
__pdoc__['RemoteCSE.findGroup']                          = None
__pdoc__['RemoteCSE.findSubscription']                   = None
__pdoc__['RemoteCSE.findRemoteCSE']                      = None

__pdoc__['Subscription.createInCSE']         		     = None
__pdoc__['Subscription.deleteFromCSE']  		         = None
__pdoc__['Subscription.updateInCSE']     		         = None
__pdoc__['Subscription.retrieveFromCSE'] 		         = None
__pdoc__['Subscription.get']              			     = None
__pdoc__['Subscription.discover']            		     = None
__pdoc__['Subscription.setAccessControlPolicies']		 = None
__pdoc__['Subscription.subscribe']                       = None
__pdoc__['Subscription.unsubscribe']                     = None
__pdoc__['Subscription.subscriptions']       		     = None
__pdoc__['Subscription.findAccessControlPolicy']         = None
__pdoc__['Subscription.findAE']                          = None
__pdoc__['Subscription.findContainer']                   = None
__pdoc__['Subscription.findContentInstance']             = None
__pdoc__['Subscription.findGroup']                       = None
__pdoc__['Subscription.findSubscription']                = None
__pdoc__['Subscription.findRemoteCSE']                   = None

__pdoc__['Node.createInCSE']         				     = None
__pdoc__['Node.deleteFromCSE']  		 		         = None
__pdoc__['Node.updateInCSE']     		 		         = None
__pdoc__['Node.retrieveFromCSE'] 		 		         = None
__pdoc__['Node.get']              					     = None
__pdoc__['Node.discover']            				     = None
__pdoc__['Node.setAccessControlPolicies']				 = None
__pdoc__['Node.subscribe']                  		     = None
__pdoc__['Node.unsubscribe']                		     = None
__pdoc__['Node.subscriptions']       				     = None
__pdoc__['Node.findAccessControlPolicy']    		     = None
__pdoc__['Node.findAE']                     		     = None
__pdoc__['Node.findContainer']              		     = None
__pdoc__['Node.findContentInstance']        		     = None
__pdoc__['Node.findGroup']                  		     = None
__pdoc__['Node.findSubscription']           		     = None
__pdoc__['Node.findRemoteCSE']              		     = None
