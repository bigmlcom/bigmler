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
        {u'input_data': {u'petal length': 0.5,
                         u'petal width': 0.5,
                         u'sepal length': 1,
                         u'sepal width': 1,
                         u'species': u'Iris-setosa'},
         }
    anomalyscore1 = api.create_anomalyscore(anomaly1, args)
    api.ok(anomalyscore1)
    