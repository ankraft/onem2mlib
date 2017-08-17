# onem2mlib
**Version 0.1**

This Python3 module implements a library to access and manage resources on a oneM2M CSE.

## Introduction

This Python3 module implements a library to access and manage resources on a oneM2M CSE.

[oneM2M](http://www.onem2m.org) is a global partnership project that specifies a common service layer, called *CSE*, for M2M and the Internet of Things. In general, devices, services, applications, and data are organized in a resources tree, which is transported and synchronized through a network of nodes. This resource tree can be access via [CRUD](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) operations. 

The application interface to the oneM2M's *CSE* is called *Mca*. This Python3 module implements an easy way to access a *CSE* via this interface.

For further information about oneM2M and its specifications see [http://www.onem2m.org](http://www.onem2m.org) resp. [http://www.onem2m.org/technical/published-documents](http://www.onem2m.org/technical/published-documents)

### Compatibility

*onem2mlib* has been tested with the following oneM2M implementations:

-  [Eclipse om2m](http://www.eclipse.org/om2m/) (feature0 branch)

More implementaions should follow.

## Installation

This module requires Python3.

Copy the *onem2mlib* directory to your project.

In addition you need to install the [lxml](http://lxml.de) library (install it with ``pip3 install lxml``).


## Usage

Read the [full module documentation](http://htmlpreview.github.io/?https://raw.githubusercontent.com/ankraft/onem2mlib/master/doc/onem2mlib/index.html).

Have a look at the examples in the [examples](./examples) directory on how to use the *onem2mlib* module.

Some examples

### Connect to a CSE

	# create session
	session = SE.Session('http://host.com:8282', 'admin', 'admin')
	# get the <CSEBase> resource
	cse = CSEBase(session, 'mn-cse')

### Create an &lt;AE> resource in a CSE

	ae = AE(cse, resourceName='aeName')
	ae.createInCSE()

### Find all &lt;container> resources of an &lt;AE>
And print them.  
And add a &lt;contentInstances> to each of it.
	
	containers = TestAE.ae.containers()
	for cnt in containers:
		print(cnts)
		cin = ContentInstance(cnt, content='some Value')
		cin.createInCSE()


### Delete an &lt;AE> from a CSE

	ae.deleteFromCSE()


## Supported Features & Limitations
The following resource types are supported in this version.

- [&lt;CSEBase>](http://htmlpreview.github.io/?https://raw.githubusercontent.com/ankraft/onem2mlib/master/doc/onem2mlib/resources.m.html#onem2mlib.resources.CSEBase)
- [&lt;AE>](http://htmlpreview.github.io/?https://raw.githubusercontent.com/ankraft/onem2mlib/master/doc/onem2mlib/resources.m.html#onem2mlib.resources.AE)
- [&lt;container>](http://htmlpreview.github.io/?https://raw.githubusercontent.com/ankraft/onem2mlib/master/doc/onem2mlib/resources.m.html#onem2mlib.resources.Container)
- [&lt;contentInstance>](http://htmlpreview.github.io/?https://raw.githubusercontent.com/ankraft/onem2mlib/master/doc/onem2mlib/resources.m.html#onem2mlib.resources.ContentInstance)
- [&lt;group>](http://htmlpreview.github.io/?https://raw.githubusercontent.com/ankraft/onem2mlib/master/doc/onem2mlib/resources.m.html#onem2mlib.resources.Group)

See also [ROADMAP](ROADMAP.md) for open issues and planned enhancements.

## License

*onem2mlib* is released under the BSD 3-Clause License. 
See [LICENSE](./LICENSE) for the full license text.
