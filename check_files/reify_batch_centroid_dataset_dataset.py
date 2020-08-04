    from bigml.api import BigML
api = BigML()
source1_file = "iris.csv"
args = \
{'fields': {'000000': {'name': 'sepal length', 'optype': 'numeric'},
'000001': {'name': 'sepal width', 'optype': 'numeric'},
'000002': {'name': 'petal length', 'optype': 'numeric'},
'000003': {'name': 'petal width', 'optype': 'numeric'},
'000004': {'name': 'species',
'optype': 'categorical',
'term_analysis': {'enabled': True}}}}
source2 = api.create_source(source1_file, args)
api.ok(source2)
args = \
{'objective_field': {'id': '000004'}}
dataset1 = api.create_dataset(source2, args)
api.ok(dataset1)
args = \
{'cluster_seed': 'bigml', 'critical_value': 5}
cluster1 = api.create_cluster(dataset1, args)
api.ok(cluster1)
args = \
{'output_dataset': True}
batchcentroid1 = api.create_batch_centroid(cluster1, dataset1, args)
api.ok(batchcentroid1)
dataset2 = api.get_dataset(batchcentroid1["object"]["output_dataset_resource"])
api.ok(dataset2)
args = \
{'fields': {'100000': {'name': 'cluster', 'preferred': True}},
'objective_field': {'id': '100000'}}
dataset3 = api.update_dataset(dataset2, args)
api.ok(dataset3)
args = \
{'all_fields': True,
'new_fields': [{'field': '( integer ( replace ( field "cluster" ) "Cluster " '
'"" ) )',
'names': ['Cluster']}],
'objective_field': {'id': '100000'}}
dataset4 = api.create_dataset(dataset3, args)
api.ok(dataset4)
