import os

from elasticsearch import Elasticsearch
from elasticsearch import exceptions
from elasticsearch.helpers import scan, bulk

from gensim.models import Doc2Vec
from gensim.utils import simple_preprocess

from django.core.management.base import BaseCommand


def gen_data(documents, model, index, field):
    for doc in documents:
        _id = doc["_id"]
        text = doc["_source"]["content"]
        tokens = simple_preprocess(text)
        vector = model.infer_vector(tokens, epochs=5)
        doc = {"doc2vec": {f"{field}_vector": list(vector)}}

        yield dict(_op_type="update", _index=index, _id=_id, doc=doc)


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
        model_path = os.path.join(models_dir, f"blogs-content-field2vec.model")

        try:
            model = Doc2Vec.load(model_path)
        except FileNotFoundError as e:
            self.stdout.write(self.style.ERROR(f"Model does not exist. {e}"))
            return None

        try:
            updates, errors = bulk(es, gen_data(documents, model, index, field))
        except exceptions.NotFoundError as e:
            self.stdout.write(self.style.ERROR(f"Index does not exist. {e}"))
            return None

        self.stdout.write(self.style.SUCCESS(f"Successfully updated {updates} vectors for {index} - {field}. "
                                             f"errors: {errors}"))
