#from tools import QdrantQueryTool
#from qdrant_client import QdrantClient

QDRANT_PORT=6333
QDRANT_HOST="localhost"
COLLECTION_NAME="gp_demo_dash"
VECTOR_NAME="fast-bge-small-en"

query = "список поставщиков"

#tool = QdrantQueryTool(QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME, VECTOR_NAME)
#tool.forward(query)

import pymorphy2

def pymorphy2_311_hotfix():
    from inspect import getfullargspec
    from pymorphy2.units.base import BaseAnalyzerUnit

    def _get_param_names_311(klass):
        if klass.__init__ is object.__init__:
            return []
        args = getfullargspec(klass.__init__).args
        return sorted(args[1:])

    setattr(BaseAnalyzerUnit, '_get_param_names', _get_param_names_311)


def lemmatize(text):
    pymorphy2_311_hotfix()
    morph = pymorphy2.MorphAnalyzer()
    words = text.lower().split()
    return [morph.parse(word)[0].normal_form for word in words]

ll = lemmatize("Какие нужно уплатить налоги с продажи квартиры?")
print(ll)