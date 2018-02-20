# onem2mlib
**Version 0.7**

This Python3 module implements a library to access and manage resources on a oneM2M CSE.

## Introduction

This Python3 module implements a library to access and manage resources on a oneM2M CSE.

[oneM2M](http://www.onem2m.org) is a global partnership project that specifies a common service layer, called *CSE*, for M2M and the Internet of Things. In general, devices, services, applications, and data are organized in a resources tree, which is transported and synchronized through a network of nodes. This resource tree can be access via [CRUD](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) operations. 

The application interface to the oneM2M's *CSE* is called *Mca*. This Python3 module implements an easy way to access a *CSE* via this interface.

For further information about oneM2M and its specifications see [http://www.onem2m.org](http://www.onem2m.org) resp. [http://www.onem2m.org/technical/published-documents](http://www.onem2m.org/technical/published-documents)

### Compatibility

*onem2mlib* has been tested with the following oneM2M implementations:

-  [Eclipse om2m](http://www.eclipse.org/om2m/) (feature0 branch)

More implementations should follow.

## Installation and Prerequisites

This module requires Python3.

Copy the *onem2mlib* directory to your project.

In addition you need to install the following modules:

- [requests](http://docs.python-requests.org/en/master/)
- [lxml](http://lxml.de)

### requests
Install with pip3:

```bash
pip3 install lxml
```

### LXML

Install with pip3:

```bash
pip3 install lxml
```

Depending on the OS and target environment you might need to install some additional libraries:

```bash
apt-get install libxml2-dev libxslt1-dev
```

#### Using a package manager
All this might take a very long time on a small system (such as a Raspberry Pi). Alternative you may install the library with the help of a package manager:

```bash
sudo apt-get install python3-lxml
```


## Usage

Read the [full module documentation](http://htmlpreview.github.io/?https://raw.githubusercontent.com/ankraft/onem2mlib/master/doc/onem2mlib/index.html).

Have a look at the examples in the [examples](./examples) directory on how to use the *onem2mlib* module.

The following sections provide some examples.

### Connect to a CSE

First, create a session and then retrieve a &lt;CSEBase> resource from a CSE. The session holds, for example, the authentication information to access the CSE.

```python
session = Session('http://host.com:8282', 'admin:admin').   # create a session
cse = CSEBase(session, 'mn-cse')                            # get the <CSEBase> resource
```

To use XML encoding, specify the encoding explicitly for a session.

```python
from onem2mlib.constants import *
session = Session('http://host.com:8282', 'admin:admin', Encoding_XML).   # create a session with XML encoding
cse = CSEBase(session, 'mn-cse')                                          # get the <CSEBase> resource
```

To access resources on a CSE it is not necessary to retrieve the &lt;CSEBase> resource from the CSE (for example, when one has only limited access to resources on the CSE). But one must have at least create a *CSEBase* **instance** that represents the CSE and holds the session information as shown above. This *CSEBase* instance can be used as usual in subsequent calls.

The following example creates a *CSEBase* **instance** without actually retrieving the &lt;CSEBase> **resource**. The *resourceName* attribute must be known and set explicitly in the constructor. The *instantly=False* argument must also be set; it prevents the retrieval of the actual resource (which, as explained above, might fail when there is only limited access to the CSE).

```python
session = Session('http://host.com:8282', 'admin:admin').                 # create a session
cse = CSEBase(session, 'mn-cse', resourceName='mn-name', instantly=False) # create a CSEBase object, without retrieving it
```

### Create an &lt;AE> resource in a CSE

The first example creates a new &lt;AE> resource or, if an &lt;AE> resource with the same name already exists in the CSE, that &lt;AE> is returned. This method to get/create a resource is usually sufficient in most cases.

```python
ae = AE(cse, resourceName='aeName')
```

The second example is similar to the first, but offers the possibility to modify the resource object before sending it to the CSE.
In general, the *get()* method creates a new or retrieves an existing resource.

```python
ae = AE(cse, resourceName='aeName', instantly=False)
# set more attributes here
ae.get()
```

The last example also creates a new &lt;AE> resource in the CSE, but does it explicitly. It fails (ie. returns *False*) in case a resource with the same name already exists.

```python
ae = AE(cse, resourceName='aeName', instantly=False)
# set more attributes here
ae.createInCSE()
```

### Add a &lt;container> resource to an &lt;AE>
Add a container to an &lt;AE> resource.

```python
container = Container(ae, resourceName='myContainer')
```

### Get all &lt;container> resources of an &lt;AE>
And print them.  
And add a &lt;contentInstances> to each of them.
	
```python
for cnt in ae.containers():
	print(cnt)
	# Create and add a new <contentInstance> in one step 
	ContentInstance(cnt, content='Some value')    
```

There is also a  shortcut for adding a new &lt;contentInstance> to a &lt;container>. So, the last line in this example could also be written like this:

```python
	cnt.addContent('Some value')
``` 
### Retrieve the latest &lt;contentInstance> from a &lt;container> resource
And print it.

```python 
cin = container.latestContentInstance()
if cin is not None:
	print(cin)
```

There is a short-cut in case you are only interested in the content.

```python 
print(container.latestContent())
```

### Delete an &lt;AE> from a CSE
Delete an &lt;AE> resource and all its sub-resource from a CSE.

	ae.deleteFromCSE()

### Subscribe to Notifications
Add a subscription to a resource and receive notifications when the resource changes.

```python
def myCallback(resource):		# Called for notifications
								# The parameter is the updated resource
	# do something with the updated resource
	...

# In the main program:
setupNotifications(myCallback)  # Initialize the notification sub-module
...
cnt = Container(ae)             # Create a container
cnt.subscribe()                 # Subscribe to changes of this resource
cnt.addContent('Some value')    # Add a new contentInstance
                                # This implicitly triggers a call to 'myCallback' when the value us changed in the CSE
```

There could also be individual callbacks for each resource. Provide another function in the *subscribe()* method call.

```python
...
cnt.subscribe(anotherCallback)          # Subscribe to changes of this resource, and provide a different callback function
...
```

Remove a subscription by calling the *unsubscribe()* method:

```python
...
cnt.unsubscribe()          # Notifications for this resource will stop
...
```


## Supported Features & Limitations

See also [ROADMAP](ROADMAP.md) for open issues and planned enhancements.

### Resources
The following resource types are supported in this version.

- [&lt;CSEBase>](http://htmlpreview.github.io/?https://raw.githubusercontent.com/ankraft/onem2mlib/master/doc/onem2mlib/resources.m.html#onem2mlib.resources.CSEBase)
- [&lt;AE>](http://htmlpreview.github.io/?https://raw.githubusercontent.com/ankraft/onem2mlib/master/doc/onem2mlib/resources.m.html#onem2mlib.resources.AE)
- [&lt;container>](http://htmlpreview.github.io/?https://raw.githubusercontent.com/ankraft/onem2mlib/master/doc/onem2mlib/resources.m.html#onem2mlib.resources.Container)
- [&lt;contentInstance>](http://htmlpreview.github.io/?https://raw.githubusercontent.com/ankraft/onem2mlib/master/doc/onem2mlib/resources.m.html#onem2mlib.resources.ContentInstance)
- [&lt;group>](http://htmlpreview.github.io/?https://raw.githubusercontent.com/ankraft/onem2mlib/master/doc/onem2mlib/resources.m.html#onem2mlib.resources.Group)
- [&lt;accessControlPolicy>](http://htmlpreview.github.io/?https://raw.githubusercontent.com/ankraft/onem2mlib/master/doc/onem2mlib/resources.m.html#onem2mlib.resources.AccessControlPolicy)
- [&lt;subscription>](http://htmlpreview.github.io/?https://raw.githubusercontent.com/ankraft/onem2mlib/master/doc/onem2mlib/resources.m.html#onem2mlib.resources.Subscription)

### Features
- **Discovery**: 
Currently, only *label* and *resourceType* are supported in filter criteria.
- **Encodings**:
JSON (the default), XML.
- **Notifications**: A program can subscribe to resource changes, provide callback methods, and receive notifications from a CSE.

## License

*onem2mlib* is released under the BSD 3-Clause License. 
See [LICENSE](./LICENSE) for the full license text.
