from bigml.api import BigML
api = BigML()

source1 = api.create_source("iris_sp_chars.csv", {'name': u'my_s\xf3urc\xe8_sp_name'})
api.ok(source1)

source1 = api.update_source(source1, {'fields': {u'000004': {'optype': u'categorical', 'name': u'sp\xe9cies'}, u'000002': {'optype': u'numeric', 'name': u'p\xe9tal.length'}, u'000003': {'optype': u'numeric', 'name': u'p\xe9tal&width\x00'}, u'000000': {'optype': u'numeric', 'name': u's\xe9pal.length'}, u'000001': {'optype': u'numeric', 'name': u's\xe9pal&width'}}})
api.ok(source1)
