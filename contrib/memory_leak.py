# Notes on debugging memory leaks in the worker

# apt-get update && apt-get install graphviz
# pip install objgraph

import objgraph
import gc
import random
from aleph.logic.documents import process_documents
objgraph.show_most_common_types()

process_documents(21)
# objgraph.show_most_common_types()

objgraph.show_chain(objgraph.find_backref_chain(random.choice(objgraph.by_type('_DebugQueryTuple')), objgraph.is_proper_module), filename='chain.png')  # noqa
gc.collect()
