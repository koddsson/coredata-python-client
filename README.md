Coredata Python API Client
==========================
[![travis build](https://travis-ci.org/koddsson/coredata-python-client.svg?branch=master)](https://travis-ci.org/koddsson/coredata-python-client)
[![Coverage Status](https://img.shields.io/coveralls/koddsson/coredata-python-client.svg)](https://coveralls.io/r/koddsson/coredata-python-client)

A Python 2/3 client for the Coredata REST API.


Testing
-------
Currently only have unittests which can be transformed into integration test by
disabling httpretty when running them. The integration tests have yet to be run
against a server so expect there to be errors.


Contributing
------------
Feel free to file issues or pull requests if there is something you need or if
something is breaking. You can also get me on
[twitter](https://twitter.com/koddsson).

TODO
----
- Go over each and every endpoint and make sure there exists a test for it.
- Add tests in super class for deleting and editing.
- Run integration tests against a running server.
