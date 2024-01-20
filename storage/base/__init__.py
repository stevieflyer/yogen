"""`db.base` Base package for database
This module defines some interface class for database connection and manipulation.

`Connector` refers to the connection to the database, which is responsible for
the connection and disconnection to the database.

`Storage` refers to the database manipulator, which is responsible for the
database operations, such as CRUD. Storage objects always have an inner connector
to handle connection issues.

You can check out the interface design in `*_interface.py`.

For implementation classes, please refer to `..vendor` packages.
"""
from .storage_interface import *
from .connector_interface import *
