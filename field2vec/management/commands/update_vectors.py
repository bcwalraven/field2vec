import os

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan, bulk

from gensim.models import Doc2Vec
from gensim.utils import simple_preprocess

from django.core.management.base import BaseCommand, CommandError


def gen_data(documents, model, index, field):
    for doc in documents:
        _id = doc["_id"]
        text = doc["_source"]["content"]
        tokens = simple_preprocess(text)
        vector = model.infer_vector(tokens, epochs=5)

        yield dict(_op_type="update", _index=index, _id=_id, doc={f"{field}_vector": list(vector)})


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('index', nargs=1, type=str)
        parser.add_argument('field', nargs=1, type=str)

    def handle(self, *args, **options):
        index, field = options["index"][0], options["field"][0]

        es = Elasticsearch()
        query = {"query": {"exists": {"field": field}}}
        documents = scan(es, query=query, index=index)

        models_dir = os.path.join(__file__, os.path.pardir, os.path.pardir, os.path.pardir, "doc2vec", index, field)
        models_dir = os.path.abspath(models_dir)
        model_path = os.path.join(models_dir, f"{index}-{field}-field2vec.model")

        model = Doc2Vec.load(model_path)

        response = bulk(es, gen_data(documents, model, index, field))
        print(response)

        self.stdout.write(self.style.SUCCESS(f"Successfully updated vectors for {index} - {field}"))
