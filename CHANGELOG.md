
# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.1.2] - 2026-04-28

* Fix :
  * transform in List/Dict/Tuples not applied
  * json_encode for soecific types in List/Tuple not correctly applyed
* Feature : 
  * Adding base64 decode try for Bytes()
* Internal :
  * Adding tests for Dict


## [0.1.1] - 2026-04-13

* Adding get_encoded() method

## [0.1.0] - 2026-04-08

* remove typing_extentions requirements
* minimize Human errors
  * change in= to enum= in kwargs options (BREAKING CHANGE)
  * prevent using method or attributes as key for Dict
  * add Kparse
  * Adding toolbox for annotation checker on some calls
* Fix
  * fix bug copy List
  * fix kwargs option bugs for rights (default must be None)
  * fix Error str display more user friendly
* Feature
  * Adding Ipaddress extension of Ip
* Doc
  * Nothing new

## [0.0.9] - 2026-03-27

* Improving $and and $or match

## [0.0.8] - 2026-03-11
  
* New features
    * rights permission loop fix
    * sphinx documentation (see docs/ and https://stricto.readthedocs.io/en/latest/ )
    * change Datetime to avoid microseconds
    * Error refactoring
* 
## [0.0.7] - 2025-11-24
  
* New features
    * rights enable()/disable()/get_permissions_status()
    * meta informations with get_current_meta()

## [0.0.6] - 2025-08-05
  
* New features
    * patch()
    * match()
    * rights()

## [0.0.5] - 2024-08-13
  
* New features
    * Schema extraction - get_schema()
    * Views - get_view()
    * Extend type (with Bytes and DateTime type)

## [0.0.4] - 2024-07-12
  
* New features
    * select()
        rfc 9535
    * can_read / can_modify
    * event handling (see trigg() method )
* tons of bugs fix

## [0.0.3] - 2024-05-16
  
* Adding Tuples()

## [0.0.2] - 2024-05-16
  
Here is the first version available on pypi

### Added

### Changed

### Fixed
