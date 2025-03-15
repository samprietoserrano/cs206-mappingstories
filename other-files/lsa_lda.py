import nltk
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import TruncatedSVD, LatentDirichletAllocation
from gensim.corpora import Dictionary
from gensim.models import LdaModel
from nltk.corpus import stopwords
import re

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Function to preprocess text
def preprocess_text(text):
    text = re.sub(r'\W+', ' ', text.lower())  # Remove special characters
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens)

# Load and preprocess text
with open("transcripts/transcript-050924.txt", "r", encoding="utf-8") as file:
    raw_text = file.read()

processed_text = preprocess_text(raw_text)

# LSA Approach
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform([processed_text])

lsa = TruncatedSVD(n_components=2)  # Extract 2 main topics
lsa_matrix = lsa.fit_transform(X)

terms = vectorizer.get_feature_names_out()
lsa_topics = []

for i, topic in enumerate(lsa.components_):
    words = [terms[j] for j in topic.argsort()[:-6:-1]]  # Top 5 words per topic
    lsa_topics.append(words)

print("LSA Topics:", lsa_topics)

# LDA Approach
vectorizer = CountVectorizer()
X_counts = vectorizer.fit_transform([processed_text])
lda = LatentDirichletAllocation(n_components=2, random_state=42)  # 2 topics
lda_matrix = lda.fit_transform(X_counts)

terms = vectorizer.get_feature_names_out()
lda_topics = []

for i, topic in enumerate(lda.components_):
    words = [terms[j] for j in topic.argsort()[:-6:-1]]  # Top 5 words per topic
    lda_topics.append(words)

print("LDA Topics:", lda_topics)

# Manually match topics to locations
# geo_keywords = {
#     "paris": ["eiffel", "seine", "france"],
#     "new york": ["manhattan", "brooklyn", "times square"],
#     "london": ["thames", "big ben", "uk"],
#     "tokyo": ["shibuya", "sakura", "japan"]
# }

# def match_location(topics):
#     for location, keywords in geo_keywords.items():
#         for topic in topics:
#             if any(word in topic for word in keywords):
#                 return location
#     return "Unknown"

# main_location_lsa = match_location(lsa_topics)
# main_location_lda = match_location(lda_topics)

# print("Main Location (LSA):", main_location_lsa)
# print("Main Location (LDA):", main_location_lda)
