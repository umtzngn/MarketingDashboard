# data_loader.py
import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime, timedelta
from config.settings import COLUMN_MAPPING, COUNTRY_ISO_MAP

class DataLoader:
    def __init__(self, data_folder='.'):
        self.data_folder = data_folder
        self.df = None

    def load_data(self):
        all_files = glob.glob(os.path.join(self.data_folder, "*.csv")) + \
                    glob.glob(os.path.join(self.data_folder, "*.xlsx"))
        
        df_list = []
        print(f"Dashboard System v9.1 Initialized. Found {len(all_files)} files.")

        for filename in all_files:
            if os.path.basename(filename).startswith('~$'): continue 
            try:
                if filename.endswith('.csv'): 
                    df_temp = pd.read_csv(filename)
                else: 
                    df_temp = pd.read_excel(filename)
                
                if df_temp.empty: continue

                # Platform simulation based on filename if missing
                current_cols = [c.lower() for c in df_temp.columns]
                if not any(x in current_cols for x in ['platform', 'source']):
                    fname_lower = filename.lower()
                    if 'facebook' in fname_lower: p = 'Facebook'
                    elif 'google' in fname_lower: p = 'Google Ads'
                    elif 'linkedin' in fname_lower: p = 'LinkedIn'
                    elif 'tiktok' in fname_lower: p = 'TikTok'
                    else: p = 'Other'
                    df_temp['Platform_Simulated'] = p
                
                df_list.append(df_temp)
                print(f"   Read: {os.path.basename(filename)}")
            except Exception as e:
                print(f"   Error ({os.path.basename(filename)}): {str(e)}")

        if not df_list:
            print("No data found. Creating dummy data.")
            self._create_dummy_data()
        else:
            self.df = pd.concat(df_list, ignore_index=True)
            self._standardize_columns()
        
        return self.df

    def _standardize_columns(self):
        new_columns = {}
        for col in self.df.columns:
            col_lower = str(col).lower().strip()
            mapped = False
            for std_name, aliases in COLUMN_MAPPING.items():
                if col_lower in aliases:
                    new_columns[col] = std_name
                    mapped = True
                    break
            if not mapped and col == 'Platform_Simulated':
                new_columns[col] = 'Platform'
        self.df = self.df.rename(columns=new_columns)
        
        # Numeric Cleaning
        for col in ['Spend', 'Clicks', 'Impressions', 'Conversions', 'Reach', 'Sentiment']:
            if col not in self.df.columns: self.df[col] = 0
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)
            
        # Simulation for missing critical data
        if self.df['Conversions'].sum() == 0:
            self.df['Conversions'] = (self.df['Clicks'] * np.random.uniform(0.02, 0.08, len(self.df))).astype(int)

        if 'Country' not in self.df.columns:
            self.df['Country'] = np.random.choice(['USA', 'GBR', 'DEU', 'TUR'], size=len(self.df))
        else:
            self.df['Country'] = self.df['Country'].apply(lambda x: COUNTRY_ISO_MAP.get(str(x).lower().strip(), str(x)))

        if 'Device' not in self.df.columns:
            self.df['Device'] = np.random.choice(['Mobile', 'Desktop', 'Tablet'], size=len(self.df), p=[0.7, 0.25, 0.05])
        
        if 'Placement' not in self.df.columns:
            self.df['Placement'] = np.random.choice(['Feed', 'Story', 'Search', 'Reels'], size=len(self.df))

        if self.df['Sentiment'].sum() == 0:
             self.df['Sentiment'] = np.random.uniform(-0.5, 0.9, len(self.df))

        for col in ['Campaign', 'AdName', 'Age', 'Gender', 'Platform']:
            if col not in self.df.columns: self.df[col] = 'Unknown'
            self.df[col] = self.df[col].fillna('Unknown').astype(str)

        if 'Date' in self.df.columns:
            self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')
        else:
            self.df['Date'] = [datetime.now() - timedelta(days=x % 90) for x in range(len(self.df))]
        self.df = self.df.dropna(subset=['Date'])

        # Calculate Derived Metrics
        self.df['CPC'] = np.where(self.df['Clicks'] > 0, self.df['Spend'] / self.df['Clicks'], 0)
        self.df['CTR'] = np.where(self.df['Impressions'] > 0, (self.df['Clicks'] / self.df['Impressions']) * 100, 0)
        self.df['CPM'] = np.where(self.df['Impressions'] > 0, (self.df['Spend'] / self.df['Impressions']) * 1000, 0)
        self.df['Frequency'] = np.where(self.df['Reach'] > 0, self.df['Impressions'] / self.df['Reach'], 1)
        self.df['CR'] = np.where(self.df['Clicks'] > 0, (self.df['Conversions'] / self.df['Clicks']) * 100, 0)

    def _create_dummy_data(self):
        dates = pd.date_range(end=datetime.now(), periods=60).tolist() * 10
        data = {
            'Date': dates,
            'Platform': ['Facebook', 'Google', 'Instagram'] * 200,
            'Spend': np.random.randint(50, 800, 600),
            'Clicks': np.random.randint(5, 80, 600),
            'Impressions': np.random.randint(1000, 15000, 600),
            'Reach': np.random.randint(800, 12000, 600),
            'Campaign': [f'Camp_{i%8}' for i in range(600)],
            'AdName': ['Ad_A', 'Ad_B', 'Ad_C'] * 200,
            'Device': np.random.choice(['Mobile', 'Desktop'], 600),
            'Placement': np.random.choice(['Feed', 'Story'], 600),
            'Country': np.random.choice(['TUR', 'USA', 'GBR'], 600),
            'Age': np.random.choice(['25-34', '35-44'], 600),
            'Gender': np.random.choice(['Male', 'Female'], 600),
            'Sentiment': np.random.uniform(-0.5, 0.9, 600)
        }
        self.df = pd.DataFrame(data)
        self._standardize_columns()