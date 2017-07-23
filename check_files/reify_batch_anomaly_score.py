from bigml.api import BigML
api = BigML()

source1 = api.create_source("iris.csv")
api.ok(source1)

dataset1 = api.create_dataset(source1, \
    {'name': u'iris'})
api.ok(dataset1)

anomaly1 = api.create_anomaly(dataset1, \
    {'anomaly_seed': u'2c249dda00fbf54ab4cdd850532a584f286af5b6', 'name': u'iris'})
api.ok(anomaly1)

batchanomalyscore1 = api.create_batch_anomaly_score(anomaly1, dataset1, \
    {'name': u'my_batch_anomaly_score_name'})
api.ok(batchanomalyscore1)
