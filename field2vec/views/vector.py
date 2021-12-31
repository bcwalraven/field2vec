import os
import json

from gensim.models import Doc2Vec
from gensim.utils import simple_preprocess

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def add_vector(request):
    body = json.loads(request.body.decode('utf-8'))

    index = body.get("index")
    field_name = body.get("field_name")
    field = body.get("field")

    models_dir = os.path.join(__file__, os.path.pardir, os.path.pardir, "doc2vec", index, field_name)
    models_dir = os.path.abspath(models_dir)
    model_path = os.path.join(models_dir, f"{index}-{field_name}-field2vec.model")

    model = Doc2Vec.load(model_path)

    tokens = simple_preprocess(field)
    vector = list(model.infer_vector(tokens, epochs=5))
    vector = json.dumps([str(v) for v in vector])

    return JsonResponse(vector, safe=False)
