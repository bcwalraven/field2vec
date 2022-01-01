
# field2vec

Video Demo:
<br>
Purpose: Provide a way to quickly train and ingest document vectors for text fields in an elasticsearch and provide an endpoint for adding vectors
to any new documents.

## Description:

 Document vectors can provide additional context for text comparison when compared with bag of word approaches such as 
 TFiDF or BM25. Field2vec leverages the elasticsearch python client library and gensim nlp library to quickly train a Doc2Vec model on 
 existing text fields in an elasticsearch index and update documents with the vectors. It also uses django to provide an HTTP server
 that can be used the the http logstash filter plug-in to update any new indexed documents with document vectors. Python generators are used so that memory will
 not be a constraint even for very large indexes.  
 
## Commands:

`python manage.py build_model <index> <field>`

This will use the elasticsearch client to pull all documents in the specified index where the target field exists and
train a gensim doc2vec model. This model is saved in a folder structure doc2vec -> \<index> -> \<field> where it can be loaded to generate vectors.

<br>

 `python manage.py update_vectors <index> <field>`
 
 This will use the elasticsearch client to pull all documents in the specified index where the target field exists and
use a pre-trained doc2vec model to generate document vectors. The documents are then updated with the elasticsearch client bulk helper
with a new field doc2vec with will contain the vector for the target field.

<br>
To use the http endpoint to generate vectors from a pre-trained model use the /add_vector/ and point and provide the index name, target field name, 
and target field in the body. An example logstash filter plug-in sequence is included under other in the django app.

 
 ## References
 
 https://docs.djangoproject.com/en/4.0/
 <br>
 https://elasticsearch-py.readthedocs.io/en/v7.16.2/
 <br>
 https://radimrehurek.com/gensim/models/doc2vec.html
 <br>
 https://dev.to/v_it_aly/python-tips-how-to-reuse-a-generator-within-one-function-a5o