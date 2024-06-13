.. toctree::
   :maxdepth: 2
   :hidden:


.. _bigmler-connector:

Connector subcommand
====================

Connections to external databases can be used to upload data to BigML. The
``bigmler connector`` subcommand can be used to create such connections in the
platform. The result will be an ``externalconnector`` object, that can be
reused to perform queries on the database and upload the results to create
the corresponding ``source`` in BigML.

.. code-block:: bash

    bigmler connector --host my_data.hostname.com \
                      --port 1234                 \
                      --engine postgresql         \
                      --user my_username          \
                      --password my_password      \
                      --database my_database      \
                      --output-dir out

As you can see, the options needed to create an external connector are:

- the host that publishes the database manager
- the port that listens to the requests
- the type of database manager: PostgreSQL, MySQL, Elasticsearch or
  SQL Server.
- the user and password needed to grant the access to the database

With this information, the command will create an ``externalconnector`` object
that will be assigned an ID. This ID will be the reference to be used when
querying the database for new data. Please, check the `remote sources
<#remote-sources>`_ section to see an example of that.


External Connector Specific Subcommand Options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

============================================ =================================
``--external-connector-id`` *CONNECTOR_ID*   external connector ID used as
                                             reference to create sources from
                                             database queries
``--host`` *HOST*                            Database host name
``--hosts`` *HOSTS*                          Comma-separated list of database
                                             host names (elasticsearch only)
``--port`` *PORT*                            Database port number
``--engine`` *KIND*                          Kind of database manager engine:
                                             mysql, postgresql, elasticsearch,
                                             sqlserver
``--database`` *DATABASE*                    Database name
``--user`` *USER*                            Database user name
``--password`` *PWD*                         Database user password
``--connection-json`` *FILE*                 Path to a JSON file containing
                                             the map of attributes to create a
                                             connection as described in
                                             the `API documentation
                                             <https://bigml.com/api/sources#sr_creating_a_source_using_external_data>`_
============================================ =================================
