from bigml.api import BigML
api = BigML()

source1 = api.create_source("iris_sp_chars.csv", \
    {'name': u'my_s\xf3urc\xe8_sp_name'})
api.ok(source1)

source1 = api.update_source(source1, \
    {'fields': {u'000000': {'name': u's\xe9pal.length', 'optype': u'numeric'},
                u'000001': {'name': u's\xe9pal&width', 'optype': u'numeric'},
                u'000002': {'name': u'p\xe9tal.length', 'optype': u'numeric'},
                u'000003': {'name': u'p\xe9tal&width\x00', 'optype': u'numeric'},
                u'000004': {'name': u'sp\xe9cies', 'optype': u'categorical'}}})
api.ok(source1)
