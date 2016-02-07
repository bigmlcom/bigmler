from bigml.api import BigML
api = BigML()

source1 = api.create_source("iris.csv")
api.ok(source1)

dataset1 = api.create_dataset(source1, \
    {'name': u'iris dataset'})
api.ok(dataset1)

cluster1 = api.create_cluster(dataset1, \
    {'name': u'my_cluster_name'})
api.ok(cluster1)
