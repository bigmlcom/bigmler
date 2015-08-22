from bigml.api import BigML
api = BigML()

source1 = api.create_source("iris.csv", {'name': u'my_source_name'})
api.ok(source1)
