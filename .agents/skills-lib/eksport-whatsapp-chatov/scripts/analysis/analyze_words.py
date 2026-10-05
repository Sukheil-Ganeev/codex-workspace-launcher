#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Частотный анализ слов в WhatsApp переписке.

Функции:
1. Токенизация сообщений (RU, EN, AR)
2. Удаление стоп-слов (RU, EN, AR)
3. Частотный анализ:
   - Топ слов общий
   - Топ слов по контакту
   - Топ фраз (n-grams)
4. TF-IDF для важных терминов
5. Word Cloud генерация (PNG)
6. Тематическое моделирование (LDA)
7. Специфичные термины туризма
8. Экспорт: JSON, PNG (word cloud)

Зависимости:
  pip install nltk wordcloud gensim matplotlib numpy pyarabic
"""

import sys
import os
import re
import json
import argparse
from datetime import datetime
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set

sys.stdout.reconfigure(encoding='utf-8')

# Опциональные импорты с fallback
try:
    import nltk
    from nltk.tokenize import word_tokenize, RegexpTokenizer
    from nltk.util import ngrams
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("WARNING: nltk не установлен. pip install nltk")

try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Для headless серверов
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False
    print("WARNING: wordcloud/matplotlib не установлены. pip install wordcloud matplotlib")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("WARNING: sklearn не установлен. pip install scikit-learn")

try:
    from gensim import corpora
    from gensim.models import LdaModel
    GENSIM_AVAILABLE = True
except ImportError:
    GENSIM_AVAILABLE = False
    print("WARNING: gensim не установлен. pip install gensim")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Инициализация NLTK данных
if NLTK_AVAILABLE:
    nltk_data_dir = Path.home() / 'nltk_data'
    nltk_data_dir.mkdir(exist_ok=True)
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("Downloading NLTK punkt...")
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        try:
            nltk.download('punkt_tab', quiet=True)
        except:
            pass
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print("Downloading NLTK stopwords...")
        nltk.download('stopwords', quiet=True)


# =====================================================================
# СТОП-СЛОВА
# =====================================================================

# Русские стоп-слова (расширенный список)
STOPWORDS_RU = {
    # Местоимения
    'я', 'ты', 'он', 'она', 'оно', 'мы', 'вы', 'они',
    'меня', 'тебя', 'его', 'её', 'нас', 'вас', 'их',
    'мне', 'тебе', 'ему', 'ей', 'нам', 'вам', 'им',
    'мной', 'тобой', 'им', 'ею', 'нами', 'вами', 'ими',
    'мой', 'твой', 'наш', 'ваш', 'свой',
    'моя', 'твоя', 'наша', 'ваша', 'своя',
    'моё', 'твоё', 'наше', 'ваше', 'своё',
    'мои', 'твои', 'наши', 'ваши', 'свои',
    'этот', 'тот', 'такой', 'какой', 'который',
    'эта', 'та', 'такая', 'какая', 'которая',
    'это', 'то', 'такое', 'какое', 'которое',
    'эти', 'те', 'такие', 'какие', 'которые',
    'весь', 'вся', 'всё', 'все', 'сам', 'сама', 'само', 'сами',
    'кто', 'что', 'чей', 'чья', 'чьё', 'чьи',

    # Предлоги
    'в', 'во', 'на', 'за', 'из', 'от', 'до', 'по', 'под', 'над',
    'к', 'ко', 'у', 'о', 'об', 'с', 'со', 'при', 'про', 'без',
    'для', 'между', 'через', 'после', 'перед', 'около',

    # Союзы
    'и', 'а', 'но', 'или', 'да', 'же', 'ли', 'бы',
    'что', 'как', 'когда', 'если', 'чтобы', 'хотя', 'пока', 'потому',

    # Частицы
    'не', 'ни', 'вот', 'вон', 'ведь', 'уже', 'ещё', 'еще', 'только',
    'лишь', 'даже', 'именно', 'просто', 'точно', 'разве', 'неужели',

    # Наречия
    'где', 'куда', 'откуда', 'там', 'тут', 'здесь', 'сюда', 'туда',
    'так', 'очень', 'совсем', 'почти', 'тоже', 'также',
    'всегда', 'никогда', 'иногда', 'часто', 'редко',
    'сейчас', 'теперь', 'тогда', 'потом', 'раньше', 'позже',
    'много', 'мало', 'больше', 'меньше', 'сколько',

    # Глаголы-связки и вспомогательные
    'быть', 'есть', 'был', 'была', 'было', 'были', 'будет', 'будут',
    'буду', 'будем', 'будете', 'будешь',
    'можно', 'нужно', 'надо', 'нельзя', 'должен', 'должна', 'должны',

    # Числительные
    'один', 'два', 'три', 'четыре', 'пять',
    'первый', 'второй', 'третий',

    # Междометия и разговорные
    'ок', 'окей', 'ага', 'угу', 'ну', 'ой', 'ах', 'эх', 'ух',
    'привет', 'пока', 'здравствуйте', 'здравствуй',
    'спасибо', 'пожалуйста', 'извините', 'простите',

    # WhatsApp специфичные
    'медиа', 'файл', 'фото', 'видео', 'аудио', 'голосовое',
    'сообщение', 'удалено', 'пропущенный', 'вызов',
}

# Английские стоп-слова
STOPWORDS_EN = {
    # Pronouns
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
    'you', 'your', 'yours', 'yourself', 'yourselves',
    'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
    'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
    'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',

    # Prepositions
    'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
    'up', 'about', 'into', 'over', 'after', 'beneath', 'under',
    'above', 'below', 'between', 'behind', 'before', 'through',

    # Conjunctions
    'and', 'but', 'or', 'nor', 'so', 'yet', 'both', 'either', 'neither',
    'not', 'only', 'own', 'same', 'than', 'too', 'very',

    # Articles
    'a', 'an', 'the',

    # Auxiliary verbs
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
    'will', 'would', 'shall', 'should', 'may', 'might', 'must',
    'can', 'could', 'need', 'dare', 'ought', 'used',

    # Adverbs
    'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both',
    'few', 'more', 'most', 'other', 'some', 'such', 'no', 'any',
    'just', 'now', 'then', 'here', 'there', 'once', 'again',
    'always', 'never', 'sometimes', 'often', 'still', 'already',

    # Common words
    'ok', 'okay', 'yes', 'no', 'hi', 'hello', 'hey', 'bye', 'goodbye',
    'thanks', 'thank', 'please', 'sorry',

    # WhatsApp specific
    'media', 'omitted', 'deleted', 'message', 'missed', 'call',
}

# Арабские стоп-слова
STOPWORDS_AR = {
    # Частицы и предлоги
    'في', 'من', 'على', 'إلى', 'عن', 'مع', 'هذا', 'هذه', 'ذلك', 'تلك',
    'الذي', 'التي', 'الذين', 'اللواتي', 'ما', 'ماذا', 'لماذا', 'كيف',
    'أين', 'متى', 'هل', 'أم', 'أو', 'و', 'ف', 'ثم', 'لكن', 'بل',

    # Местоимения
    'أنا', 'أنت', 'أنتِ', 'هو', 'هي', 'نحن', 'أنتم', 'أنتن', 'هم', 'هن',
    'لي', 'لك', 'له', 'لها', 'لنا', 'لكم', 'لهم',

    # Глаголы-связки
    'كان', 'كانت', 'كانوا', 'يكون', 'تكون', 'أكون',
    'هناك', 'هنا', 'كل', 'بعض', 'كثير', 'قليل',

    # Числительные
    'واحد', 'اثنان', 'ثلاثة', 'أربعة', 'خمسة',

    # Разговорные
    'شكرا', 'شكراً', 'مرحبا', 'أهلا', 'مع السلامة',
    'نعم', 'لا', 'أيوه', 'طيب', 'تمام', 'أوكي',
}

# Объединенный набор стоп-слов
ALL_STOPWORDS = STOPWORDS_RU | STOPWORDS_EN | STOPWORDS_AR

# Добавим NLTK стоп-слова если доступны
if NLTK_AVAILABLE:
    try:
        from nltk.corpus import stopwords as nltk_stopwords
        ALL_STOPWORDS |= set(nltk_stopwords.words('russian'))
        ALL_STOPWORDS |= set(nltk_stopwords.words('english'))
        try:
            ALL_STOPWORDS |= set(nltk_stopwords.words('arabic'))
        except:
            pass
    except:
        pass


# =====================================================================
# ТУРИСТИЧЕСКИЕ ТЕРМИНЫ (домен-специфичные)
# =====================================================================

TOURISM_TERMS = {
    # Экскурсии и туры
    'экскурсия', 'тур', 'сафари', 'поездка', 'путешествие',
    'обзорная', 'индивидуальная', 'групповая', 'частная',
    'tour', 'excursion', 'safari', 'trip', 'journey',

    # Достопримечательности ОАЭ
    'дубай', 'абу-даби', 'абудаби', 'шарджа', 'аджман', 'фуджейра',
    'dubai', 'abudhabi', 'abu-dhabi', 'sharjah', 'ajman', 'fujairah',
    'бурдж', 'халифа', 'burj', 'khalifa', 'atlantis', 'атлантис',
    'пальма', 'джумейра', 'palm', 'jumeirah', 'marina', 'марина',
    'молл', 'mall', 'эмиратс', 'emirates',
    'ferrari', 'феррари', 'warner', 'варнер', 'лувр', 'louvre',
    'aquaventure', 'аквавенчур', 'аквапарк', 'waterpark',

    # Транспорт
    'трансфер', 'transfer', 'аэропорт', 'airport',
    'встреча', 'pickup', 'доставка', 'dropoff',
    'машина', 'car', 'автомобиль', 'vehicle',
    'лимузин', 'limousine', 'минивэн', 'minivan',
    'яхта', 'yacht', 'катер', 'boat', 'лодка',

    # Билеты и парки
    'билет', 'ticket', 'входной', 'entrance', 'пропуск', 'pass',
    'парк', 'park', 'аттракцион', 'attraction',

    # Проживание
    'отель', 'hotel', 'гостиница', 'resort', 'курорт',
    'номер', 'room', 'бронь', 'booking', 'бронирование', 'reservation',

    # Питание
    'ресторан', 'restaurant', 'кафе', 'cafe',
    'ужин', 'dinner', 'обед', 'lunch', 'завтрак', 'breakfast',
    'круиз', 'cruise', 'дхоу', 'dhow',

    # Валюта и оплата
    'дирхам', 'dirham', 'aed', 'рубль', 'rub', 'доллар', 'usd',
    'оплата', 'payment', 'предоплата', 'deposit', 'баланс', 'balance',
    'курс', 'rate', 'обмен', 'exchange',
    'наличные', 'cash', 'карта', 'card', 'перевод', 'transfer',

    # Документы
    'паспорт', 'passport', 'виза', 'visa', 'ваучер', 'voucher',

    # Время
    'дата', 'date', 'время', 'time', 'час', 'hour',
    'утро', 'morning', 'вечер', 'evening', 'ночь', 'night',

    # Люди
    'гид', 'guide', 'водитель', 'driver', 'туристы', 'tourists',
    'гости', 'guests', 'пассажиры', 'passengers',
    'взрослый', 'adult', 'ребенок', 'child', 'дети', 'children',

    # Статусы
    'подтверждено', 'confirmed', 'ожидание', 'pending',
    'отменено', 'cancelled', 'завершено', 'completed',
}


# =====================================================================
# ТОКЕНИЗАЦИЯ
# =====================================================================

def detect_language(text: str) -> str:
    """Определить язык текста по символам."""
    # Подсчёт символов разных алфавитов
    cyrillic = len(re.findall(r'[а-яёА-ЯЁ]', text))
    arabic = len(re.findall(r'[\u0600-\u06FF]', text))
    latin = len(re.findall(r'[a-zA-Z]', text))

    total = cyrillic + arabic + latin
    if total == 0:
        return 'unknown'

    if cyrillic / total > 0.5:
        return 'ru'
    elif arabic / total > 0.5:
        return 'ar'
    elif latin / total > 0.5:
        return 'en'
    else:
        return 'mixed'


def clean_text(text: str) -> str:
    """Очистить текст от мусора."""
    if not text:
        return ''

    # Удаляем URL
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)

    # Удаляем email
    text = re.sub(r'\S+@\S+\.\S+', '', text)

    # Удаляем номера телефонов
    text = re.sub(r'\+?\d{10,15}', '', text)

    # Удаляем emoji (основные диапазоны Unicode)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    text = emoji_pattern.sub('', text)

    # Удаляем WhatsApp метки
    text = re.sub(r'\[.*?(ФОТО|ВИДЕО|АУДИО|ГОЛОСОВОЕ|ДОКУМЕНТ|СТИКЕР|GIF|КОНТАКТ|ЛОКАЦИЯ).*?\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\(медиа не сохранено.*?\)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<Media omitted>', '', text, flags=re.IGNORECASE)

    # Удаляем лишние пробелы
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def tokenize_text(text: str, language: str = 'auto') -> List[str]:
    """Токенизировать текст на слова."""
    if not text:
        return []

    # Очищаем текст
    text = clean_text(text)

    if not text:
        return []

    # Определяем язык если auto
    if language == 'auto':
        language = detect_language(text)

    # Приводим к нижнему регистру
    text = text.lower()

    # Токенизация
    if NLTK_AVAILABLE:
        try:
            # Используем RegexpTokenizer для лучшего контроля
            tokenizer = RegexpTokenizer(r'[а-яёa-z\u0600-\u06FF]+')
            tokens = tokenizer.tokenize(text)
        except:
            # Fallback на простой split
            tokens = re.findall(r'[а-яёa-z\u0600-\u06FF]+', text)
    else:
        # Без NLTK - простая токенизация regex
        tokens = re.findall(r'[а-яёa-z\u0600-\u06FF]+', text)

    # Фильтруем короткие токены (< 2 символов)
    tokens = [t for t in tokens if len(t) >= 2]

    return tokens


def remove_stopwords(tokens: List[str], custom_stopwords: Set[str] = None) -> List[str]:
    """Удалить стоп-слова из списка токенов."""
    stopwords = ALL_STOPWORDS.copy()
    if custom_stopwords:
        stopwords |= custom_stopwords

    return [t for t in tokens if t not in stopwords]


def extract_ngrams(tokens: List[str], n: int = 2) -> List[Tuple[str, ...]]:
    """Извлечь n-граммы из токенов."""
    if len(tokens) < n:
        return []

    if NLTK_AVAILABLE:
        return list(ngrams(tokens, n))
    else:
        # Ручная реализация
        return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]


# =====================================================================
# ЧАСТОТНЫЙ АНАЛИЗ
# =====================================================================

def count_word_frequencies(texts: List[str], remove_stops: bool = True) -> Counter:
    """Подсчитать частоты слов во всех текстах."""
    all_tokens = []

    for text in texts:
        tokens = tokenize_text(text)
        if remove_stops:
            tokens = remove_stopwords(tokens)
        all_tokens.extend(tokens)

    return Counter(all_tokens)


def count_ngram_frequencies(texts: List[str], n: int = 2, remove_stops: bool = True) -> Counter:
    """Подсчитать частоты n-грамм."""
    all_ngrams = []

    for text in texts:
        tokens = tokenize_text(text)
        if remove_stops:
            tokens = remove_stopwords(tokens)
        grams = extract_ngrams(tokens, n)
        all_ngrams.extend(grams)

    return Counter(all_ngrams)


def analyze_by_contact(messages: List[Dict], remove_stops: bool = True) -> Dict[str, Counter]:
    """Анализ частоты слов по контактам."""
    by_contact = defaultdict(list)

    for msg in messages:
        contact_id = msg.get('contact_id', msg.get('jid', 'unknown'))
        text = msg.get('text', '')
        if text:
            by_contact[contact_id].append(text)

    result = {}
    for contact_id, texts in by_contact.items():
        result[contact_id] = count_word_frequencies(texts, remove_stops)

    return result


# =====================================================================
# TF-IDF АНАЛИЗ
# =====================================================================

def calculate_tfidf(texts: List[str], top_n: int = 50) -> List[Tuple[str, float]]:
    """Вычислить TF-IDF и вернуть топ терминов."""
    if not SKLEARN_AVAILABLE:
        print("ОШИБКА: sklearn не установлен для TF-IDF")
        return []

    if not texts:
        return []

    # Предобработка текстов
    processed_texts = []
    for text in texts:
        tokens = tokenize_text(text)
        tokens = remove_stopwords(tokens)
        processed_texts.append(' '.join(tokens))

    # Фильтруем пустые
    processed_texts = [t for t in processed_texts if t.strip()]

    if not processed_texts:
        return []

    try:
        # TF-IDF векторизатор
        vectorizer = TfidfVectorizer(
            max_features=1000,
            min_df=2,  # Минимум в 2 документах
            max_df=0.95,  # Максимум в 95% документов
        )

        tfidf_matrix = vectorizer.fit_transform(processed_texts)
        feature_names = vectorizer.get_feature_names_out()

        # Средний TF-IDF по всем документам
        mean_tfidf = tfidf_matrix.mean(axis=0).A1

        # Сортируем по убыванию
        sorted_indices = mean_tfidf.argsort()[::-1]

        result = []
        for idx in sorted_indices[:top_n]:
            term = feature_names[idx]
            score = float(mean_tfidf[idx])
            if score > 0:
                result.append((term, round(score, 4)))

        return result

    except Exception as e:
        print(f"Ошибка TF-IDF: {e}")
        return []


# =====================================================================
# ТЕМАТИЧЕСКОЕ МОДЕЛИРОВАНИЕ (LDA)
# =====================================================================

def run_lda_analysis(texts: List[str], num_topics: int = 5, words_per_topic: int = 10) -> Dict:
    """Запустить LDA тематическое моделирование."""
    if not GENSIM_AVAILABLE:
        print("ОШИБКА: gensim не установлен для LDA")
        return {}

    if not texts:
        return {}

    # Подготовка документов
    documents = []
    for text in texts:
        tokens = tokenize_text(text)
        tokens = remove_stopwords(tokens)
        if tokens:
            documents.append(tokens)

    if len(documents) < 10:
        print("ПРЕДУПРЕЖДЕНИЕ: Слишком мало документов для LDA (< 10)")
        return {}

    try:
        # Создаём словарь и корпус
        dictionary = corpora.Dictionary(documents)

        # Фильтруем редкие и частые слова
        dictionary.filter_extremes(no_below=2, no_above=0.9)

        if len(dictionary) < 10:
            print("ПРЕДУПРЕЖДЕНИЕ: Слишком мало уникальных слов для LDA")
            return {}

        corpus = [dictionary.doc2bow(doc) for doc in documents]

        # Обучаем LDA
        lda_model = LdaModel(
            corpus=corpus,
            id2word=dictionary,
            num_topics=num_topics,
            random_state=42,
            passes=10,
            alpha='auto',
            eta='auto'
        )

        # Извлекаем темы
        topics = {}
        for topic_id in range(num_topics):
            topic_words = lda_model.show_topic(topic_id, topn=words_per_topic)
            topics[f"topic_{topic_id + 1}"] = {
                "words": [(word, round(prob, 4)) for word, prob in topic_words],
                "top_words": [word for word, prob in topic_words[:5]]
            }

        return {
            "num_topics": num_topics,
            "topics": topics,
            "total_documents": len(documents),
            "vocabulary_size": len(dictionary),
        }

    except Exception as e:
        print(f"Ошибка LDA: {e}")
        return {}


# =====================================================================
# WORD CLOUD ГЕНЕРАЦИЯ
# =====================================================================

def generate_wordcloud(word_freq: Dict[str, int], output_path: str,
                       title: str = "Word Cloud",
                       width: int = 1200, height: int = 600,
                       background_color: str = 'white',
                       colormap: str = 'viridis') -> bool:
    """Сгенерировать Word Cloud и сохранить как PNG."""
    if not WORDCLOUD_AVAILABLE:
        print("ОШИБКА: wordcloud не установлен")
        return False

    if not word_freq:
        print("ПРЕДУПРЕЖДЕНИЕ: Нет данных для Word Cloud")
        return False

    try:
        # Создаём Word Cloud
        wc = WordCloud(
            width=width,
            height=height,
            background_color=background_color,
            colormap=colormap,
            max_words=200,
            min_font_size=10,
            max_font_size=150,
            random_state=42,
            # Для кириллицы нужен шрифт
            font_path=None,  # Системный шрифт
        )

        # Генерируем из частот
        wc.generate_from_frequencies(word_freq)

        # Сохраняем
        plt.figure(figsize=(width/100, height/100), dpi=100)
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.title(title, fontsize=16, fontweight='bold')
        plt.tight_layout(pad=0)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close()

        print(f"Word Cloud сохранён: {output_path}")
        return True

    except Exception as e:
        print(f"Ошибка генерации Word Cloud: {e}")
        return False


# =====================================================================
# АНАЛИЗ ТУРИСТИЧЕСКИХ ТЕРМИНОВ
# =====================================================================

def extract_tourism_terms(texts: List[str]) -> Dict[str, int]:
    """Извлечь и подсчитать туристические термины."""
    all_tokens = []

    for text in texts:
        tokens = tokenize_text(text)
        all_tokens.extend(tokens)

    # Фильтруем только туристические термины
    tourism_tokens = [t for t in all_tokens if t in TOURISM_TERMS]

    return dict(Counter(tourism_tokens).most_common(100))


def categorize_tourism_terms(term_counts: Dict[str, int]) -> Dict[str, Dict[str, int]]:
    """Категоризировать туристические термины."""
    categories = {
        "destinations": {
            "terms": ['дубай', 'dubai', 'абу-даби', 'abudhabi', 'abu-dhabi', 'абудаби',
                     'шарджа', 'sharjah', 'аджман', 'ajman', 'фуджейра', 'fujairah'],
            "counts": {}
        },
        "attractions": {
            "terms": ['бурдж', 'халифа', 'burj', 'khalifa', 'atlantis', 'атлантис',
                     'ferrari', 'феррари', 'лувр', 'louvre', 'аквапарк', 'waterpark',
                     'молл', 'mall', 'пальма', 'palm'],
            "counts": {}
        },
        "transport": {
            "terms": ['трансфер', 'transfer', 'аэропорт', 'airport', 'машина', 'car',
                     'яхта', 'yacht', 'катер', 'boat', 'лимузин', 'limousine'],
            "counts": {}
        },
        "tours": {
            "terms": ['экскурсия', 'excursion', 'тур', 'tour', 'сафари', 'safari',
                     'круиз', 'cruise', 'дхоу', 'dhow'],
            "counts": {}
        },
        "accommodation": {
            "terms": ['отель', 'hotel', 'курорт', 'resort', 'номер', 'room',
                     'бронь', 'booking', 'бронирование', 'reservation'],
            "counts": {}
        },
        "payment": {
            "terms": ['дирхам', 'dirham', 'aed', 'рубль', 'rub', 'доллар', 'usd',
                     'оплата', 'payment', 'курс', 'rate', 'обмен', 'exchange'],
            "counts": {}
        }
    }

    for term, count in term_counts.items():
        for category, data in categories.items():
            if term.lower() in [t.lower() for t in data["terms"]]:
                data["counts"][term] = count
                break

    # Убираем пустые категории
    return {k: v["counts"] for k, v in categories.items() if v["counts"]}


# =====================================================================
# ЗАГРУЗКА ДАННЫХ
# =====================================================================

def load_messages_jsonl(filepath: str) -> List[Dict]:
    """Загрузить сообщения из JSONL файла."""
    messages = []

    if not os.path.exists(filepath):
        print(f"Файл не найден: {filepath}")
        return messages

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    messages.append(msg)
                except json.JSONDecodeError as e:
                    if line_num <= 5:
                        print(f"  Ошибка JSON в строке {line_num}: {e}")
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")

    return messages


# =====================================================================
# СОХРАНЕНИЕ РЕЗУЛЬТАТОВ
# =====================================================================

class NumpyJSONEncoder(json.JSONEncoder):
    """JSON encoder с поддержкой numpy типов."""
    def default(self, obj):
        if NUMPY_AVAILABLE:
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
        return super().default(obj)


def save_json(data: Dict, filepath: str):
    """Сохранить данные в JSON."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, cls=NumpyJSONEncoder)
    print(f"Сохранено: {filepath}")


def format_frequency_table(counter: Counter, top_n: int = 30, title: str = "Частота слов") -> str:
    """Форматировать частотную таблицу для вывода."""
    lines = [
        f"\n{title}",
        "=" * 50,
        f"{'#':>3} | {'Слово':<25} | {'Частота':>10}",
        "-" * 50
    ]

    for i, (word, count) in enumerate(counter.most_common(top_n), 1):
        lines.append(f"{i:>3} | {word:<25} | {count:>10}")

    lines.append("-" * 50)
    return "\n".join(lines)


# =====================================================================
# ГЛАВНАЯ ФУНКЦИЯ
# =====================================================================

def run_word_analysis(input_file: str, output_dir: str,
                      top_words: int = 100,
                      ngram_sizes: List[int] = [2, 3],
                      lda_topics: int = 5,
                      generate_clouds: bool = True) -> Dict:
    """Полный анализ слов."""

    print(f"\nЗагрузка сообщений из: {input_file}")
    messages = load_messages_jsonl(input_file)

    if not messages:
        print("Сообщения не найдены!")
        return {}

    print(f"Загружено {len(messages)} сообщений")

    # Извлекаем тексты
    texts = [msg.get('text', '') for msg in messages if msg.get('text')]
    print(f"Текстовых сообщений: {len(texts)}")

    if not texts:
        print("Нет текстовых сообщений для анализа!")
        return {}

    results = {
        "metadata": {
            "source_file": input_file,
            "analyzed_at": datetime.now().isoformat(),
            "total_messages": len(messages),
            "text_messages": len(texts),
            "version": "1.0.0"
        }
    }

    # ─────────────────────────────────────────────────────────────
    # 1. Частотный анализ слов
    # ─────────────────────────────────────────────────────────────
    print("\n[1/7] Частотный анализ слов...")
    word_freq = count_word_frequencies(texts, remove_stops=True)

    results["word_frequencies"] = {
        "total_unique_words": len(word_freq),
        "total_word_count": sum(word_freq.values()),
        "top_words": dict(word_freq.most_common(top_words))
    }

    print(format_frequency_table(word_freq, 20, "Топ-20 слов (без стоп-слов)"))

    # ─────────────────────────────────────────────────────────────
    # 2. N-граммы
    # ─────────────────────────────────────────────────────────────
    print("\n[2/7] Анализ n-грамм...")
    results["ngrams"] = {}

    for n in ngram_sizes:
        ngram_freq = count_ngram_frequencies(texts, n=n, remove_stops=True)
        # Преобразуем tuple в строку для JSON
        ngram_dict = {' '.join(gram): count for gram, count in ngram_freq.most_common(50)}
        results["ngrams"][f"{n}-grams"] = ngram_dict

        print(f"\nТоп-10 {n}-грамм:")
        for gram, count in list(ngram_freq.most_common(10)):
            print(f"  {' '.join(gram)}: {count}")

    # ─────────────────────────────────────────────────────────────
    # 3. Анализ по контактам
    # ─────────────────────────────────────────────────────────────
    print("\n[3/7] Анализ по контактам...")
    by_contact = analyze_by_contact(messages)

    contact_summaries = {}
    for contact_id, freq in by_contact.items():
        contact_summaries[contact_id] = {
            "total_words": sum(freq.values()),
            "unique_words": len(freq),
            "top_10": dict(freq.most_common(10))
        }

    results["by_contact"] = contact_summaries
    print(f"Проанализировано контактов: {len(contact_summaries)}")

    # ─────────────────────────────────────────────────────────────
    # 4. TF-IDF
    # ─────────────────────────────────────────────────────────────
    print("\n[4/7] TF-IDF анализ...")
    tfidf_terms = calculate_tfidf(texts, top_n=50)
    results["tfidf"] = {
        "top_terms": tfidf_terms
    }

    if tfidf_terms:
        print("\nТоп-15 TF-IDF терминов:")
        for term, score in tfidf_terms[:15]:
            print(f"  {term}: {score:.4f}")

    # ─────────────────────────────────────────────────────────────
    # 5. LDA тематическое моделирование
    # ─────────────────────────────────────────────────────────────
    print(f"\n[5/7] LDA тематическое моделирование ({lda_topics} тем)...")
    lda_results = run_lda_analysis(texts, num_topics=lda_topics)
    results["lda"] = lda_results

    if lda_results and "topics" in lda_results:
        print(f"\nНайдено {lda_results['num_topics']} тем:")
        for topic_name, topic_data in lda_results["topics"].items():
            top_words = topic_data.get("top_words", [])
            print(f"  {topic_name}: {', '.join(top_words)}")

    # ─────────────────────────────────────────────────────────────
    # 6. Туристические термины
    # ─────────────────────────────────────────────────────────────
    print("\n[6/7] Анализ туристических терминов...")
    tourism_counts = extract_tourism_terms(texts)
    tourism_categories = categorize_tourism_terms(tourism_counts)

    results["tourism_terms"] = {
        "all_terms": tourism_counts,
        "by_category": tourism_categories
    }

    if tourism_counts:
        print("\nТоп-15 туристических терминов:")
        for term, count in list(tourism_counts.items())[:15]:
            print(f"  {term}: {count}")

        print("\nПо категориям:")
        for category, terms in tourism_categories.items():
            if terms:
                total = sum(terms.values())
                print(f"  {category}: {total} упоминаний")

    # ─────────────────────────────────────────────────────────────
    # 7. Word Clouds
    # ─────────────────────────────────────────────────────────────
    if generate_clouds and WORDCLOUD_AVAILABLE:
        print("\n[7/7] Генерация Word Clouds...")

        clouds_dir = os.path.join(output_dir, "wordclouds")
        os.makedirs(clouds_dir, exist_ok=True)

        # Общий word cloud
        generate_wordcloud(
            dict(word_freq.most_common(200)),
            os.path.join(clouds_dir, "wordcloud_general.png"),
            title="Общий Word Cloud"
        )

        # Word cloud туристических терминов
        if tourism_counts:
            generate_wordcloud(
                tourism_counts,
                os.path.join(clouds_dir, "wordcloud_tourism.png"),
                title="Туристические термины",
                colormap='YlOrRd'
            )

        # Word cloud биграмм (топ-100)
        bigram_freq = count_ngram_frequencies(texts, n=2, remove_stops=True)
        bigram_dict = {' '.join(gram): count for gram, count in bigram_freq.most_common(100)}
        if bigram_dict:
            generate_wordcloud(
                bigram_dict,
                os.path.join(clouds_dir, "wordcloud_bigrams.png"),
                title="Биграммы",
                colormap='cool'
            )

        results["wordclouds"] = {
            "general": os.path.join(clouds_dir, "wordcloud_general.png"),
            "tourism": os.path.join(clouds_dir, "wordcloud_tourism.png"),
            "bigrams": os.path.join(clouds_dir, "wordcloud_bigrams.png"),
        }
    else:
        print("\n[7/7] Word Clouds пропущены (wordcloud не установлен)")

    # ─────────────────────────────────────────────────────────────
    # Сохранение результатов
    # ─────────────────────────────────────────────────────────────
    print("\nСохранение результатов...")
    os.makedirs(output_dir, exist_ok=True)

    # Основной JSON
    save_json(results, os.path.join(output_dir, "word_analysis.json"))

    # Отдельные файлы для удобства
    save_json(
        {"word_frequencies": results["word_frequencies"]},
        os.path.join(output_dir, "word_frequencies.json")
    )

    save_json(
        {"ngrams": results["ngrams"]},
        os.path.join(output_dir, "ngrams.json")
    )

    save_json(
        {"tourism_terms": results["tourism_terms"]},
        os.path.join(output_dir, "tourism_terms.json")
    )

    if results.get("lda"):
        save_json(
            {"lda": results["lda"]},
            os.path.join(output_dir, "lda_topics.json")
        )

    # ─────────────────────────────────────────────────────────────
    # Итоговая статистика
    # ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("АНАЛИЗ СЛОВ ЗАВЕРШЁН")
    print("=" * 60)
    print(f"Всего сообщений: {len(messages)}")
    print(f"Текстовых сообщений: {len(texts)}")
    print(f"Уникальных слов: {len(word_freq)}")
    print(f"Всего слов: {sum(word_freq.values())}")
    print(f"Контактов проанализировано: {len(contact_summaries)}")
    print(f"Туристических терминов: {len(tourism_counts)}")
    if lda_results:
        print(f"LDA тем: {lda_results.get('num_topics', 0)}")
    print(f"\nРезультаты сохранены в: {output_dir}")
    print("=" * 60)

    return results


# =====================================================================
# CLI
# =====================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Частотный анализ слов в WhatsApp переписке",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python analyze_words.py
  python analyze_words.py --input messages.jsonl
  python analyze_words.py --top-words 200 --lda-topics 10
  python analyze_words.py --no-clouds
        """
    )

    parser.add_argument(
        "--input", "-i",
        default="D:/Downloads/Chats/_база/raw/all_messages.jsonl",
        help="Входной JSONL файл с сообщениями"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="D:/Downloads/Chats/_аналитика/words",
        help="Директория для результатов"
    )
    parser.add_argument(
        "--top-words", "-t",
        type=int,
        default=100,
        help="Количество топ слов для сохранения (default: 100)"
    )
    parser.add_argument(
        "--lda-topics",
        type=int,
        default=5,
        help="Количество LDA тем (default: 5)"
    )
    parser.add_argument(
        "--no-clouds",
        action="store_true",
        help="Не генерировать Word Clouds"
    )
    parser.add_argument(
        "--ngrams",
        type=str,
        default="2,3",
        help="Размеры n-грамм через запятую (default: 2,3)"
    )

    args = parser.parse_args()

    # Парсим размеры n-грамм
    ngram_sizes = [int(x.strip()) for x in args.ngrams.split(",")]

    run_word_analysis(
        input_file=args.input,
        output_dir=args.output_dir,
        top_words=args.top_words,
        ngram_sizes=ngram_sizes,
        lda_topics=args.lda_topics,
        generate_clouds=not args.no_clouds
    )


if __name__ == "__main__":
    main()
