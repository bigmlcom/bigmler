from bigml.api import BigML
api = BigML()

source1 = api.create_source("iris.csv")
api.ok(source1)

dataset1 = api.create_dataset(source1, \
    {'name': u'iris dataset'})
api.ok(dataset1)

anomaly1 = api.create_anomaly(dataset1, \
    {'anomaly_seed': u'2c249dda00fbf54ab4cdd850532a584f286af5b6',
     'name': u"iris dataset's anomaly detector"})
api.ok(anomaly1)

anomalyscore1 = api.create_anomaly_score(anomaly1, \
    {u'petal length': 0.5,
     u'petal width': 0.5,
     u'sepal length': 1,
     u'sepal width': 1,
     u'species': u'Iris-setosa'}, \
    {'name': u'my_anomaly_score_name'})
api.ok(anomalyscore1)
