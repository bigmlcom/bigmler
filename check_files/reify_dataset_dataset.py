from bigml.api import BigML
api = BigML()

source1 = api.create_source("iris.csv")
api.ok(source1)

dataset1 = api.create_dataset(source1)
api.ok(dataset1)

dataset2 = api.create_dataset(dataset1, \
    {'all_but': [u'000001'],
     'all_fields': False,
     'input_fields': [u'000000', u'000001', u'000002', u'000003', u'000004'],
     'name': u'my_dataset_from_dataset_name',
     'new_fields': [{u'description': u'',
                     'field': u'2',
                     u'label': u'',
                     u'name': u'new'}],
     'objective_field': {'id': u'100004'}})
api.ok(dataset2)
