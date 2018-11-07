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
        {u'anomaly_seed': u'bigml',
                  u'seed': u'bigml'}
    anomaly1 = api.create_anomaly(dataset1, args)
    api.ok(anomaly1)
    
    args = \
        {u'fields_map': {u'000000': u'000000',
                         u'000001': u'000001',
                         u'000002': u'000002',
                         u'000003': u'000003',
                         u'000004': u'000004'},
         }
    batchanomalyscore1 = api.create_batch_anomaly_score(anomaly1, dataset1, args)
    api.ok(batchanomalyscore1)
    