    from bigml.api import BigML
    api = BigML()

    source1 = api.create_source("iris.csv")
    api.ok(source1)

    dataset1 = api.create_dataset(source1, \
        {'name': 'iris'})
    api.ok(dataset1)

    dataset2 = api.create_dataset(dataset1, \
        {'name': 'iris', 'sample_rate': 0.7, 'seed': 'BigML'})
    api.ok(dataset2)

    dataset3 = api.create_dataset(dataset1, \
        {'name': 'iris', 'out_of_bag': True, 'sample_rate': 0.7, 'seed': 'BigML'})
    api.ok(dataset3)

    model1 = api.create_model(dataset2, \
        {'name': 'iris'})
    api.ok(model1)

    evaluation1 = api.create_evaluation(model1, dataset3, \
        {'name': 'my_evaluation_name'})
    api.ok(evaluation1)
