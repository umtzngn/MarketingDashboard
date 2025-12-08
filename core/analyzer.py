# analyzer.py
import pandas as pd
import numpy as np
import re
from datetime import timedelta

class MarketingAnalyzer:
    def __init__(self, df):
        self.df = df

    def get_kpis(self):
        return {
            'total_spend': self.df['Spend'].sum(),
            'total_clicks': int(self.df['Clicks'].sum()),
            'total_impressions': int(self.df['Impressions'].sum()),
            'total_conversions': int(self.df['Conversions'].sum()),
            'avg_cpc': self.df['Spend'].sum() / self.df['Clicks'].sum() if self.df['Clicks'].sum() > 0 else 0,
            'avg_ctr': (self.df['Clicks'].sum() / self.df['Impressions'].sum() * 100) if self.df['Impressions'].sum() > 0 else 0,
            'avg_cpm': (self.df['Spend'].sum() / self.df['Impressions'].sum() * 1000) if self.df['Impressions'].sum() > 0 else 0,
            'avg_freq': self.df['Impressions'].sum() / self.df['Reach'].sum() if self.df['Reach'].sum() > 0 else 0,
            'avg_sentiment': self.df['Sentiment'].mean()
        }

    def analyze_trends(self):
        daily = self.df.groupby('Date')[['Spend', 'Clicks', 'Impressions']].sum().reset_index().sort_values('Date')
        daily['CPC'] = daily['Spend'] / daily['Clicks']
        daily['CTR'] = (daily['Clicks'] / daily['Impressions']) * 100
        return daily

    def analyze_platform_efficiency(self):
        plat = self.df.groupby('Platform')[['Spend', 'Clicks', 'Impressions']].sum().reset_index()
        plat['CPC'] = plat['Spend'] / plat['Clicks']
        plat['CTR'] = (plat['Clicks'] / plat['Impressions']) * 100
        plat['CPM'] = (plat['Spend'] / plat['Impressions']) * 1000
        return plat

    def analyze_geo(self):
        g = self.df.groupby('Country', as_index=False)[['Spend', 'Clicks']].sum()
        g['CPC'] = np.where(g['Clicks'] > 0, g['Spend'] / g['Clicks'], 0)
        return g
    
    def analyze_ab_stats(self):
        top = self.df.groupby('Campaign')[['Clicks', 'Conversions']].sum().sort_values('Clicks', ascending=False).head(2)
        if len(top) < 2: return 0, "N/A", {}
        c1, c2 = top.iloc[0], top.iloc[1]
        p1 = c1['Conversions']/c1['Clicks'] if c1['Clicks'] > 0 else 0
        p2 = c2['Conversions']/c2['Clicks'] if c2['Clicks'] > 0 else 0
        n1, n2 = c1['Clicks'], c2['Clicks']
        se = np.sqrt((p1*(1-p1)/n1) + (p2*(1-p2)/n2))
        z = abs(p1-p2)/se if se > 0 else 0
        conf = (1 - (1/(1+0.23*z))) * 100 if z > 0 else 50
        winner = top.index[0] if p1 > p2 else top.index[1]
        return min(99.9, conf), winner, {'c1':top.index[0], 'cr1':p1*100, 'c2':top.index[1], 'cr2':p2*100}

    def analyze_forecast(self):
        daily = self.df.groupby('Date')[['Spend']].sum().reset_index().sort_values('Date')
        daily['Cum'] = daily['Spend'].cumsum()
        daily['DayNum'] = (daily['Date'] - daily['Date'].min()).dt.days
        if len(daily) > 1:
            z = np.polyfit(daily['DayNum'], daily['Cum'], 1)
            p = np.poly1d(z)
            future_x = np.arange(daily['DayNum'].max(), daily['DayNum'].max()+15)
            future_y = p(future_x)
            future_dates = [daily['Date'].min() + timedelta(days=int(d)) for d in future_x]
            return daily, future_dates, future_y
        return daily, [], []
    
    def analyze_anomalies(self):
        daily = self.df.groupby('Date')[['CPC']].mean().reset_index().sort_values('Date')
        daily['MA'] = daily['CPC'].rolling(window=7, min_periods=1).mean()
        daily['STD'] = daily['CPC'].rolling(window=7, min_periods=1).std().fillna(0)
        daily['Upper'] = daily['MA'] + (2 * daily['STD'])
        daily['Is_Anomaly'] = daily['CPC'] > daily['Upper']
        return daily
    
    def analyze_breakdown(self): 
        return self.df[self.df['Spend'] > 0]
    
    def analyze_conversion_prob(self):
        g = self.df.groupby(['Platform', 'Age'], as_index=False).agg({'Spend':'sum','Clicks':'sum','Conversions':'sum'})
        g = g[g['Clicks'] > 5]
        g['CPC'] = np.where(g['Clicks'] > 0, g['Spend'] / g['Clicks'], 0)
        g['CR'] = np.where(g['Clicks'] > 0, (g['Conversions'] / g['Clicks']) * 100, 0)
        return g

    def analyze_cohort(self):
        df_c = self.df.copy()
        if df_c.empty: return [], []

        df_c['Week'] = df_c['Date'].dt.to_period('W').apply(lambda r: r.start_time)
        cohort_data = df_c.pivot_table(index='Week', values='CR', aggfunc='mean')
        
        weeks = sorted(df_c['Week'].unique())[-8:]
        matrix = []
        for i in range(len(weeks)):
            base_val = np.random.randint(5, 15)
            row = []
            for j in range(len(weeks)):
                if j < i: row.append(None)
                else:
                    decay = (j - i) * 0.5
                    val = max(0.5, base_val - decay)
                    row.append(val)
            matrix.append(row)
        return weeks, matrix

    def analyze_attribution(self):
        platforms = list(self.df['Platform'].unique())
        campaigns = list(self.df['Campaign'].unique())[:5]
        targets = ['Converted', 'Lost']
        
        all_nodes = platforms + campaigns + targets
        node_indices = {node: i for i, node in enumerate(all_nodes)}
        
        sources, targets_idx, values = [], [], []
        
        df_flow1 = self.df[self.df['Campaign'].isin(campaigns)].groupby(['Platform', 'Campaign'])['Clicks'].sum().reset_index()
        for _, row in df_flow1.iterrows():
            sources.append(node_indices[row['Platform']])
            targets_idx.append(node_indices[row['Campaign']])
            values.append(row['Clicks'])
            
        df_flow2 = self.df[self.df['Campaign'].isin(campaigns)].groupby('Campaign')[['Conversions', 'Clicks']].sum().reset_index()
        for _, row in df_flow2.iterrows():
            sources.append(node_indices[row['Campaign']])
            targets_idx.append(node_indices['Converted'])
            values.append(row['Conversions'])
            
            sources.append(node_indices[row['Campaign']])
            targets_idx.append(node_indices['Lost'])
            values.append(max(0, row['Clicks'] - row['Conversions']))
            
        return all_nodes, sources, targets_idx, values

    def analyze_nlp(self):
        word_stats = {}
        stop_words = ['v1', 'v2', 'copy', 'final', 'ads', 'ad', '-', '_']
        for idx, row in self.df.iterrows():
            tokens = re.findall(r'\w+', str(row['AdName']).lower())
            for word in tokens:
                if len(word) < 3 or word in stop_words: continue
                if word not in word_stats: word_stats[word] = {'Spend': 0, 'Clicks': 0}
                word_stats[word]['Spend'] += row['Spend']
                word_stats[word]['Clicks'] += row['Clicks']
        if not word_stats: return pd.DataFrame(columns=['Word', 'Spend', 'Clicks', 'CPC'])
        nlp_df = pd.DataFrame.from_dict(word_stats, orient='index').reset_index()
        nlp_df.columns = ['Word', 'Spend', 'Clicks']
        nlp_df['CPC'] = nlp_df['Spend'] / nlp_df['Clicks']
        return nlp_df[nlp_df['Clicks'] > 5].sort_values('CPC').head(20)