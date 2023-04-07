import pickle

from langdetect import detect


class SpamFilter:
    def __init__(self, **kwargs):
        # load model and vectorizer
        with open(
            "coreplus/spams/static/model_and_vectorizer_with_pickle(en).pkl", "rb"
        ) as f:
            vectorizer_en, model_en = pickle.load(f)
        self.vectorizer_en = vectorizer_en
        self.model_en = model_en
        with open(
            "coreplus/spams/static/model_and_vectorizer_with_pickle(id).pkl", "rb"
        ) as f:
            vectorizer_id, model_id = pickle.load(f)
        self.vectorizer_id = vectorizer_id
        self.model_id = model_id

    def is_spam(self, text):
        lang = detect(text)
        if lang == "en":
            text_vector = self.vectorizer_en.transform([text])
            res = self.model_en.predict(text_vector)
        else:
            text_vector = self.vectorizer_id.transform([text])
            res = self.model_id.predict(text_vector)
        # return 1 = spam, 0 = normal
        return res[0]
