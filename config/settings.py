# config.py

COLUMN_MAPPING = {
    'Date': ['date', 'tarih', 'day', 'gun'],
    'Spend': ['amount spent', 'cost', 'total spent', 'spend', 'harcama', 'tutar'],
    'Clicks': ['clicks', 'link clicks', 'tiklama', 'tiklamalar', 'click'],
    'Impressions': ['impressions', 'gosterim', 'goruntulenme', 'impression'],
    'Reach': ['reach', 'erisim', 'unique reach', 'ulasim'],
    'Conversions': ['conversions', 'donusumler', 'purchases', 'satis', 'leads', 'results'],
    'Campaign': ['campaign name', 'kampanya adi', 'campaign', 'kampanya'],
    'AdName': ['ad name', 'reklam adi', 'ad', 'creative name', 'reklam'],
    'Platform': ['platform', 'source', 'kaynak'],
    'Country': ['country', 'region', 'ulke', 'bolge', 'location'],
    'Age': ['age', 'yas', 'age range'],
    'Gender': ['gender', 'cinsiyet'],
    'Device': ['device', 'cihaz', 'device platform'],
    'Placement': ['placement', 'yerlesim', 'platform position'],
    'Sentiment': ['sentiment', 'sentiment score', 'duygu', 'puan']
}

COUNTRY_ISO_MAP = {
    'turkey': 'TUR', 'turkiye': 'TUR', 'tr': 'TUR',
    'usa': 'USA', 'united states': 'USA', 'us': 'USA',
    'uk': 'GBR', 'united kingdom': 'GBR', 'germany': 'DEU', 'almanya': 'DEU'
}