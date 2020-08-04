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
'term_analysis': {'enabled': True}}},
}
source2 = api.create_source(source1_file, args)
api.ok(source2)
args = \
{'objective_field': {'id': '000004'},
}
dataset1 = api.create_dataset(source2, args)
api.ok(dataset1)
args = \
{'anomaly_seed': 'bigml',
'seed': 'bigml'}
anomaly1 = api.create_anomaly(dataset1, args)
api.ok(anomaly1)
args = \
{'input_data': {'petal length': 0.5,
'petal width': 0.5,
'sepal length': 1,
'sepal width': 1,
'species': 'Iris-setosa'},
}
anomalyscore1 = api.create_anomalyscore(anomaly1, args)
api.ok(anomalyscore1)