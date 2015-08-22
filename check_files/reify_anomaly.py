from bigml.api import BigML
api = BigML()

source1 = api.create_source("iris.csv")
api.ok(source1)

dataset1 = api.create_dataset(source1)
api.ok(dataset1)

anomaly1 = api.create_anomaly(dataset1, {'name': u'my_anomaly_name'})
api.ok(anomaly1)
