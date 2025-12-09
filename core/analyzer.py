# core/analyzer.py
import pandas as pd
import numpy as np
from datetime import timedelta
from math import erf, sqrt


def _norm_cdf(x: float) -> float:
    """Standard normal CDF (no SciPy dependency)."""
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


class MarketingAnalyzer:
    """
    Performs real-data marketing analysis across Facebook, LinkedIn, and Google Ads.
    No random or mock data generation is used.

    Eski API ile uyumlu olması için:
    - get_kpis
    - analyze_trends
    - analyze_platform_efficiency
    - analyze_cohort
    - analyze_attribution
    - analyze_conversion_prob
    - analyze_forecast
    - analyze_anomalies
    - analyze_breakdown
    - analyze_geo
    - analyze_nlp
    - analyze_ab_stats

    fonksiyonları da sağlanıyor.
    """

    def __init__(self, df: pd.DataFrame):
        if df is None or df.empty:
            raise ValueError("MarketingAnalyzer requires a non-empty DataFrame")
        self.df = df.copy()
        self._prepare_base_metrics()

    # -------------------------------------------------------------
    # Core metric preparation
    # -------------------------------------------------------------
    def _prepare_base_metrics(self):
        """Adds safe calculated metrics like CPC, CTR, CVR."""
        df = self.df
        df["Spend"] = pd.to_numeric(df.get("Spend", 0), errors="coerce").fillna(0.0)
        df["Clicks"] = pd.to_numeric(df.get("Clicks", 0), errors="coerce").fillna(0.0)
        df["Impressions"] = pd.to_numeric(df.get("Impressions", 0), errors="coerce").fillna(0.0)
        df["Conversions"] = pd.to_numeric(df.get("Conversions", 0), errors="coerce").fillna(0.0)

        df["CPC"] = np.where(df["Clicks"] > 0, df["Spend"] / df["Clicks"], np.nan)
        df["CTR"] = np.where(df["Impressions"] > 0, df["Clicks"] / df["Impressions"], np.nan)
        df["CVR"] = np.where(df["Clicks"] > 0, df["Conversions"] / df["Clicks"], np.nan)

        # Clean date
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        self.df = df

    # -------------------------------------------------------------
    # New-style KPI summary
    # -------------------------------------------------------------
    def get_summary_kpis(self):
        """Returns total spend, clicks, impressions, conversions, CTR, CVR, CPC."""
        total_spend = self.df["Spend"].sum()
        total_clicks = self.df["Clicks"].sum()
        total_impr = self.df["Impressions"].sum()
        total_conv = self.df["Conversions"].sum()

        ctr = total_clicks / total_impr if total_impr > 0 else np.nan
        cvr = total_conv / total_clicks if total_clicks > 0 else np.nan
        cpc = total_spend / total_clicks if total_clicks > 0 else np.nan

        return {
            "Total Spend": total_spend,
            "Total Clicks": total_clicks,
            "Total Impressions": total_impr,
            "Total Conversions": total_conv,
            "CTR": ctr,
            "CVR": cvr,
            "CPC": cpc,
        }

    # -------------------------------------------------------------
    # Eski API ile uyumlu get_kpis
    # -------------------------------------------------------------
    def get_kpis(self):
        """
        HTML raporun beklediği KPI sözlüğünü döner.
        Kullanılan anahtarlar:
        - total_spend
        - total_clicks
        - total_impressions
        - total_conversions
        - avg_cpc
        - avg_ctr  (yüzde)
        - avg_cpm
        - avg_sentiment
        """
        df = self.df

        total_spend = df["Spend"].sum()
        total_clicks = df["Clicks"].sum()
        total_impr = df["Impressions"].sum()
        total_conv = df["Conversions"].sum()

        # Ortalama metrikler (0'a bölme korumalı)
        avg_cpc = total_spend / total_clicks if total_clicks > 0 else 0.0
        avg_ctr = (total_clicks / total_impr * 100.0) if total_impr > 0 else 0.0  # yüzde
        avg_cpm = total_spend / (total_impr / 1000.0) if total_impr > 0 else 0.0

        # Sentiment kolonundan ortalama (gerçek data varsa kullan, yoksa 0)
        if "Sentiment" in df.columns:
            s = pd.to_numeric(df["Sentiment"], errors="coerce")
            if s.dropna().empty:
                avg_sentiment = 0.0
            else:
                avg_sentiment = float(s.mean())
        else:
            avg_sentiment = 0.0

        kpis = {
            "total_spend": float(total_spend),
            "total_clicks": int(total_clicks),
            "total_impressions": int(total_impr),
            "total_conversions": int(total_conv),
            "avg_cpc": float(avg_cpc),
            "avg_ctr": float(avg_ctr),
            "avg_cpm": float(avg_cpm),
            "avg_sentiment": float(avg_sentiment),
        }
        return kpis



    # -------------------------------------------------------------
    # Trend analysis (new)
    # -------------------------------------------------------------
    def get_daily_trends(self):
        """Aggregates metrics per date and platform."""
        if "Date" not in self.df.columns or self.df["Date"].isna().all():
            return pd.DataFrame()

        group_cols = ["Date"]
        if "Platform" in self.df.columns:
            group_cols.append("Platform")

        df_t = (
            self.df.groupby(group_cols)
            .agg({"Spend": "sum", "Clicks": "sum", "Impressions": "sum", "Conversions": "sum"})
            .reset_index()
        )
        df_t["CPC"] = np.where(df_t["Clicks"] > 0, df_t["Spend"] / df_t["Clicks"], np.nan)
        df_t["CTR"] = np.where(df_t["Impressions"] > 0, df_t["Clicks"] / df_t["Impressions"], np.nan)
        df_t["CVR"] = np.where(df_t["Clicks"] > 0, df_t["Conversions"] / df_t["Clicks"], np.nan)
        return df_t

    # -------------------------------------------------------------
    # Eski API: analyze_trends -> new get_daily_trends
    # -------------------------------------------------------------
    def analyze_trends(self):
        return self.get_daily_trends()

    # -------------------------------------------------------------
    # Platform efficiency
    # -------------------------------------------------------------
    def analyze_platform_efficiency(self):
        """
        Platform bazlı toplu performans:
        Spend, Impressions, Clicks, Conversions, CTR, CVR, CPC, CPM
        """
        if "Platform" not in self.df.columns:
            return pd.DataFrame()

        df = (
            self.df.groupby("Platform")
            .agg({
                "Spend": "sum",
                "Impressions": "sum",
                "Clicks": "sum",
                "Conversions": "sum",
            })
            .reset_index()
        )

        # Oranlar
        df["CTR"] = np.where(df["Impressions"] > 0,
                             df["Clicks"] / df["Impressions"],
                             np.nan)
        df["CVR"] = np.where(df["Clicks"] > 0,
                             df["Conversions"] / df["Clicks"],
                             np.nan)
        df["CPC"] = np.where(df["Clicks"] > 0,
                             df["Spend"] / df["Clicks"],
                             np.nan)

        # 🔹 Eksik olan: CPM = Spend / (Impressions / 1000)
        df["CPM"] = np.where(df["Impressions"] > 0,
                             df["Spend"] / (df["Impressions"] / 1000.0),
                             np.nan)

        return df


    # -------------------------------------------------------------
    # Cohort: şimdilik devre dışı (placeholder)
    # -------------------------------------------------------------
    def analyze_cohort(self):
        """
        Eski versiyonda burası tamamen random cohort üretimi yapıyordu.
        Gerçek bir cohort analizi tasarlayana kadar boş döndürüyoruz.
        main.py ve charts tarafı [] gördüğünde genelde 'no data' grafiği çizer.
        """
        return [], []

    # -------------------------------------------------------------
    # Anomaly detection (CPC)
    # -------------------------------------------------------------
    def detect_cpc_anomalies(self, window: int = 7):
        """
        Detect CPC anomalies using rolling mean ± 2σ.

        charts.create_anomaly_chart(anom_df) şu kolonları bekliyor:
        - 'Upper'      : üst limit
        - 'Lower'      : alt limit
        - 'Is_Anomaly' : True/False
        Ayrıca 'CPC' ve 'Date' zaten mevcut.
        """
        df = self.get_daily_trends()
        if df.empty:
            return pd.DataFrame()

        df = df.sort_values("Date").copy()

        df["rolling_mean"] = df["CPC"].rolling(window).mean()
        df["rolling_std"] = df["CPC"].rolling(window).std()

        # charts.py ile uyumlu kolon isimleri:
        df["Upper"] = df["rolling_mean"] + 2 * df["rolling_std"]
        df["Lower"] = df["rolling_mean"] - 2 * df["rolling_std"]
        df["Is_Anomaly"] = df["CPC"] > df["Upper"]

        # rolling_* kolonlarını debug için bırakabiliriz; şart değil.
        return df


    def analyze_anomalies(self):
        return self.detect_cpc_anomalies()

    # -------------------------------------------------------------
    # A/B Test (Two-proportion z-test)
    # -------------------------------------------------------------
    def ab_test_analysis(self):
        """Compare top 2 campaigns by clicks using a two-proportion z-test."""
        if "Campaign" not in self.df.columns:
            return {"status": "no_campaign_data"}

        df = (
            self.df.groupby("Campaign")[["Clicks", "Conversions"]]
            .sum()
            .sort_values("Clicks", ascending=False)
            .head(2)
        )

        if len(df) < 2:
            return {"status": "not_enough_campaigns"}

        c1, c2 = df.index
        clicks1, conv1 = df.loc[c1, ["Clicks", "Conversions"]]
        clicks2, conv2 = df.loc[c2, ["Clicks", "Conversions"]]

        if clicks1 < 30 or clicks2 < 30:
            return {"status": "insufficient_sample_size"}

        p1 = conv1 / clicks1 if clicks1 > 0 else 0
        p2 = conv2 / clicks2 if clicks2 > 0 else 0
        p_pool = (conv1 + conv2) / (clicks1 + clicks2)
        se = np.sqrt(p_pool * (1 - p_pool) * (1 / clicks1 + 1 / clicks2))
        z = (p1 - p2) / se if se > 0 else 0.0
        p_value = 2 * (1 - _norm_cdf(abs(z)))

        return {
            "status": "ok",
            "Campaign_A": c1,
            "Campaign_B": c2,
            "p1": p1,
            "p2": p2,
            "z": z,
            "p_value": p_value,
            "confidence": (1 - p_value) * 100,
            "winner": c1 if p1 > p2 else c2,
        }

    def analyze_ab_stats(self):
        """
        main.py şu şekilde bekliyor:
        ab_conf, ab_winner, ab_details = analyzer.analyze_ab_stats()
        """
        res = self.ab_test_analysis()
        if res.get("status") != "ok":
            return 0.0, None, {}

        details = {
            "c1": res["Campaign_A"],
            "c2": res["Campaign_B"],
            "p1": res["p1"],
            "p2": res["p2"],
            "p_value": res["p_value"],
            "z": res["z"],
        }
        return res["confidence"], res["winner"], details

    # -------------------------------------------------------------
    # Forecast
    # -------------------------------------------------------------
    def forecast_spend(self, days_forward: int = 15):
        """Simple linear projection of daily spend."""
        trends = self.get_daily_trends()
        if trends.empty:
            return pd.DataFrame()

        df = trends.groupby("Date")["Spend"].sum().reset_index()
        df = df.sort_values("Date")
        df["t"] = range(len(df))

        if len(df) < 5:
            return pd.DataFrame()

        coeffs = np.polyfit(df["t"], df["Spend"], 1)
        df["forecast"] = np.polyval(coeffs, df["t"])
        last_t = df["t"].iloc[-1]
        forecast_dates = [df["Date"].iloc[-1] + timedelta(days=i) for i in range(1, days_forward + 1)]
        forecast_values = np.polyval(coeffs, np.arange(last_t + 1, last_t + days_forward + 1))
        forecast_df = pd.DataFrame({"Date": forecast_dates, "forecast": forecast_values})
        return forecast_df

    def analyze_forecast(self):
        # Günlük trendleri al (Platform kırılımı varsa da gelsin)
        trends = self.get_daily_trends()
        if trends.empty:
            # charts tarafı boş DataFrame görünce zaten düzgün handle edebilir
            return trends, [], []

        # Forecast için platform kırılımını atıp toplam spend üzerinden gidelim
        daily = (
            trends.groupby("Date", as_index=False)["Spend"]
            .sum()
            .sort_values("Date")
        )

        # Kümülatif harcama (Cum) – charts.py burada bunu bekliyor
        daily["Cum"] = daily["Spend"].cumsum()

        # Zaman indexi (0, 1, 2, ...)
        daily["t"] = range(len(daily))

        # Çok az gün varsa forecast yapmanın anlamı yok
        if len(daily) < 5:
            return daily, [], []

        # Basit lineer trend: Cum ~ t
        coeffs = np.polyfit(daily["t"], daily["Cum"], 1)

        last_t = daily["t"].iloc[-1]
        horizon = 15  # 15 gün ileri

        # Forecast için t değerleri
        future_t = np.arange(last_t + 1, last_t + horizon + 1)

        # Forecast tarihleri: son tarihten itibaren ileriye doğru
        last_date = daily["Date"].iloc[-1]
        f_dates = [last_date + timedelta(days=i) for i in range(1, horizon + 1)]

        # Kümülatif harcama forecast'i
        f_vals = np.polyval(coeffs, future_t)

        return daily, f_dates, f_vals


    # -------------------------------------------------------------
    # Geo analysis
    # -------------------------------------------------------------
    def geo_performance(self):
        if "Country" not in self.df.columns:
            return pd.DataFrame()
        df = (
            self.df.groupby("Country")
            .agg({"Spend": "sum", "Clicks": "sum", "Impressions": "sum", "Conversions": "sum"})
            .reset_index()
        )
        df["CPC"] = np.where(df["Clicks"] > 0, df["Spend"] / df["Clicks"], np.nan)
        df["CTR"] = np.where(df["Impressions"] > 0, df["Clicks"] / df["Impressions"], np.nan)
        df["CVR"] = np.where(df["Clicks"] > 0, df["Conversions"] / df["Clicks"], np.nan)
        return df

    def analyze_geo(self):
        return self.geo_performance()

    # -------------------------------------------------------------
    # Attribution (Sankey) - high level summary
    # -------------------------------------------------------------
    def attribution_summary(self):
        if "Campaign" not in self.df.columns or "Platform" not in self.df.columns:
            return pd.DataFrame()
        df = (
            self.df.groupby(["Platform", "Campaign"])
            .agg({"Clicks": "sum", "Conversions": "sum"})
            .reset_index()
        )
        df["NonConversions"] = np.maximum(df["Clicks"] - df["Conversions"], 0)
        return df

    def analyze_attribution(self):
        """
        Eski API: nodes, src, tgt, vals döndürüyordu.
        Burada Platform -> Campaign -> Converted / Lost yapısı kuruyoruz.
        """
        df = self.attribution_summary()
        if df.empty:
            return [], [], [], []

        nodes = []
        node_index = {}

        def add_node(name: str) -> int:
            if name not in node_index:
                node_index[name] = len(nodes)
                nodes.append(name)
            return node_index[name]

        sources = []
        targets = []
        values = []

        # Outcome nodes
        converted_idx = add_node("Converted")
        lost_idx = add_node("Lost")

        for _, row in df.iterrows():
            plat = str(row["Platform"])
            camp = str(row["Campaign"])
            clicks = float(row["Clicks"])
            conv = float(row["Conversions"])
            nonconv = float(row["NonConversions"])

            p_idx = add_node(plat)
            c_idx = add_node(camp)

            # Platform -> Campaign (value: clicks)
            if clicks > 0:
                sources.append(p_idx)
                targets.append(c_idx)
                values.append(clicks)

            # Campaign -> Converted / Lost
            if conv > 0:
                sources.append(c_idx)
                targets.append(converted_idx)
                values.append(conv)
            if nonconv > 0:
                sources.append(c_idx)
                targets.append(lost_idx)
                values.append(nonconv)

        return nodes, sources, targets, values

    # -------------------------------------------------------------
    # Funnel metrics (overall)
    # -------------------------------------------------------------
    def funnel_summary(self):
        """Simple Impressions → Clicks → Conversions funnel."""
        imp = self.df["Impressions"].sum()
        clk = self.df["Clicks"].sum()
        conv = self.df["Conversions"].sum()

        return {
            "Impressions": imp,
            "Clicks": clk,
            "Conversions": conv,
            "CTR": clk / imp if imp > 0 else np.nan,
            "CVR": conv / clk if clk > 0 else np.nan,
        }

    # (eski API için ayrı analyze_conversion_prob yok; funnel/similar için kullanılıyor olabilir)

    def analyze_conversion_prob(self, min_clicks: int = 30):
        """
        Audience bazlı dönüşüm analizi.

        Çıktı kolonları:
        - Age
        - Gender (varsa)
        - Clicks
        - Conversions
        - Spend
        - CR  : Conversion Rate (%)  = Conversions / Clicks * 100
        - CPC : Cost per Click      = Spend / Clicks
        """
        df = self.df.copy()

        # Age yoksa bu analiz yapılamaz
        if "Age" not in df.columns:
            return pd.DataFrame()

        # Clicks > 0 olan satırlar
        df = df[df["Clicks"] > 0]
        if df.empty:
            return pd.DataFrame()

        # Grup kolonları: Age (+ Gender varsa)
        group_cols = ["Age"]
        if "Gender" in df.columns:
            group_cols.append("Gender")

        grouped = (
            df.groupby(group_cols, as_index=False)
              .agg(
                  Clicks=("Clicks", "sum"),
                  Conversions=("Conversions", "sum"),
                  Spend=("Spend", "sum"),
              )
        )

        # Çok az tıklaması olan segmentleri at (noise temizliği)
        grouped = grouped[grouped["Clicks"] >= min_clicks]
        if grouped.empty:
            return pd.DataFrame()

        grouped["CR"] = np.where(
            grouped["Clicks"] > 0,
            grouped["Conversions"] / grouped["Clicks"] * 100.0,
            np.nan,
        )
        grouped["CPC"] = np.where(
            grouped["Clicks"] > 0,
            grouped["Spend"] / grouped["Clicks"],
            np.nan,
        )

        return grouped


    # -------------------------------------------------------------
    # Device & Placement breakdown
    # -------------------------------------------------------------
    def device_placement_summary(self):
        if "Device" not in self.df.columns or "Placement" not in self.df.columns:
            return pd.DataFrame()
        df = (
            self.df.groupby(["Device", "Placement"])
            .agg({"Spend": "sum", "Clicks": "sum", "Conversions": "sum"})
            .reset_index()
        )
        df["CPC"] = np.where(df["Clicks"] > 0, df["Spend"] / df["Clicks"], np.nan)
        return df

    def analyze_breakdown(self):
        """
        Sunburst grafiği için device breakdown döner:
        Platform -> Device -> Placement hiyerarşisi.

        charts.create_sunburst(df_break) içinde:
        path=['Platform', 'Device', 'Placement'], values='Spend'
        beklendiği için bu kolonları mutlaka üretmemiz gerekiyor.
        """
        # Device / Placement kolonları yoksa 'Unknown' ile doldur
        df = self.df.copy()

        if "Platform" not in df.columns:
            return pd.DataFrame()

        if "Device" not in df.columns:
            df["Device"] = "Unknown"
        if "Placement" not in df.columns:
            df["Placement"] = "Unknown"

        # Grup: Platform - Device - Placement
        df_grouped = (
            df.groupby(["Platform", "Device", "Placement"])
            .agg({
                "Spend": "sum",
                "Clicks": "sum",
                "Conversions": "sum",
            })
            .reset_index()
        )

        # İstersen CVR da hesaplayalım (ileride başka yerde kullanırsan hazır dursun)
        df_grouped["CVR"] = np.where(
            df_grouped["Clicks"] > 0,
            df_grouped["Conversions"] / df_grouped["Clicks"],
            np.nan
        )

        return df_grouped


    # -------------------------------------------------------------
    # Audience (Age + Gender)
    # -------------------------------------------------------------
    def audience_summary(self):
        if "Age" not in self.df.columns or "Gender" not in self.df.columns:
            return pd.DataFrame()
        df = (
            self.df.groupby(["Age", "Gender"])
            .agg({"Spend": "sum", "Clicks": "sum", "Conversions": "sum"})
            .reset_index()
        )
        df["CPC"] = np.where(df["Clicks"] > 0, df["Spend"] / df["Clicks"], np.nan)
        df["CVR"] = np.where(df["Clicks"] > 0, df["Conversions"] / df["Clicks"], np.nan)
        return df

    # -------------------------------------------------------------
    # NLP: Keyword frequency from AdName
    # -------------------------------------------------------------
    def adname_keyword_analysis(self, top_n: int = 20):
        if "AdName" not in self.df.columns:
            return pd.DataFrame()
        stopwords = {"v1", "v2", "copy", "final", "ads", "ad", "-", "_", "the", "a", "an"}
        keywords: dict[str, float] = {}

        for _, row in self.df.iterrows():
            name = str(row["AdName"]).lower()
            clicks = row.get("Clicks", 0)
            for token in name.replace("-", " ").replace("_", " ").split():
                if token not in stopwords and len(token) > 2:
                    keywords[token] = keywords.get(token, 0) + clicks

        if not keywords:
            return pd.DataFrame()

        df = pd.DataFrame(
            sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:top_n],
            columns=["Keyword", "Total_Clicks"],
        )
        return df

    def analyze_nlp(self):
        return self.adname_keyword_analysis()
