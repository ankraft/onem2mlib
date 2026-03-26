#
#	Session.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for Session handling.
#

import logging
import onem2mlib.constants as CON
import onem2mlib.exceptions as EXC
import onem2mlib.internal as INT
import onem2mlib.mcarequests as MCA


logger = logging.getLogger(__name__)

class Session:
	"""
	A Session object is used when connecting to a oneM2M CSE. It holds various information
	about the current session, such as the CSE endpoint, credentials, desired encoding, etc.
	"""

	def __init__(self, address,  originator, encoding=CON.Encoding_JSON):
		"""
		Initialize a Session object. 

		Please note, the credentials (the originator) are currently hold unsecured in
		Session instances.

		Args:

		- *address*: String. The URL of the CSE host to connect to. This includes the protocol, hostname, 
			port number, and any API prefix etc.
		- *originator*: String. The originator for identification in access control policies.
		- *encoding*: Integer. The encoding of request content. Optional, the default is
			`onem2mlib.constants.Encoding_JSON`. Providing a wrong encoding will throw a `onem2mlib.exceptions.NotSupportedError`
			exception.
		"""
		self.address = address
		""" String. The URL of the CSE host to connect to. The address includes the protocol, hostname, 
			port number, and any API prefix etc. """
		while self.address is not None and self.address.endswith('/'):
			self.address = self.address[:-1]

		self.originator = originator
		""" String. This specifies the originator for identification in access control policies. 
			It can be a domain, an originatorID, the string "all", or a role-ID. """

		self.encoding = encoding
		"""	Integer, either `onem2mlib.constants.Encoding_XML` or `onem2mlib.constants.Encoding_JSON`.
			It specifies the type of encoding for requests between the AE and the CSE. """
		if self.encoding not in [CON.Encoding_XML, CON.Encoding_JSON]:
			logger.critical('Unsupported encoding: ' + str(self.encoding))
			raise EXC.NotSupportedError('Unsupported encoding: ' + str(self.encoding))
		if self.encoding == CON.Encoding_XML and not CON.Support_XML:
			logger.critical('Unsupported encoding: Encoding_XML.')
			raise EXC.NotSupportedError('Unsupported encoding: Encoding_XML')
		if not self.originator:
			logger.error('Missing accessControlOriginator')
			raise EXC.AuthenticationError('Missing accessControlOriginator')

	
	def getCSEBase(self):
		"""
		Retrieves the CSEBase resource directly from the root path.
		Returns a populated CSEBase object.
		"""
  
		response = MCA.get(self, '-') 

		if response and response.status_code == 200:
			from onem2mlib import CSEBase
   
			resource = CSEBase(session=self, instantly=False)
			
			resource._parseResponse(response)
			
			return resource

		error_text = ""
		if response:
			error_text = f"{response.status_code} - {response.text}"
		else:
			error_text = "No response received from CSE"

		logger.error('Retrieve CSEBase failed: ' + error_text)
		raise EXC.CSEOperationError('Cannot get CSEBase. ' + error_text)


	def __str__(self):
		result = 'Session:\n'
		result += INT.strResource('address', None, self.address)
		result += INT.strResource('originator', None, self.originator)
		result += INT.strResource('encoding', None, self.encoding)
		return result

