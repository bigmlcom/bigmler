    from bigml.api import BigML
    api = BigML()

    source1 = api.create_source("iris_sp_chars.csv", \
        {'name': 'my_sóurcè_sp_name'})
    api.ok(source1)

    source1 = api.update_source(source1, \
        {'fields': {'000000': {'name': 'sépal.length', 'optype': 'numeric'},
                    '000001': {'name': 'sépal&width', 'optype': 'numeric'},
                    '000002': {'name': 'pétal.length', 'optype': 'numeric'},
                    '000003': {'name': 'pétal&width\x00', 'optype': 'numeric'},
                    '000004': {'name': 'spécies', 'optype': 'categorical'}}})
    api.ok(source1)
