from bigml.api import BigML
api = BigML()
source1_file = "iris_sp_chars.csv"
args = \
{'fields': {'000000': {'name': 'sépal.length', 'optype': 'numeric'},
'000001': {'name': 'sépal&width', 'optype': 'numeric'},
'000002': {'name': 'pétal.length', 'optype': 'numeric'},
'000003': {'name': 'pétal&width\x00', 'optype': 'numeric'},
'000004': {'name': 'spécies',
'optype': 'categorical',
'term_analysis': {'enabled': True}}},
}
source2 = api.create_source(source1_file, args)
api.ok(source2)