import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from textstat import flesch_reading_ease, gunning_fog, syllable_count

input_file = pd.read_excel('Input.xlsx')

for index, row in input_file.iterrows():
    url_id = row['URL_ID']
    url = row['URL']
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        paragraphs = soup.select('.td-pb-span8.td-main-content p')
        if paragraphs:
            article_text = ' '.join(paragraph.get_text() for paragraph in paragraphs)
        else:
            alt_paragraphs = soup.select('.tdb-block-inner p')
            if alt_paragraphs:
                article_text = ' '.join(paragraph.get_text() for paragraph in alt_paragraphs)
            else:
                print(f"No content found for URL_ID: {url_id}")
                continue

        with open(f'{url_id}.txt', 'w', encoding='utf-8') as file:
            file.write(article_text)
    else:
        print(f"Failed to fetch URL: {url}")

input_file = pd.read_excel('Output_Data_Structure.xlsx')

positive_words = set()
negative_words = set()

with open('MasterDictionary/positive-words.txt', 'r') as pos_file:
    positive_words = set(pos_file.read().splitlines())

with open('MasterDictionary/negative-words.txt', 'r') as neg_file:
    negative_words = set(neg_file.read().splitlines())

stopwords_list = set()

stopwords_folder = 'StopWords'
for filename in os.listdir(stopwords_folder):
    if filename.endswith('.txt'):
        with open(os.path.join(stopwords_folder, filename), 'r') as stopwords_file:
            stopwords_list.update(stopwords_file.read().splitlines())

url_ids = []
positive_scores = []
negative_scores = []
polarity_scores = []
subjectivity_scores = []
avg_sentence_lengths = []
percentage_complex_words = []
fog_indices = []
avg_words_per_sentence = []
complex_word_counts = []
word_counts = []
syllables_per_word = []
personal_pronouns = []
avg_word_lengths = []

for index, row in input_file.iterrows():
    url_id = row['URL_ID']
    file_path = f'C:\\Users\\RAVIRAJ SODHA\\Desktop\\Blackcoffer\\{url_id}.txt'#Please Replace this path with your Folder Path on your machine

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            article_text = file.read()

        sentences = sent_tokenize(article_text)
        words = word_tokenize(article_text)

        words_cleaned = [word.lower() for word in words if word.isalpha() and word.lower() not in stopwords_list]

        positive_count = sum(1 for word in words_cleaned if word in positive_words)
        negative_count = sum(1 for word in words_cleaned if word in negative_words)
        total_words = len(words_cleaned)
        if total_words != 0:
            positive_score = positive_count / total_words
            negative_score = negative_count / total_words
        else:
            positive_score, negative_score = 0, 0

        polarity_score = positive_score - negative_score

        subjectivity_score = TextBlob(article_text).sentiment.subjectivity

        if len(sentences) > 0:
            avg_sentence_length = sum(len(sent.split()) for sent in sentences) / len(sentences)
        else:
            avg_sentence_length = 0

        if len(words_cleaned) > 0:
            percentage_complex_words.append(len([word for word in words_cleaned if syllable_count(word) > 2]) / len(words_cleaned) * 100)
            fog_indices.append(gunning_fog(article_text))
            avg_words_per_sentence.append(len(words_cleaned) / len(sentences))
            complex_word_counts.append(len([word for word in words_cleaned if syllable_count(word) > 2]))
            word_counts.append(len(words_cleaned))
            syllables_per_word.append(syllable_count(' '.join(words_cleaned)) / len(words_cleaned))
            avg_word_lengths.append(sum(len(word) for word in words_cleaned) / len(words_cleaned))
        else:
            percentage_complex_words.append(0)
            fog_indices.append(0)
            avg_words_per_sentence.append(0)
            complex_word_counts.append(0)
            word_counts.append(0)
            syllables_per_word.append(0)
            avg_word_lengths.append(0)

        personal_pronoun_count = sum(1 for word in words_cleaned if word.lower() in ['i', 'me', 'my', 'mine', 'myself', 'we', 'our', 'ours', 'ourselves'])
        total_personal_pronouns = personal_pronoun_count / word_counts[-1] if word_counts[-1] > 0 else 0

        url_ids.append(url_id)
        positive_scores.append(positive_score)
        negative_scores.append(negative_score)
        polarity_scores.append(polarity_score)
        subjectivity_scores.append(subjectivity_score)
        avg_sentence_lengths.append(avg_sentence_length)
        personal_pronouns.append(total_personal_pronouns)

    else:
        print(f'File not found for URL_ID: {url_id}')

output_df = pd.DataFrame({
    'URL_ID': url_ids,
    'POSITIVE SCORE': positive_scores,
    'NEGATIVE SCORE': negative_scores,
    'POLARITY SCORE': polarity_scores,
    'SUBJECTIVITY SCORE': subjectivity_scores,
    'AVG SENTENCE LENGTH': avg_sentence_lengths,
    'PERCENTAGE OF COMPLEX WORDS': percentage_complex_words,
    'FOG INDEX': fog_indices,
    'AVG NUMBER OF WORDS PER SENTENCE': avg_words_per_sentence,
    'COMPLEX WORD COUNT': complex_word_counts,
    'WORD COUNT': word_counts,
    'SYLLABLE PER WORD': syllables_per_word,
    'PERSONAL PRONOUNS': personal_pronouns,
    'AVG WORD LENGTH': avg_word_lengths
})

output_df.to_excel('output_analysis.xlsx', index=False)
