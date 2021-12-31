import os

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

from gensim.models.doc2vec import TaggedDocument
from gensim.models import Doc2Vec
from gensim.utils import simple_preprocess

from django.core.management.base import BaseCommand, CommandError


class DocumentIterator:
    def __init__(self, documents, field):
        self.documents = documents
        self.field = field

    def __iter__(self):
        for i, doc in enumerate(self.documents):
            text = doc["_source"][self.field]
            tokens = simple_preprocess(text)
            yield TaggedDocument(tokens, [i])


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('index', nargs=1, type=str)
        parser.add_argument('field', nargs=1, type=str)

    def handle(self, *args, **options):
        index, field = options["index"][0], options["field"][0]

        es = Elasticsearch()
        query = {"query": {"exists": {"field": field}}}
        documents = scan(es, query=query, index=index)

        model = Doc2Vec(
            DocumentIterator(documents, field),
            vector_size=10,
            window=5,
            workers=1)

        models_dir = os.path.join(__file__, os.path.pardir, os.path.pardir, os.path.pardir, "doc2vec", index, field)
        models_dir = os.path.abspath(models_dir)
        model_path = os.path.join(models_dir, f"{index}-{field}-field2vec.model")

        if not os.path.exists(models_dir):
            os.makedirs(models_dir)

        model.save(model_path)

        self.stdout.write(self.style.SUCCESS(f"Successfully built vector model for {index} - {field}"))
