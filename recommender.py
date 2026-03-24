import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MovieRecommender:
    def __init__(self, path):
        self.df = pd.read_csv(path)
        self.prepare()

    def prepare(self):
        features = ['keywords', 'cast', 'genres', 'director']
        for f in features:
            self.df[f] = self.df[f].fillna('')

        self.df['combined'] = self.df['keywords'] + ' ' + self.df['cast'] + ' ' + self.df['genres'] + ' ' + self.df['director']

        self.vectorizer = TfidfVectorizer()
        self.matrix = self.vectorizer.fit_transform(self.df['combined'])
        self.similarity = cosine_similarity(self.matrix)

    def recommend(self, movie, top_n=6):
        movie = movie.lower()
        if movie not in self.df['title'].str.lower().values:
            return []

        idx = self.df[self.df['title'].str.lower() == movie].index[0]
        scores = list(enumerate(self.similarity[idx]))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:top_n+1]

        return [{"title": self.df.iloc[i[0]]['title'], "score": round(i[1]*100,2)} for i in scores]

    def get_titles(self):
        return list(self.df['title'].values)
