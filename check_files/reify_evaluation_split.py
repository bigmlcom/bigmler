from bigml.api import BigML
api = BigML()

source1 = api.create_source("iris.csv")
api.ok(source1)

dataset1 = api.create_dataset(source1)
api.ok(dataset1)

dataset2 = api.create_dataset(dataset1, \
    {'name': u"iris' dataset - sample (70.00%)", 'sample_rate': 0.7})
api.ok(dataset2)

dataset3 = api.create_dataset(dataset1, \
    {'name': u"iris' dataset - sample (30.00%)",
     'out_of_bag': True,
     'sample_rate': 0.7})
api.ok(dataset3)

model1 = api.create_model(dataset2)
api.ok(model1)

evaluation1 = api.create_evaluation(model1, dataset3, \
    {'name': u'my_evaluation_name'})
api.ok(evaluation1)
