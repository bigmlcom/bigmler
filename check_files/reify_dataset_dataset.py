from bigml.api import BigML
api = BigML()

source1 = api.create_source("iris.csv")
api.ok(source1)

dataset1 = api.create_dataset(source1, \
    {'name': u'iris dataset'})
api.ok(dataset1)

dataset2 = api.create_dataset(dataset1, \
    {'all_but': [u'000001'],
     'all_fields': False,
     'name': u'my_dataset_from_dataset_name',
     'new_fields': [{u'description': u'',
                     'field': u'2',
                     u'label': u'',
                     u'name': u'new'}]})
api.ok(dataset2)
