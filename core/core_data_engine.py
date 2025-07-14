import math
import re
import os
import pandas as pd
from collections import Counter

class CoreDataEngine:
    def __init__(self):
        pass

    def infer_data_type(self, series):
        if pd.api.types.is_integer_dtype(series):
            return "int"
        elif pd.api.types.is_float_dtype(series):
            return "float"
        elif pd.api.types.is_bool_dtype(series):
            return "bool"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
        else:
            return "string"

    def compute_entropy(self, values):
        if len(values) == 0:
            return 0.0
        counter = Counter(values)
        total = len(values)
        entropy = -sum((count/total) * math.log2(count/total) for count in counter.values())
        return round(entropy, 4)

    def infer_regex_pattern(self, values, sample_size=100):
        def simplify(val):
            return re.sub(r'[A-Z]', 'A',
                   re.sub(r'[a-z]', 'a',
                   re.sub(r'\d', '9', val)))

        simplified = [simplify(v) for v in values[:sample_size] if isinstance(v, str)]
        if not simplified:
            return None
        pattern_counts = Counter(simplified)
        most_common_pattern, _ = pattern_counts.most_common(1)[0]
        return most_common_pattern

    def profile_column(self, series: pd.Series, total_rows: int) -> dict:
        non_null_series = series.dropna()
        n_unique = non_null_series.nunique()
        data_type = self.infer_data_type(series)

        profile = {
            "data_type": str(data_type),
            "is_unique": bool(n_unique == total_rows),
            "is_complete": bool(series.isnull().sum() == 0),
            "is_categorical": bool((n_unique < 0.1 * total_rows) and (data_type in ["string", "int"])),
            "num_unique_values": float(n_unique),
            "sample_values": [str(v) for v in non_null_series.unique()[:5]]
        }
        if data_type in ["string", "int"]:
            profile["entropy"] = self.compute_entropy(non_null_series.astype(str).tolist())
        if data_type == "string":
            profile["regex_pattern"] = self.infer_regex_pattern(non_null_series.tolist())

        return profile

    # def profile_table(self, file_path: str) -> dict:
    #     df = pd.read_csv(file_path)
    #     total_rows = len(df)
    #     table_profile = {
    #         "table_name": os.path.basename(file_path),
    #         "num_rows": total_rows,
    #         "columns": {}
    #     }

    #     for col in df.columns:
    #         table_profile["columns"][col] = self.profile_column(df[col], total_rows)

    #     return table_profile

    # def profile_multiple_tables(self, file_paths: list) -> dict:
    #     result = {}
    #     for file in file_paths:
    #         result[os.path.basename(file)] = self.profile_table(file)
    #     return result

    def detect_primary_keys(self, profile_data):
        table_keys = {}
        for table, meta in profile_data.items():
            primary_keys = []
            candidate_keys = []

            for col, props in meta["columns"].items():
                if props["is_unique"] and props["is_complete"]:
                    primary_keys.append(col)
                elif props["is_unique"]:
                    candidate_keys.append(col)

            table_keys[table] = {
                "primary_keys": primary_keys,
                "candidate_keys": candidate_keys
            }
        return table_keys

    # def detect_foreign_keys(self, file_paths, profile_data, table_keys):
    #     dataframes = {os.path.basename(file): pd.read_csv(file) for file in file_paths}
    #     relationships = []

    #     for from_table_path, df_from in dataframes.items():
    #         from_table = os.path.basename(from_table_path)
    #         for from_col in df_from.columns:
    #             from_profile = profile_data[from_table]["columns"][from_col]
    #             if from_profile["is_unique"]:
    #                 continue

    #             from_values = set(df_from[from_col].dropna())

    #             for to_table_path, df_to in dataframes.items():
    #                 to_table = os.path.basename(to_table_path)
    #                 if from_table == to_table:
    #                     continue

    #                 for pk_col in table_keys[to_table]["primary_keys"]:
    #                     to_values = set(df_to[pk_col].dropna())
    #                     if not from_values or not to_values:
    #                         continue

    #                     common = from_values & to_values
    #                     overlap_ratio = len(common) / len(from_values)

    #                     if overlap_ratio > 0.8:
    #                         relationships.append({
    #                             "from_table": from_table,
    #                             "from_column": from_col,
    #                             "to_table": to_table,
    #                             "to_column": pk_col,
    #                             "confidence": round(overlap_ratio, 4)
    #                         })
    #     return relationships

    def process_multiple_data(self, csv_data_dict: dict) -> list:
        """
        Args:
            csv_data_dict: Dict of {filename: pd.DataFrame}
        Returns:
            List of relationship dicts
        """
        profile_data = self.profile_multiple_dataframes(csv_data_dict)
        table_keys = self.detect_primary_keys(profile_data)
        relationships = self.detect_foreign_keys_from_dfs(csv_data_dict, profile_data, table_keys)
        return relationships

    def profile_multiple_dataframes(self, df_dict: dict) -> dict:
        result = {}
        for fname, df in df_dict.items():
            total_rows = len(df)
            result[fname] = {
                "table_name": fname,
                "num_rows": total_rows,
                "columns": {
                    col: self.profile_column(df[col], total_rows) for col in df.columns
                }
            }
        return result

    def detect_foreign_keys_from_dfs(self, df_dict: dict, profile_data: dict, table_keys: dict) -> list:
        relationships = []
        for from_table, df_from in df_dict.items():
            for from_col in df_from.columns:
                from_profile = profile_data[from_table]["columns"][from_col]
                if from_profile["is_unique"]:
                    continue

                from_values = set(df_from[from_col].dropna())

                for to_table, df_to in df_dict.items():
                    if from_table == to_table:
                        continue

                    for pk_col in table_keys[to_table]["primary_keys"]:
                        to_values = set(df_to[pk_col].dropna())
                        if not from_values or not to_values:
                            continue

                        common = from_values & to_values
                        overlap_ratio = len(common) / len(from_values)

                        if overlap_ratio > 0.8:
                            relationships.append({
                                "from_table": from_table,
                                "from_column": from_col,
                                "to_table": to_table,
                                "to_column": pk_col,
                                "confidence": round(overlap_ratio, 4)
                            })
        return relationships
