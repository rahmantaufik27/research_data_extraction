import requests
import re
import string
import nltk
from nltk.tokenize import word_tokenize
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

try:
    nltk.data.find('tokenizers/punkt')
    nltk.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# PREPROCESSING

class Preprocessing:
    def clean_text(self, texts):
        # text lower case
        texts = str(texts)
        text_clean = texts.lower()
        # get only alphabet text
        text_clean = re.sub("[^0-9a-z]+", " ", text_clean)

        return text_clean

    def tokenize_text(self, texts):
        all_sentences = nltk.sent_tokenize(texts)
        all_words = [nltk.word_tokenize(sent) for sent in all_sentences]
        return all_words

    # def remove_wordstop(self, words):
    #     # stopword dari tala, sastrawi dan spacy id
    #     sw1_raw = pd.read_csv(
    #         "dataset/stopwords_combination.txt",
    #         lineterminator="\n",
    #         names=["stopword"],
    #         header=None,
    #     )
    #     sw1 = sw1_raw["stopword"].values.tolist()
    #     # stopword custom
    #     sw4_raw = pd.read_csv(
    #         "dataset/stopwords_apotek_custom.txt",
    #         lineterminator="\n",
    #         names=["stopword"],
    #         header=None,
    #     )
    #     sw4 = sw4_raw["stopword"].values.tolist()
    #     # stopword gabungan indonesia
    #     sw_raw = sw1 + sw4
    #     # hapus duplikat values di list
    #     sw = list(dict.fromkeys(sw_raw))
    #     # stopword gabungan indonesia inggris
    #     stopwords_list = nltk.corpus.stopwords.words("english")
    #     stopwords_list.extend(sw)

    #     for i in range(len(words)):
    #         words[i] = [w for w in words[i] if w not in stopwords_list]
    #     return words

    # def stemming_text(self, words):
    #     factory = StemmerFactory()
    #     stemmer = factory.create_stemmer()
    #     stem_text = stemmer.stem(words)
    #     return stem_text

    # def pre_process(self, docs):
    #     text_processed = str(docs)
    #     text_processed = self.clean_text(text_processed)
    #     text_processed = self.stemming_text(text_processed)
    #     text_processed = self.tokenize_text(text_processed)
    #     text_processed = self.remove_wordstop(text_processed)
    #     text_processed = text_processed[0]
    #     return text_processed
