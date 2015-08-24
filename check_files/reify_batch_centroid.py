from bigml.api import BigML
api = BigML()

source1 = api.create_source("iris.csv")
api.ok(source1)

dataset1 = api.create_dataset(source1)
api.ok(dataset1)

cluster1 = api.create_cluster(dataset1)
api.ok(cluster1)

batchcentroid1 = api.create_batch_centroid(cluster1, dataset1, \
    {'name': u'my_batch_centroid_name'})
api.ok(batchcentroid1)
