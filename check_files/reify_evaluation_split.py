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
{'objective_field': {'id': '000004'},
'sample_rate': 0.7,
'seed': 'BigML'}
dataset2 = api.create_dataset(dataset1, args)
api.ok(dataset2)
args = \
{'objective_field': {'id': '000004'},
'out_of_bag': True,
'sample_rate': 0.7,
'seed': 'BigML'}
dataset3 = api.create_dataset(dataset1, args)
api.ok(dataset3)
args = \
{}
model1 = api.create_model(dataset2, args)
api.ok(model1)
args = \
{'operating_kind': 'probability', }
evaluation1 = api.create_evaluation(model1, dataset3, args)
api.ok(evaluation1)
