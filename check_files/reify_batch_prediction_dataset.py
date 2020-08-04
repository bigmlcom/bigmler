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
model1 = api.create_model(dataset1)
api.ok(model1)
args = \
{'operating_kind': 'probability', 'output_dataset': True}
batchprediction1 = api.create_batch_prediction(model1, dataset1, args)
api.ok(batchprediction1)
dataset2 = api.get_dataset(batchprediction1["object"]["output_dataset_resource"])
api.ok(dataset2)
args = \
{'fields': {'100000': {'name': 'species', 'preferred': True}},
'objective_field': {'id': '100000'}}
dataset3 = api.update_dataset(dataset2, args)
api.ok(dataset3)