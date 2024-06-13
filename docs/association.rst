.. toctree::
   :maxdepth: 2
   :hidden:


.. _bigmler-association:

Association subcommand
======================

Association Discovery is a popular method to find out relations among values
in high-dimensional datasets.

A common case where association discovery is often used is
market basket analysis. This analysis seeks for customer shopping
patterns across large transactional
datasets. For instance, do customers who buy hamburgers and ketchup also
consume bread?

Businesses use those insights to make decisions on promotions and product
placements.
Association Discovery can also be used for other purposes such as early
incident detection, web usage analysis, or software intrusion detection.

In BigML, the Association resource object can be built from any dataset, and
its results are a list of association rules between the items in the dataset.
In the example case, the corresponding
association rule would have hamburguers and ketchup as the items at the
left hand side of the association rule and bread would be the item at the
right hand side. Both sides in this association rule are related,
in the sense that observing
the items in the left hand side implies observing the items in the right hand
side. There are some metrics to ponder the quality of these association rules:

- Support: the proportion of instances which contain an itemset.

For an association rule, it means the number of instances in the dataset which
contain the rule's antecedent and rule's consequent together
over the total number of instances (N) in the dataset.

It gives a measure of the importance of the rule. Association rules have
to satisfy a minimum support constraint (i.e., min_support).

- Coverage: the support of the antedecent of an association rule.
  It measures how often a rule can be applied.

- Confidence or (strength): The probability of seeing the rule's consequent
  under the condition that the instances also contain the rule's antecedent.
  Confidence is computed using the support of the association rule over the
  coverage. That is, the percentage of instances which contain the consequent
  and antecedent together over the number of instances which only contain
  the antecedent.

Confidence is directed and gives different values for the association
rules Antecedent → Consequent and Consequent → Antecedent. Association
rules also need to satisfy a minimum confidence constraint
(i.e., min_confidence).

- Leverage: the difference of the support of the association
  rule (i.e., the antecedent and consequent appearing together) and what would
  be expected if antecedent and consequent where statistically independent.
  This is a value between -1 and 1. A positive value suggests a positive
  relationship and a negative value suggests a negative relationship.
  0 indicates independence.

Lift: how many times more often antecedent and consequent occur together
than expected if they where statistically independent.
A value of 1 suggests that there is no relationship between the antecedent
and the consequent. Higher values suggest stronger positive relationships.
Lower values suggest stronger negative relationships (the presence of the
antecedent reduces the likelihood of the consequent)

As to the items used in association rules, each type of field is parsed to
extract items for the rules as follows:

- Categorical: each different value (class) will be considered a separate item.
- Text: each unique term will be considered a separate item.
- Items: each different item in the items summary will be considered.
- Numeric: Values will be converted into categorical by making a
  segmentation of the values.

For example, a numeric field with values ranging from 0 to 600 split
into 3 segments:
segment 1 → [0, 200), segment 2 → [200, 400), segment 3 → [400, 600].
You can refine the behavior of the transformation using
`discretization <https://bigml.com/api/associations#ad_create_discretization>`_
and `field_discretizations <https://bigml.com/api/associations#ad_create_field_discretizations>`_.


The ``bigmler association`` subcommand will discover the association
rules present in your
datasets. Starting from the raw data in your files:

.. code-block:: bash

    bigmler association --train my_file.csv

will generate the ``source``, ``dataset`` and ``association`` objects
required to present the association rules hidden in your data. You can also
limit the number of rules extracted using the ``--max-k`` option


.. code-block:: bash

    bigmler association --dataset dataset/532db2b637203f3f1a000103 \
                        --max-k 20

With the prior command only 20 association rules will be extracted. Similarly,
you can change the search strategy used to find them


.. code-block:: bash

    bigmler association --dataset dataset/532db2b637203f3f1a000103 \
                        --search-strategy confidence

In this case, the ``confidence`` is used (the default value being
``leverage``).


Association Specific Subcommand Options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

===================================== =========================================
``--association-attributes``          Path to a JSON file containing
                                      attributes (any of the updatable
                                      attributes described in the
                                      `developers section <https://bigml.com/api/associations#ad_association_properties>`_ )
                                      for the association
``--max-k`` K                         Maximum number of rules to be found
``--search-strategy`` STRATEGY        Strategy used when searching for the
                                      associations. The possible values are:
                                      confidence, coverage, leverage, lift,
                                      support
===================================== =========================================
