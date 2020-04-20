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
         }
    dataset2 = api.create_dataset(source2, args)
    api.ok(dataset2)

    args = \
        {}
    dataset3 = api.create_dataset([dataset1,dataset2], args)
    api.ok(dataset3)

    args = \
        {u'objective_field': {u'id': u'000004'}}
    dataset4 = api.update_dataset(dataset3, args)
    api.ok(dataset4)
