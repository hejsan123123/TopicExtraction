import gensim, os, bz2, inspect
from gensim import corpora, models, similarities
import logging


def iter_documents(top_directory):
    """Iterate over all documents, yielding a document (=list of utf8 tokens) at a time."""
    for root, dirs, files in os.walk(top_directory):
        for file in filter(lambda file: file.endswith('.txt'), files):
            document = open(os.path.join(root, file)).read() # read the entire document, as one big string
            yield gensim.utils.tokenize(document, lower=True) # or whatever tokenization suits you

class MyCorpus(object):
    def __init__(self, top_dir):
        self.top_dir = top_dir
        self.dictionary = gensim.corpora.Dictionary(iter_documents(top_dir))
        self.dictionary.filter_extremes(no_below=1, keep_n=30000) # check API docs for pruning params
        self.dictionary.save('/tmp/deerwester.dict')

    def __iter__(self):
        for tokens in iter_documents(self.top_dir):
            yield self.dictionary.doc2bow(tokens)

def main():
    top_directory = '/Users/jonathanklemetz/Desktop/Lemmatized'
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    corpus = MyCorpus(top_directory) #Creates a MyCorpus object, containing all the documents
    dictionary = corpora.Dictionary.load('/tmp/deerwester.dict')

    # Not entierly sure what this is doing, but it was necessary to create a proper corpus object.
    # I think this is because that gensims algorithms require to have the corpuses stored on the hard drive.
    corpora.MmCorpus.serialize('/tmp/corpus.mm', corpus)
    corpus = corpora.MmCorpus('/tmp/corpus.mm')
    print(corpus)

    #lda = gensim.models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=5, passes=10)
    lda = gensim.models.ldamulticore.LdaMulticore(corpus=corpus, id2word=dictionary, num_topics=200, passes=5, batch=True, workers=2, chunksize=3000, iterations=100)
    #lda.log_perplexity(chunk=chunksize, total_docs=2163)
    lda.print_topics(10, num_words=10)

    document = corpus[0]


#for document in corpus:
#printTopic = lda.get_document_topics(document, minimum_probability=None)
#print(printTopic)        
#print(document[1])


main()