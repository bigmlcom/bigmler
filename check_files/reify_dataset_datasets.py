from bigml.api import BigML
api = BigML()

source1 = api.create_source("iris.csv")
api.ok(source1)

dataset1 = api.create_dataset(source1, \
    {'name': u'iris'})
api.ok(dataset1)

dataset2 = api.create_dataset(source1, \
    {'name': u'iris'})
api.ok(dataset2)

dataset3 = api.create_dataset(['dataset2', 'dataset1'], \
    {'name': u'my_dataset_name'})
api.ok(dataset3)
