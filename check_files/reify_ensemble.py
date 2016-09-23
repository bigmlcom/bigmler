from bigml.api import BigML
api = BigML()

source1 = api.create_source("iris.csv")
api.ok(source1)

dataset1 = api.create_dataset(source1, \
    {'name': u'iris dataset'})
api.ok(dataset1)

ensemble1 = api.create_ensemble(dataset1, \
    {'name': u'my_ensemble_name', 'seed': u'BigML'})
api.ok(ensemble1)
