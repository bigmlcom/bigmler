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
{'all_fields': False,
'new_fields': [{'field': '(all-but "000001")',
'names': ['sepal length',
'petal length',
'petal width',
'species']},
{'field': '2', 'names': ['new']}],
'objective_field': {'id': '000004'},
}
dataset2 = api.create_dataset(dataset1, args)
api.ok(dataset2)