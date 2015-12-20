    from bigml.api import BigML
    api = BigML()

    source1 = api.create_source("iris.csv")
    api.ok(source1)

    dataset1 = api.create_dataset(source1)
    api.ok(dataset1)

    dataset2 = api.create_dataset(dataset1, \
        {'all_but': ['000001'],
         'all_fields': False,
         'input_fields': ['000000', '000001', '000002', '000003', '000004'],
         'name': 'my_dataset_from_dataset_name',
         'new_fields': [{'description': '', 'field': '2', 'label': '', 'name': 'new'}],
         'objective_field': {'id': '100004'}})
    api.ok(dataset2)
