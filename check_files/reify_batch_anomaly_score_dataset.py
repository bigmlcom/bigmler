from bigml.api import BigML
api = BigML()

source1 = api.create_source("iris.csv")
api.ok(source1)

dataset1 = api.create_dataset(source1)
api.ok(dataset1)

anomaly1 = api.create_anomaly(dataset1)
api.ok(anomaly1)

batchanomalyscore1 = api.create_batch_anomaly_score(anomaly1, dataset1, \
    {'output_dataset': True})
api.ok(batchanomalyscore1)

dataset2 = api.get_dataset(batchanomalyscore1['object']['output_dataset_resource'])
api.ok(dataset2)

dataset2 = api.update_dataset(dataset2, \
    {'fields': {u'000000': {'name': u'score'}},
     'name': u'my_dataset_from_batch_anomaly_score_name'})
api.ok(dataset2)
