# core/data_loader.py
import os
import glob
from datetime import datetime

import numpy as np
import pandas as pd

from config.settings import COLUMN_MAPPING, COUNTRY_ISO_MAP


# Hangi kolonları standart olarak beklediğimizi tanımlayalım
CANONICAL_COLUMNS = list(COLUMN_MAPPING.keys())

# Metrik kolonlar: numerik olacak, yoksa 0 ile doldurulacak
METRIC_COLUMNS = ["Spend", "Clicks", "Impressions", "Reach", "Conversions"]


class DataLoader:
    """
    Gerçek platform (Facebook / LinkedIn / Google Ads) verilerini
    tek DataFrame'de birleştirip kolonları standart formata çevirir.
    Kesinlikle random / mock data üretmez.
    """

    def __init__(self, data_folder: str = "."):
        self.data_folder = data_folder
        self.df: pd.DataFrame | None = None

    # -----------------------------
    # Public API
    # -----------------------------
    def load_data(self) -> pd.DataFrame:
        """
        data_folder içindeki tüm CSV / Excel dosyalarını okur,
        birleştirir ve standardize eder.
        """
        files = self._find_input_files()

        if not files:
            raise FileNotFoundError(
                f"No CSV/XLSX files found in folder: {self.data_folder}"
            )

        frames: list[pd.DataFrame] = []
        for path in files:
            df = self._read_single_file(path)
            if df is None or df.empty:
                continue

            df["SourceFile"] = os.path.basename(path)
            frames.append(df)

        if not frames:
            raise ValueError(
                f"Input files found but could not read any data from: {files}"
            )

        raw = pd.concat(frames, ignore_index=True)
        standardized = self._standardize_columns(raw)
        self.df = standardized
        return standardized

    # -----------------------------
    # Internal helpers
    # -----------------------------
    def _find_input_files(self) -> list[str]:
        patterns = ["*.csv", "*.xlsx", "*.xls"]
        files: list[str] = []
        for pattern in patterns:
            files.extend(glob.glob(os.path.join(self.data_folder, pattern)))
        return files

    def _read_single_file(self, path: str) -> pd.DataFrame | None:
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".csv":
                df = pd.read_csv(path)
            else:
                # .xlsx veya .xls
                df = pd.read_excel(path)
            return df
        except Exception as e:
            print(f"[DataLoader] Failed to read {path}: {e}")
            return None

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        - COLUMN_MAPPING'e göre kolon isimlerini canonical hale getirir
        - Eksik canonical kolonları ekler (metrikler için 0, diğerleri için NaN)
        - Tarih, ülke, platform gibi alanları temizler
        """
        df = df.copy()

        # 1) Kolon isimlerini küçük harfe map'leyerek mapping yap
        lower_to_original = {c.lower(): c for c in df.columns}

        rename_map: dict[str, str] = {}

        for canonical, candidates in COLUMN_MAPPING.items():
            # Eğer zaten birebir bu isimde kolon varsa, onu kullan
            if canonical in df.columns:
                continue

            found_original = None

            # Aday isimlerden biri mevcut mu (case-insensitive)?
            for cand in candidates:
                cand_lower = cand.lower()
                if cand_lower in lower_to_original:
                    found_original = lower_to_original[cand_lower]
                    break

            if found_original is not None:
                rename_map[found_original] = canonical

        if rename_map:
            df = df.rename(columns=rename_map)

        # 2) Eksik canonical kolonlar için default değerler ekle
        for col in CANONICAL_COLUMNS:
            if col not in df.columns:
                if col in METRIC_COLUMNS:
                    df[col] = 0.0
                else:
                    df[col] = pd.NA

        # 3) Tip dönüşümleri ve temizleme
        df = self._clean_types_and_values(df)

        return df

    def _clean_types_and_values(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # --- Date ---
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            # Tarihi olmayan satırlar çok kafa karıştırır, bunları atmak genelde daha iyi
            df = df.dropna(subset=["Date"])
        else:
            # Normalde buraya düşmemesi lazım çünkü az önce ekledik,
            # ama yine de koruma amaçlı:
            df["Date"] = pd.NaT

        # --- Numeric metrikler ---
        for col in METRIC_COLUMNS:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        # --- Platform ---
        # Eğer Excel'den Platform kolonu dolu geliyorsa onu aynen kullan,
        # boş/NaN olan satırlar için dosya isminden tahmin etmeye çalış.
        if "Platform" in df.columns:
            df["Platform"] = df["Platform"].astype(str).str.strip()
            if "SourceFile" in df.columns:
                mask_empty = df["Platform"].isin(["", "nan", "NaN"])
                df.loc[mask_empty, "Platform"] = df.loc[mask_empty, "SourceFile"].apply(
                    self._infer_platform_from_filename
                )
        elif "SourceFile" in df.columns:
            df["Platform"] = df["SourceFile"].apply(
                self._infer_platform_from_filename
            )
        else:
            df["Platform"] = pd.NA

        # --- Country -> ISO3 map ---
        if "Country" in df.columns:
            df["Country"] = df["Country"].astype(str).str.strip()
            lower_map = {k.lower(): v for k, v in COUNTRY_ISO_MAP.items()}

            def _map_country(val: str) -> str:
                if not val or val.lower() in ["nan", "none"]:
                    return val
                # eğer zaten ISO3 formatında ise (3 harf, büyük) dokunma
                if len(val) == 3 and val.isupper():
                    return val
                return lower_map.get(val.lower(), val)

            df["Country"] = df["Country"].apply(_map_country)

        # --- Age / Gender / Device / Placement / AdName / Campaign basit temizleme ---
        for col in ["Age", "Gender", "Device", "Placement", "Campaign", "AdName"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        # --- Sentiment ---
        # Sentiment için ARTIK random üretim yok.
        # Eğer Excel'den numeric bir kolon geliyorsa kullanılır, yoksa NaN kalır.
        if "Sentiment" in df.columns:
            df["Sentiment"] = pd.to_numeric(df["Sentiment"], errors="coerce")

        return df

    def _infer_platform_from_filename(self, filename: str) -> str:
        """
        Dosya adından platform tahmini.
        Burada da random yok, sadece string eşleştirme var.
        """
        name = filename.lower()
        if "facebook" in name or "meta" in name:
            return "Facebook"
        if "linkedin" in name:
            return "LinkedIn"
        if "google" in name or "adwords" in name or "ads_" in name:
            return "Google Ads"
        return "Unknown"
