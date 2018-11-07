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
        {u'cluster_seed': u'2c249dda00fbf54ab4cdd850532a584f286af5b6',
         u'critical_value': 5,
         }
    cluster1 = api.create_cluster(dataset1, args)
    api.ok(cluster1)
    
    args = \
        {u'input_data': {u'petal length': 0.5,
                         u'petal width': 0.5,
                         u'sepal length': 1,
                         u'sepal width': 1,
                         u'species': u'Iris-setosa'},
         }
    centroid1 = api.create_centroid(cluster1, args)
    api.ok(centroid1)
    