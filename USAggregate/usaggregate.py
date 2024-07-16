import pandas as pd
import pkg_resources
import os

#For version 1.0.5, add panel capabilities + fuzzy matching for column names

def usaggregate(data, level, agg_numeric='mean', agg_character='first'):
    if not isinstance(data, list) or len(data) < 1:
        raise ValueError("Data must be a list of one or more pandas DataFrames.")
    
    supported_levels = ['zip', 'city', 'county', 'state']
    if level not in supported_levels:
        raise ValueError(f"Level must be one of {supported_levels}.")
    
    zipcodes_path = pkg_resources.resource_filename('USAggregate', 'data/zipcodes.csv')
    zip_relations = pd.read_csv(zipcodes_path, dtype=str)
    
    level_hierarchy = {'zip': 0, 'city': 1, 'county': 2, 'state': 3}
    
    # Create a dictionary to map state abbreviations to full state names
    state_map = {row['ST']: row['state'] for _, row in zip_relations.iterrows()}
    state_map.update({row['state']: row['state'] for _, row in zip_relations.iterrows()})

    # Create a unique mapping from city, state to county, state
    zip_relations['state'] = zip_relations['ST'].map(state_map)
    city_to_county = zip_relations.drop_duplicates(subset=['city', 'state']).set_index(['city', 'state'])[['county']]
    print("City to County Mapping:\n", city_to_county.head())

    def detect_geo_columns(df):
        for col in df.columns:
            if 'zip' in col.lower():
                return 'zip'
            if 'city' in col.lower():
                return 'city'
            if 'state' in col.lower():
                return 'state'
            if 'county' in col.lower():
                return 'county'
        return None

    def convert_state_abbreviations(df):
        if 'state' in df.columns:
            df['state'] = df['state'].map(state_map).fillna(df['state'])
        return df

    def get_geo_id(df, current_level, target_level):
        if current_level == 'zip' and target_level == 'city':
            df = df.merge(zip_relations[['zipcode', 'city', 'ST']], left_on='zip', right_on='zipcode', how='left')
            df['GEO_ID'] = df.apply(lambda x: f"{x['city']}, {state_map[x['ST']]}" if pd.notna(x['city']) and pd.notna(x['ST']) else pd.NA, axis=1)
            df.drop(columns=['zipcode', 'city', 'ST'], inplace=True)
        elif current_level == 'zip' and target_level == 'county':
            df = df.merge(zip_relations[['zipcode', 'county', 'ST']], left_on='zip', right_on='zipcode', how='left')
            df['GEO_ID'] = df.apply(lambda x: f"{x['county']}, {state_map[x['ST']]}" if pd.notna(x['county']) and pd.notna(x['ST']) else pd.NA, axis=1)
            df.drop(columns=['zipcode', 'county', 'ST'], inplace=True)
        elif current_level == 'zip' and target_level == 'state':
            df = df.merge(zip_relations[['zipcode', 'ST']], left_on='zip', right_on='zipcode', how='left')
            df['GEO_ID'] = df['ST'].map(state_map).where(pd.notna(df['ST']), pd.NA)
            df.drop(columns=['zipcode', 'ST'], inplace=True)
        elif current_level == 'city' and target_level == 'county':
            print("Before Join:\n", df.head())
            df = df.join(city_to_county, on=['city', 'state'], how='left')
            print("After Join:\n", df.head())
            df['GEO_ID'] = df.apply(lambda x: f"{x['county']}, {x['state']}" if pd.notna(x['county']) and pd.notna(x['state']) else pd.NA, axis=1)
            print("With GEO_ID:\n", df.head())
            df.drop(columns=['city', 'state', 'county'], inplace=True)
        elif current_level == 'city' and target_level == 'state':
            df['GEO_ID'] = df['state'].map(state_map)  # Ensure full state name is used
            df.drop(columns=['city', 'state'], inplace=True)
        elif current_level == 'county' and target_level == 'state':
            df['GEO_ID'] = df['state'].map(state_map)  # Ensure full state name is used
            df.drop(columns=['county', 'state'], inplace=True)
        else:
            df['GEO_ID'] = df[current_level]
            if current_level == 'county':
                df['GEO_ID'] = df.apply(lambda x: f"{x['county']}, {x['state']}" if pd.notna(x['county']) and pd.notna(x['state']) else pd.NA, axis=1)
            elif current_level == 'city':
                df['GEO_ID'] = df.apply(lambda x: f"{x['city']}, {x['state']}" if pd.notna(x['city']) and pd.notna(x['state']) else pd.NA, axis=1)
        return df

    def aggregate_dataframe(df, level):
        current_level = detect_geo_columns(df)
        if current_level is None:
            raise ValueError("No geographic column detected in the DataFrame.")
        
        if level_hierarchy[current_level] > level_hierarchy[level]:
            raise ValueError(f"Cannot aggregate from {current_level} to {level}. Please choose a higher level of aggregation.")
        
        df = convert_state_abbreviations(df)
        
        df = get_geo_id(df, current_level, level)
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
        char_cols = df.select_dtypes(include=['object']).columns.difference(['GEO_ID'])
        
        if agg_numeric == 'mean':
            numeric_agg = df.groupby('GEO_ID')[numeric_cols].mean()
        elif agg_numeric == 'median':
            numeric_agg = df.groupby('GEO_ID')[numeric_cols].median()
        elif agg_numeric == 'mode':
            numeric_agg = df.groupby('GEO_ID')[numeric_cols].agg(lambda x: x.mode()[0] if not x.mode().empty else pd.NA)
        elif agg_numeric == 'sum':
            numeric_agg = df.groupby('GEO_ID')[numeric_cols].sum()
        elif agg_numeric == 'first':
            numeric_agg = df.groupby('GEO_ID')[numeric_cols].first()
        elif agg_numeric == 'last':
            numeric_agg = df.groupby('GEO_ID')[numeric_cols].last()
        else:
            raise ValueError("agg_numeric must be 'mean', 'median', 'mode', 'sum', 'first', or 'last'.")
        
        if agg_character == 'first':
            char_agg = df.groupby('GEO_ID')[char_cols].first()
        elif agg_character == 'last':
            char_agg = df.groupby('GEO_ID')[char_cols].last()
        elif agg_character == 'mode':
            char_agg = df.groupby('GEO_ID')[char_cols].agg(lambda x: x.mode()[0] if not x.mode().empty else pd.NA)
        else:
            raise ValueError("agg_character must be 'first', 'last', or 'mode'.")
        
        return numeric_agg.join(char_agg).reset_index()

    # Aggregate each dataframe and store the results
    aggregated_data = []
    for df in data:
        aggregated_df = aggregate_dataframe(df, level)
        aggregated_data.append(aggregated_df)
        print(f"Aggregated DataFrame {len(aggregated_data)}:\n", aggregated_df)
    
    # Merge the aggregated dataframes
    result = aggregated_data[0]
    for df in aggregated_data[1:]:
        result = result.merge(df, on='GEO_ID', how='outer', suffixes=('', '_dup'))
        # Remove duplicate columns after merge
        result = result.loc[:, ~result.columns.str.endswith('_dup')]

    # Drop original geographic identifier columns
    geo_columns_to_drop = ['zip', 'city', 'state', 'county']
    result.drop(columns=[col for col in geo_columns_to_drop if col in result.columns], inplace=True)
    
    # Drop rows with NaN GEO_ID
    result.dropna(subset=['GEO_ID'], inplace=True)
    
    return result