.. toctree::
   :maxdepth: 2
   :hidden:


.. _bigmler-source:

Source subcommand
=================

The ``bigmler source`` subcommand can be used to create sources from data files
either with or without images. Regular CSV files will generate a ``Source``
resource in BigML whereas collections of images will generate ``composite
sources``.

Composite Sources
-----------------

A Composite Source is an arbitrary collection of other BigML Sources.
The Sources in a composite are called components.
When all the components have the same fields,
the composite itself will inherit those fields, and you will be able to
create a dataset from it: the result will just be the concatenation of all
the rows extracted from each component source inside the composite.

You could put together a list of CSV sources, or maybe a couple of CSV files
and an ARFF file with the same exact fields, and the resulting composite
will inherit those fields and behave like a single source for all practical
purposes.

As any other source, a (possibly empty) composite is created open, meaning
that you can modify it. In the case of composites, modifying it means
performing one of the following operations:

- Adding components

.. code-block:: bash

    bigmler source --source source/4f603fe203ce89bb2d000000 \
                   --add-sources source/4f603fe203ce89bb2d000001,source/4f603fe203ce89bb2d000002 \
                   --output-dir final-composite

- Removing components

.. code-block:: bash

    bigmler source --source source/4f603fe203ce89bb2d000000 \
                   --remove-sources source/4f603fe203ce89bb2d000001,source/4f603fe203ce89bb2d000002 \
                   --output-dir final-composite

- Replacing the full list of components

.. code-block:: bash

    bigmler source --source source/4f603fe203ce89bb2d000000 \
                   --replace-sources source/4f603fe203ce89bb2d000001,source/4f603fe203ce89bb2d000002 \
                   --output-dir final-composite

A source can belong to as many composites as you wish,
and composites can be nested, with the only limitation that a composite
can only be a component if it's closed (non-editable).

When a source belongs to one or more composites, it cannot be modified,
regardless of whether it's open or closed. That way all composites see the same
version of the source all the time.

As you add or remove components to a composite, it will check the
compatibility of the fields of all its components, and update its own set
of fields. Thus, adding and removing sources to a composite is in this sense
analogous to changing the parsing specification of, say, a CSV, in the sense
that that is also an operation that can potentially change the collection
of fields (and even the number of rows) extracted to the CSV.

Once you have finished adding components to a composite and want to use it
to create datasets, you must close it. When you close a composite, all its
components will be automatically closed for you.

Unlike all other kinds of source, composites created this way must be
explicitly closed by an API call or UI action in order to create a dataset.
That is mainly to avoid accidentally closing a composite that is being worked
on by several collaborators, or by mistake. Since composites can have a huge
number of components and closing them also closes all of them, it may be
relatively slow.

As an alternative to combining pre-existing sources into a composite,
one can also upload a zip or tar file containing more than one file.
BigML will then automatically create one source for each file inside
the archive, and put them all together in a composite source.

Image Feature Extraction
------------------------

BigML provides configurable Image Analysis extraction capabilities for
Composites built on images. The Composite configuration options include
automatically computing as new features the dimensions, average pixels,
level histogram, histogram of gradients, wavelet subbands and even using
features derived from pre-trained CNNs. For more detail, you can check
the `Image Analysis <https://bigml.com/api/sources?id=image-analysis>`_
API documentation for composites.

All these options are in turn configurable when creating sources using BigMLer.

.. code-block:: bash

    bigmler source --data cats.zip --dimensions --HOG \
                   --pretrained-cnn mobilenet \
                   --output-dir final-composite

Thanks to those new features, all kind of models (not only Deepnets) can
be built taking advantage of the images information. To learn the options
available for image extraction configuration,
see :ref:image-feature-extraction .

Annotated images as Composite Sources
-------------------------------------

BigML allows to use images too to build your Machine Learning models.
In order to use images in BigML, each image file needs to be uploaded and
transformed in a Source object, and the collection of images that will become
your training data is handled in BigML as a collection of Sources. However,
this collection of sources is in turn a Source (to be precise, a
``Composite Source``). Each row in a Composite Source can contain one or more
images, but it can also contain other fields related to those images,
like labels, used in classification, or regions, used in object detection.

When storing images in a repository, is common practice to keep them
in directories or compressed files. The related fields, like labels or regions,
are usually stored as additional files where some attribute points to the image
they refer to. In BigML Composite Sources, though,
images and annotations can be consolidated as different fields
of the composite source, so that every row of data in the composite source
contains the source created by uploading the related image plus the
annotation fields associated to it.

As there's not a single standard procedure to create and store these image and
annotation files, BigMLer tries to give options that encompass most of
the usual scenarios. We'll see some examples using the specific
``bigmler source`` subcommand.

First scenario: We only need to upload images and they are already stored
in a single compressed file.

.. code-block:: bash

    bigmler source --train my_images.zip --output-dir output

In this case, the ``my_images.zip`` is uploaded and a new ``composite source``
is created containing the images.

Second scenario: Images are stored in a directory.

.. code-block:: bash

    bigmler source --train ./my_images_directory --output-dir output

The BigMLer command creates a local compressed file that contains the
images stored in the directory given as a ``--train`` option. The compressed
file is stored in the ``output`` directory and then is uploaded to BigML,
resulting in a ``composite source``.

Third scenario: The images are stored in a directory and they have associated
annotations which have been stored in an annotations JSON file.

.. code-block:: bash

    bigmler source --train ./my_images_directory \
                   --annotations-file annotations.json \
                   --output-dir output

BigML uses a BigML-COCO syntax to provide labels associated to
images. The annotations file should contain a list of dictionaries and
each dictionary corresponds to one of the images. The reference to the
annotated image is provided in the ``file`` attribute.

.. code-block:: JSON

    [{"file": "my_images/image1.jpg",
      "label": "label1"}.
     {"file": "my_images/image2.jpg",
      "label": "label1"},
     {"file": "my_images/image3.jpg",
      "label": "label2"}]

In this case, the previous ``bigmler source`` command will zip the images
contained in the ``my_images_directory``, upload them and create the
corresponding composite source, and finally add a new field named ``label``
to the composite source where the labels provided in the ``annotations.json``
file will be updated.

These are the basic scenarios, but other annotations syntaxes, like ``VOC``,
``YOLO`` or ``COCO`` files are also accepted.
As for the first two the annotations are
provided separately, in one file per image, you would need to
provide the directory where these files are stored and
the annotations language as options:

.. code-block:: bash

    bigmler source --train ./my_images_directory \
                   --annotations-dir ./annotations_directory \
                   --annotations-language VOC
                   --output-dir output

Each annotation file can contain some ``folder`` attribute.
That will be interpreted as a subfolder information that will be
added to the given ``--train`` path on a per image basis.

On the contrary, ``COCO`` annotations are provided in a single file.
In that case, you can point to the file using the ``--annotations-file``
option.

.. code-block:: bash

    bigmler source --train ./my_images_directory \
                   --annotations-file ./my_coco_annotations.json \
                   --annotations-language COCO
                   --output-dir output

The created composite sources are editable up until you close them
explicitly or you create a dataset from them. While editable, more annotations
can be added to an existing source. For instance, to add annotations
to the source generated in the third scenario,
``source/61373ea6520f903f48000001``, we could use:

.. code-block:: bash

    bigmler source --source source/61373ea6520f903f48000001 \
                   --images-file my_images.zip \
                   --annotations-file new_annotations.json \
                   --output-dir output


Source subcommand Options
^^^^^^^^^^^^^^^^^^^^^^^^^

===================================== =========================================
``--data`` *PATH*                     Path to the data file or directory (if
                                      more than one file should be uploaded)
``--images-file`` *PATH*              Path to a compressed file that contains
                                      images
``--annotations-file`` *PATH*         Path to the file that contains the
                                      annotations for images
``--annotations-dir`` *DIRECTORY*     Path to a directory that contains
                                      annotation files, one per image
``--annotations-language`` *LANGUAGE* Language that sets the syntax of
                                      the annotations. Options: VOC or YOLO
``--source`` *SOURCE ID*              Id for the source that will be updated
``--source-in`` *PATH*                Path to the file that contains source Ids
                                      (one per line) and uses the last one
                                      as source ID for updates
``--sources-in`` *PATH*               Path to the file that contains source Ids
                                      (one per line) and uses them all as the
                                      list of sources to create composite
                                      sources
``--close``                           Causes a source to be closed for editing
``--open``                            If the source is closed, clones the
                                      source into a new one open for editing
``--add-sources`` *STRING*            Adds a comma-separater list of sources to
                                      a composite source
``--delete-sources`` *STRING*         Deletes a comma-separated list of sources
                                      from the composite source and also
                                      individually
                                      if they don't belong to another
                                      composite
``--remove-sources`` *STRING*         Deletes a comma-separated list of sources
                                      from the
                                      composite source keeping them as
                                      individual sources
``--rows-values-json`` *PATH*         Path to a JSON file that contains the
                                      values for some rows and fields
``--rows-indices`` *STRING*           Comma-separated list of indices of
                                      the rows that will be affected by the
                                      ``--rows-values-json`` option
``--rows-components`` *STRING*        Comma-separated list of source Ids
                                      that will be affected by the
                                      ``--rows-values-json`` option
===================================== =========================================



Image Analysis Specific Options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

===================================== =========================================
``--no-image-analysis``               Disables the Image Feature Extraction
                                      (only Deepnets will be able to use images
                                      information)
``--dimensions``                      Enables Image dimensions extraction
``--average-pixels``                  Enables Image average pixels extraction
``--level-histogram``                 Enables color level histogram extraction
``--HOG``                             Enables histogram of gradients extraction
``--ws-level``                        Enables wavelet subbands extraction and
                                      sets the number of iterations.
``--pretrained-cnn``                  Enables extraction of particular
                                      pretrained CNN features. The available
                                      options for CNNs are: mobilenet,
                                      mobilenetv2 and resnet18
===================================== =========================================
