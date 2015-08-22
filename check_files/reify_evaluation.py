from bigml.api import BigML
api = BigML()

source1 = api.create_source("iris.csv")
api.ok(source1)

dataset1 = api.create_dataset(source1)
api.ok(dataset1)

model1 = api.create_model(dataset1)
api.ok(model1)

evaluation1 = api.create_evaluation(model1, dataset1, {'name': u'my_evaluation_name'})
api.ok(evaluation1)
