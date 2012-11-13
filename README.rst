BigMLer - A higher-level API to BigML's API
===========================================


Support
-------

Please report problems and bugs to our `BigML.io issue
tracker <https://github.com/bigmlcom/io/issues>`_.

Discussions about the different bindings take place in the general
`BigML mailing list <http://groups.google.com/group/bigml>`_. Or join us
in our `Campfire chatroom <https://bigmlinc.campfirenow.com/f20a0>`_.

Requirements
------------

Python 2.6 and Python 2.7 are currently supported by these bindings.

The only mandatory third-party dependencies are the
`requests <https://github.com/kennethreitz/requests>`_,
`poster <http://atlee.ca/software/poster/#download>`_ and
`unidecode <http://pypi.python.org/pypi/Unidecode/#downloads>`_ libraries. These
libraries are automatically installed during the setup.

The bindings will also use ``simplejson`` if you happen to have it
installed, but that is optional: we fall back to Python's built-in JSON
libraries is ``simplejson`` is not found.

Installation
------------

To install the latest stable release with
`pip <http://www.pip-installer.org/>`_::

    $ pip install bigmler

You can also install the development version of the bindings directly
from the Git repository::

    $ pip install -e git://github.com/bigmlcom/python.git#egg=bigml_python

Authentication
--------------

All the requests to BigML.io must be authenticated using your username
and `API key <https://bigml.com/account/apikey>`_ and are always
transmitted over HTTPS.

This module will look for your username and API key in the environment
variables ``BIGML_USERNAME`` and ``BIGML_API_KEY`` respectively. You can
add the following lines to your ``.bashrc`` or ``.bash_profile`` to set
those variables automatically when you log in::

    export BIGML_USERNAME=myusername
    export BIGML_API_KEY=ae579e7e53fb9abd646a6ff8aa99d4afe83ac291

Additional Information
----------------------

We've just barely scratched the surface. For additional information, see
the `full documentation for the Python
bindings on Read the Docs <http://bigml.readthedocs.org>`_.
Alternatively, the same documentation can be built from a local checkout
of the source by installing `Sphinx <http://sphinx.pocoo.org>`_
(``$ pip install sphinx``) and then running::

    $ cd docs
    $ make html

Then launch ``docs/_build/html/index.html`` in your browser.

How to Contribute
-----------------

Please follow the next steps:

  1. Fork the project on github.com.
  2. Create a new branch.
  3. Commit changes to the new branch.
  4. Send a `pull request <https://github.com/bigmlcom/bigmler/pulls>`_.


For details on the underlying API, see the
`BigML API documentation <https://bigml.com/developers>`_.
