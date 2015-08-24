from bigml.api import BigML
api = BigML()

source1 = api.create_source("iris.csv")
api.ok(source1)

dataset1 = api.create_dataset(source1)
api.ok(dataset1)

model1 = api.create_model(dataset1)
api.ok(model1)

prediction1 = api.create_prediction(model1, \
    {u'petal length': 0.5}, \
    {'name': u'my_prediction_name'})
api.ok(prediction1)
