.. toctree::
   :maxdepth: 2
   :hidden:


.. _bigmler-project:

Project subcommand
------------------

Projects are organizational resources and they are usually created at
source-creation time in order to keep together in a separate repo all
the resources derived from a source. However, you can also create a project
or update its properties independently using the ``bigmler project``
subcommand.

.. code-block:: bash

    bigmler project --name my_project

will create a new project and name it. You can also add other attributes
such as ``--tag``, ``--description`` or ``--category`` in the project
creation call. You can also add or update any other attribute to
the project using a JSON file with the ``--project-attributes`` option.

.. code-block:: bash

    bigmler project --project-id project/532db2b637203f3f1a000153 \
                    --project-attributes my_attributes.json


Project Specific Subcommand Options
-----------------------------------

===================================== =========================================
``--organization`` *ORGANIZATION_ID*  Organization ID to create projects
                                      in an organization
``--project-attributes``              Path to a JSON file containing
                                      attributes for the project
===================================== =========================================
