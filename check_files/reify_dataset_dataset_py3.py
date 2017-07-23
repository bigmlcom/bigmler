    from bigml.api import BigML
    api = BigML()

    source1 = api.create_source("iris.csv")
    api.ok(source1)

    dataset1 = api.create_dataset(source1, \
        {'name': 'iris'})
    api.ok(dataset1)

    dataset2 = api.create_dataset(dataset1, \
        {'all_but': ['000001'],
         'all_fields': False,
         'name': 'my_dataset_from_dataset_name',
         'new_fields': [{'description': '', 'field': '2', 'label': '', 'name': 'new'}]})
    api.ok(dataset2)
