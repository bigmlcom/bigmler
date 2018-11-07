    from bigml.api import BigML
    api = BigML()
    source1_file = "iris_sp_chars.csv"
    args = \
        {u'fields': {u'000000': {u'name': u's\xe9pal.length', u'optype': u'numeric'},
                     u'000001': {u'name': u's\xe9pal&width', u'optype': u'numeric'},
                     u'000002': {u'name': u'p\xe9tal.length', u'optype': u'numeric'},
                     u'000003': {u'name': u'p\xe9tal&width\x00',
                                 u'optype': u'numeric'},
                     u'000004': {u'name': u'sp\xe9cies',
                                 u'optype': u'categorical',
                                 u'term_analysis': {u'enabled': True}}},
         }
    source2 = api.create_source(source1_file, args)
    api.ok(source2)
    