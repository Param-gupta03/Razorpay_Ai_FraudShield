import pandas as pd
import numpy as np
import gc

class FeaturePipeline:
    def __init__(self):
        self.categorical_cols = []
        self.categories = {}
        self.frequency_maps = {}
        self.fitted = False
        
    def fit(self, train_df):
        """
        Learns parameters (category mappings, frequency encoding maps) from the training set.
        """
        print("Fitting feature pipeline on training data...")
        
        # 1. Identify categorical columns
        # Object and category types, and M columns, card4, card6, ProductCD, DeviceType, DeviceInfo
        # Let's check columns that are categorical
        cols_to_check = train_df.columns.tolist()
        for col in cols_to_check:
            if col in ['TransactionID', 'isFraud', 'TransactionDT']:
                continue
            
            is_cat = (
                isinstance(train_df[col].dtype, pd.CategoricalDtype) or
                pd.api.types.is_string_dtype(train_df[col]) or
                col in ['ProductCD', 'card4', 'card6', 'DeviceType', 'DeviceInfo'] or
                col.startswith('M')
            )
            if is_cat:
                self.categorical_cols.append(col)
                # Learn category values (fill NaNs with 'MISSING' first)
                unique_vals = train_df[col].astype(str).fillna('MISSING').unique().tolist()
                if 'MISSING' not in unique_vals:
                    unique_vals.append('MISSING')
                self.categories[col] = unique_vals
                
        print(f"Identified {len(self.categorical_cols)} categorical columns.")
        
        # 2. Learn frequency mappings for high-cardinality features to avoid target leakage
        cols_for_frequency = [
            'card1', 'card2', 'card3', 'card5', 'addr1', 'addr2', 
            'P_emaildomain', 'R_emaildomain', 'DeviceInfo'
        ]
        # Also let's learn frequency of card1_card2 compound feature
        temp_card1_card2 = train_df['card1'].astype(str) + "_" + train_df['card2'].astype(str)
        self.frequency_maps['card1_card2'] = temp_card1_card2.value_counts().to_dict()
        
        for col in cols_for_frequency:
            if col in train_df.columns:
                self.frequency_maps[col] = train_df[col].value_counts(dropna=False).to_dict()
                
        self.fitted = True
        print("Fitting complete.")
        return self

    def transform(self, df):
        """
        Applies engineered features, imputations, and mappings to a dataset.
        """
        if not self.fitted:
            raise ValueError("Pipeline must be fitted before transform can be called.")
            
        print("Transforming dataset...")
        res_df = df.copy()
        
        # 1. Chronological Time Features
        # TransactionDT is in seconds.
        # Hour of day: 3600 seconds in an hour, 24 hours in a day
        res_df['hour'] = (res_df['TransactionDT'] // 3600) % 24
        # Day of week: 86400 seconds in a day, 7 days in a week
        res_df['day_of_week'] = (res_df['TransactionDT'] // 86400) % 7
        
        # 2. TransactionAmt features
        res_df['TransactionAmt_log'] = np.log1p(res_df['TransactionAmt'])
        res_df['TransactionAmt_decimal'] = res_df['TransactionAmt'] - res_df['TransactionAmt'].astype(int)
        
        # 3. Missingness Counts (per-row null counts)
        res_df['nulls_count'] = res_df.isnull().sum(axis=1)
        
        identity_cols = [c for c in res_df.columns if c.startswith('id_') or c in ['DeviceType', 'DeviceInfo']]
        if len(identity_cols) > 0:
            res_df['identity_nulls_count'] = res_df[identity_cols].isnull().sum(axis=1)
        else:
            res_df['identity_nulls_count'] = 0
            
        # 4. Email Matching Features
        if 'P_emaildomain' in res_df.columns and 'R_emaildomain' in res_df.columns:
            p_email = res_df['P_emaildomain'].astype(object).fillna('MISSING').astype(str)
            r_email = res_df['R_emaildomain'].astype(object).fillna('MISSING').astype(str)
            
            # 1: match, 0: mismatch, -1: missing either
            res_df['email_match'] = np.where(
                (p_email == 'nan') | (r_email == 'nan') | (p_email == 'None') | (r_email == 'None') | (p_email == 'MISSING') | (r_email == 'MISSING'),
                -1,
                np.where(p_email == r_email, 1, 0)
            )
            
            # Simple domain grouping (extracting suffix/provider)
            res_df['P_emaildomain_bin'] = p_email.apply(lambda x: x.split('.')[0] if '.' in x else x)
            res_df['R_emaildomain_bin'] = r_email.apply(lambda x: x.split('.')[0] if '.' in x else x)
        else:
            res_df['email_match'] = -1
            res_df['P_emaildomain_bin'] = 'MISSING'
            res_df['R_emaildomain_bin'] = 'MISSING'
            
        # 5. Screen Resolution features from id_33 (e.g. "1920x1080")
        if 'id_33' in res_df.columns:
            res_str = res_df['id_33'].astype(object).fillna('MISSING').astype(str)
            split_res = res_str.str.split('x', expand=True)
            
            res_df['screen_width'] = pd.to_numeric(split_res[0], errors='coerce')
            if 1 in split_res.columns:
                res_df['screen_height'] = pd.to_numeric(split_res[1], errors='coerce')
            else:
                res_df['screen_height'] = np.nan
            res_df['screen_area'] = res_df['screen_width'] * res_df['screen_height']
            res_df['screen_aspect_ratio'] = res_df['screen_width'] / res_df['screen_height']
        else:
            res_df['screen_width'] = np.nan
            res_df['screen_height'] = np.nan
            res_df['screen_area'] = np.nan
            res_df['screen_aspect_ratio'] = np.nan
            
        # 6. Device and OS features from id_30 (OS) and id_31 (browser)
        if 'id_30' in res_df.columns:
            os_str = res_df['id_30'].astype(object).fillna('MISSING').astype(str).str.lower()
            
            # Categorize OS
            res_df['os_name'] = np.where(os_str.str.contains('windows'), 'windows',
                                np.where(os_str.str.contains('ios'), 'ios',
                                np.where(os_str.str.contains('android'), 'android',
                                np.where(os_str.str.contains('mac'), 'mac',
                                np.where(os_str.str.contains('linux'), 'linux', 'other OS')))))
        else:
            res_df['os_name'] = 'MISSING'
            
        if 'id_31' in res_df.columns:
            browser_str = res_df['id_31'].astype(object).fillna('MISSING').astype(str).str.lower()
            
            # Categorize Browser
            res_df['browser_name'] = np.where(browser_str.str.contains('chrome'), 'chrome',
                                    np.where(browser_str.str.contains('safari'), 'safari',
                                    np.where(browser_str.str.contains('firefox'), 'firefox',
                                    np.where(browser_str.str.contains('edge'), 'edge',
                                    np.where(browser_str.str.contains('samsung'), 'samsung',
                                    np.where(browser_str.str.contains('opera'), 'opera',
                                    np.where(browser_str.str.contains('ie'), 'ie', 'other browser')))))))
        else:
            res_df['browser_name'] = 'MISSING'
            
        # 7. Card features (frequency encoding mapping from fit)
        # Create card1_card2 compound column
        card1_card2_col = res_df['card1'].astype(str) + "_" + res_df['card2'].astype(str)
        res_df['card1_card2_count'] = card1_card2_col.map(self.frequency_maps['card1_card2']).fillna(0)
        
        cols_for_frequency = [
            'card1', 'card2', 'card3', 'card5', 'addr1', 'addr2', 
            'P_emaildomain', 'R_emaildomain', 'DeviceInfo'
        ]
        for col in cols_for_frequency:
            if col in res_df.columns:
                res_df[f"{col}_count"] = res_df[col].map(self.frequency_maps.get(col, {})).fillna(0)
                
        # 8. Handling Categorical Missing Values & Converting to Pandas Category Type
        # Ensure new engineered categoricals are added to the list and categories learned
        extra_cats = ['os_name', 'browser_name', 'P_emaildomain_bin', 'R_emaildomain_bin']
        for c in extra_cats:
            if c not in self.categorical_cols:
                self.categorical_cols.append(c)
                # Learn unique categories on the fly from fit mapping or default list
                if c not in self.categories:
                    self.categories[c] = list(res_df[c].astype(str).unique())
        
        # Standardize categorical values and convert type
        for col in self.categorical_cols:
            if col in res_df.columns:
                # Convert to string and fill NaNs
                res_df[col] = res_df[col].astype(str).fillna('MISSING')
                # Map unknown values to 'MISSING'
                valid_categories = self.categories.get(col, ['MISSING'])
                res_df[col] = np.where(res_df[col].isin(valid_categories), res_df[col], 'MISSING')
                # Set as category
                res_df[col] = pd.Categorical(res_df[col], categories=valid_categories)
                
        # Keep track of generated features
        print(f"Transformation complete. DataFrame shape: {res_df.shape}")
        return res_df
