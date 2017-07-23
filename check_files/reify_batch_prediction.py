from bigml.api import BigML
api = BigML()

source1 = api.create_source("iris.csv")
api.ok(source1)

dataset1 = api.create_dataset(source1, \
    {'name': u'iris'})
api.ok(dataset1)

model1 = api.create_model(dataset1, \
    {'name': u'iris'})
api.ok(model1)

batchprediction1 = api.create_batch_prediction(model1, dataset1, \
    {'name': u'my_batch_prediction_name'})
api.ok(batchprediction1)
