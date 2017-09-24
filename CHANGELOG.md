# CHANGELOG

## Version 0.5 (xxxx-xx-xx)
- [IMPROVEMENT] Added support for JSON encoding to communicate with a CSE. JSON is now the default encoding.
- [IMPROVEMENT] Added better checks in various functions. Raising more exceptions when encounting wrong or empty resources.
- [CHANGE] Moved marshalling functions to an extra source file.
- [CHANGE] Refactored some internal functions
- [FIX] Fixed some test cases.

## Version 0.4 (2017-09-10)
- [IMPROVEMENT] Added general discovery support. Currently supported attributes are *label* and *type*.
- [FIX] Added more tests for &lt;contentInstances>.
- [FIX] Improved speed of discovery of direct sub-resources.
- [CHANGE] Moved basic operations from individual resource classes to the ResourceBase class.
- [CHANGE] Renamed the internal utilities sub-module. Introduced new utilities sub-module for public use.
- [CHANGE] Refactored the internal discovery functions.

## Version 0.3 (2017-09-01)
- [IMPROVEMENT] Better handling of lost connections to the CSE. Added connection timeout.
- [IMPROVEMENT] Support for &lt;accessControlPolicy>.
- [FIX] Small bug fixes and stability improvements.
- [CHANGE] Changed originator format in Sessions

## Version 0.2 (2017-08-20)
- [FIX] Small bug fixes and speed improvements.
- [IMPROVEMENT] Simplified handling when creating and retrieving resources.

## Version 0.1 (2017-08-13)
- First release