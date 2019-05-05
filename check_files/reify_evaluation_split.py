    from bigml.api import BigML
    api = BigML()
    source1_file = "iris.csv"
    args = \
        {u'fields': {u'000000': {u'name': u'sepal length', u'optype': u'numeric'},
                     u'000001': {u'name': u'sepal width', u'optype': u'numeric'},
                     u'000002': {u'name': u'petal length', u'optype': u'numeric'},
                     u'000003': {u'name': u'petal width', u'optype': u'numeric'},
                     u'000004': {u'name': u'species',
                                 u'optype': u'categorical',
                                 u'term_analysis': {u'enabled': True}}},
         }
    source2 = api.create_source(source1_file, args)
    api.ok(source2)

    args = \
        {u'objective_field': {u'id': u'000004'},
         }
    dataset1 = api.create_dataset(source2, args)
    api.ok(dataset1)

    args = \
        {u'objective_field': {u'id': u'000004'},
                  u'sample_rate': 0.7,
         u'seed': u'BigML'}
    dataset2 = api.create_dataset(dataset1, args)
    api.ok(dataset2)

    args = \
        {u'input_fields': [u'000000', u'000001', u'000002', u'000003', u'000004'],
         u'objective_field': {u'id': u'000004'},
         u'out_of_bag': True,
                  u'sample_rate': 0.7,
         u'seed': u'BigML'}
    dataset3 = api.create_dataset(dataset1, args)
    api.ok(dataset3)

    args = \
        {}
    model1 = api.create_model(dataset2, args)
    api.ok(model1)

    args = \
        {u'operating_kind': u'probability',
         }
    evaluation1 = api.create_evaluation(model1, dataset3, args)
    api.ok(evaluation1)
