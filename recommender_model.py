import pandas as pd
import difflib
import os
import re
import json
import ast

def extract_symptoms_from_json(json_string):
    if pd.isna(json_string) or not isinstance(json_string, str): return ""
    try:
        data = json.loads(json_string)
    except:
        try: data = ast.literal_eval(json_string)
        except: return ""
    
    symptoms = []
    if isinstance(data, dict) and 'yes_symptoms' in data:
        for item in data['yes_symptoms']:
            text = item.get('text', '').strip()
            if text and text not in ["การรักษาก่อนหน้า", "Previous treatment"]:
                symptoms.append(text)
    return ", ".join(symptoms)

class SymptomRecommender:
    def __init__(self, df, col_gender, col_age, col_search):
        self.df = df
        self.col_gender = col_gender
        self.col_age = col_age
        self.col_search = col_search
        self.all_unique_symptoms = self._get_unique_symptoms()
        self.df['Age_Group'] = self.df[self.col_age].apply(self._assign_age_group)
    
    def _split_symptoms(self, text):
        if pd.isna(text) or text == "": return []
        tokens = re.split(r'[,;]+', str(text).strip())
        return [t.strip() for t in tokens if t.strip()]

    def _get_unique_symptoms(self):
        all_tokens = []
        for text in self.df[self.col_search].dropna():
            all_tokens.extend(self._split_symptoms(text))
        return sorted(list(set(all_tokens)))

    def _assign_age_group(self, age):
        if pd.isna(age): return 'Unknown'
        age = float(age)
        if age <= 6: return '0-6'
        elif age <= 18: return '7-18'
        elif age <= 60: return '19-60'
        else: return '60+'

    def find_closest_symptom(self, user_input_symptom):
        matches = difflib.get_close_matches(user_input_symptom, self.all_unique_symptoms, n=3, cutoff=0.6)
        return matches

    def recommend(self, gender, age, input_symptoms, top_n=3):
        if isinstance(input_symptoms, str):
            input_list = [s.strip() for s in input_symptoms.split(',')]
        else:
            input_list = input_symptoms

        matched_symptoms = []
        for symp in input_list:
            if symp not in self.all_unique_symptoms:
                closest = self.find_closest_symptom(symp)
                if closest: matched_symptoms.append(closest[0])
            else:
                matched_symptoms.append(symp)

        matched_symptoms = list(set(matched_symptoms))
        if not matched_symptoms:
            return {"error": True, "message": "ไม่พบอาการที่ระบุในระบบ"}

        def row_has_symptom(row):
            search_tokens = self._split_symptoms(row[self.col_search])
            summary_tokens = self._split_symptoms(row['Cleaned_Symptoms'])
            all_tokens = set(search_tokens + summary_tokens)
            return any(ms in all_tokens for ms in matched_symptoms)

        exact_match_df = self.df[self.df.apply(row_has_symptom, axis=1)]

        if len(exact_match_df) == 0:
            return {"error": False, "tier_1": [], "tier_2": [], "tier_3": [], "message": "ไม่มีข้อมูลอาการร่วมในระบบสำหรับเคสนี้"}

        target_group = self._assign_age_group(age)
        age_groups = ['0-6', '7-18', '19-60', '60+']
        idx = age_groups.index(target_group)
        neighbors = []
        if idx > 0: neighbors.append(age_groups[idx-1])
        if idx < len(age_groups)-1: neighbors.append(age_groups[idx+1])

        t1_mask = (exact_match_df[self.col_gender].str.lower() == gender.lower()) & (exact_match_df['Age_Group'] == target_group)
        t2_mask = (~t1_mask) & ((exact_match_df['Age_Group'].isin(neighbors)) | (exact_match_df['Age_Group'] == target_group))
        t3_mask = ~(t1_mask | t2_mask)

        def get_top_symptoms_for_tier(sub_df, excluded_symptoms):
            all_related = []
            for _, row in sub_df.iterrows():
                s_tokens = self._split_symptoms(row[self.col_search])
                sum_tokens = self._split_symptoms(row['Cleaned_Symptoms'])
                
                valid_sum = [t for t in sum_tokens if t in self.all_unique_symptoms]
                combined_tokens = set(s_tokens + valid_sum)

                for t in combined_tokens:
                    if t not in matched_symptoms and t not in excluded_symptoms:
                        all_related.append(t)
            
            counts = pd.Series(all_related).value_counts()
            top_list = counts.head(top_n).index.tolist()
            return top_list, set(top_list)

        tier_1_list, seen_1 = get_top_symptoms_for_tier(exact_match_df[t1_mask], set())
        tier_2_list, seen_2 = get_top_symptoms_for_tier(exact_match_df[t2_mask], seen_1)
        tier_3_list, _ = get_top_symptoms_for_tier(exact_match_df[t3_mask], seen_1.union(seen_2))

        return {
            "error": False,
            "detected_symptoms": matched_symptoms,
            "tier_1": tier_1_list,
            "tier_2": tier_2_list,
            "tier_3": tier_3_list,
            "message": "วิเคราะห์สำเร็จ"
        }

def load_and_clean_data(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found")
    
    df = pd.read_csv(file_path)
    col_search = 'search_term' 
    col_gender = next((col for col in df.columns if 'gender' in col.lower() or 'เพศ' in col), 'Gender')
    col_age = next((col for col in df.columns if 'age' in col.lower() or 'อายุ' in col), 'Age')
    col_summary = next((col for col in df.columns if 'summary' in col.lower()), None)

    if col_summary:
        df['Cleaned_Symptoms'] = df[col_summary].apply(extract_symptoms_from_json)
    else:
        df['Cleaned_Symptoms'] = ""

    df[col_gender] = df[col_gender].astype(str).str.strip().str.title()
    df[col_age] = pd.to_numeric(df[col_age].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce')
    df[col_age] = df[col_age].fillna(df[col_age].median())
    
    return df, col_gender, col_age, col_search

