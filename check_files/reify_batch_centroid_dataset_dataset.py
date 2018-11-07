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
                                 u'term_analysis': {u'enabled': True}}}}
    source2 = api.create_source(source1_file, args)
    api.ok(source2)
    
    args = \
        {u'objective_field': {u'id': u'000004'}}
    dataset1 = api.create_dataset(source2, args)
    api.ok(dataset1)
    
    args = \
        {u'cluster_seed': u'2c249dda00fbf54ab4cdd850532a584f286af5b6',
         u'critical_value': 5}
    cluster1 = api.create_cluster(dataset1, args)
    api.ok(cluster1)
    
    args = \
        {u'fields_map': {u'000000': u'000000',
                         u'000001': u'000001',
                         u'000002': u'000002',
                         u'000003': u'000003',
                         u'000004': u'000004'},
         u'output_dataset': True}
    batchcentroid1 = api.create_batch_centroid(cluster1, dataset1, args)
    api.ok(batchcentroid1)
    
    dataset2 = api.get_dataset(batchcentroid1["object"]["output_dataset_resource"])
    api.ok(dataset2)
    
    args = \
        {u'fields': {u'100000': {u'name': u'cluster', u'preferred': True}},
         u'objective_field': {u'id': u'100000'}}
    dataset3 = api.update_dataset(dataset2, args)
    api.ok(dataset3)
    
    args = \
        {u'all_fields': False,
         u'new_fields': [{u'field': u'(all)', u'names': [u'cluster']},
                         {u'field': u'( integer ( replace ( field "cluster" ) "Cluster " "" ) )',
                          u'names': [u'Cluster']}],
         u'objective_field': {u'id': u'100000'}}
    dataset4 = api.create_dataset(dataset3, args)
    api.ok(dataset4)
    