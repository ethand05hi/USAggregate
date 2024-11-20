import pandas as pd
import pkg_resources

def load_zip_relations():
    """
    Load the zip_relations (zipcodes.csv) file from the data folder.
    """
    filepath = pkg_resources.resource_filename('USAggregate', 'data/zipcodes.csv')
    return pd.read_csv(filepath, dtype=str)

def usaggregate(data, level, 
                agg_numeric_geo='mean', agg_character_geo='first', 
                col_specific_agg_num_geo=None, col_specific_agg_chr_geo=None, 
                time_period=None):
    """
    A function to aggregate a list of pandas DataFrames by geography and time periods.
    Dynamically infers missing geographic columns using zip_relations.

    Parameters:
    - data: list of pandas DataFrames to aggregate.
    - level: level of geographic aggregation ('zip', 'city', 'county', 'state').
    - agg_numeric_geo: default numeric aggregation method for numeric columns during geographic aggregation.
    - agg_character_geo: default character aggregation method for character columns during geographic aggregation.
    - col_specific_agg_num_geo: dictionary specifying numeric aggregation methods for specific columns.
    - col_specific_agg_chr_geo: dictionary specifying character aggregation methods for specific columns.
    - time_period: time period for grouping ('day', 'week', 'month', 'quarter', 'year').

    Returns:
    - Aggregated DataFrame.
    """
    zip_relations = load_zip_relations()  # Load zip_relations file
    col_specific_agg_num_geo = col_specific_agg_num_geo or {}
    col_specific_agg_chr_geo = col_specific_agg_chr_geo or {}

    state_map = dict(zip(zip_relations['ST'], zip_relations['state']))

    def preprocess_zipcode_column(df):
        """
        Ensure the 'zipcode' column has 5-character strings, taking only the part before '-'.
        """
        if 'zipcode' in df.columns:
            # Ensure string type
            df['zipcode'] = df['zipcode'].astype(str)
            # Take only part before '-'
            df['zipcode'] = df['zipcode'].str.split('-').str[0]
            # Add leading zeros to ensure 5 characters
            df['zipcode'] = df['zipcode'].str.zfill(5)
        return df

    def preprocess_countyfp_column(df):
        """
        Ensure 'COUNTYFP' column is a string of 5 characters and merge 'state' and 'county' if missing.
        """
        if 'COUNTYFP' in df.columns:
            # Ensure string type
            df['COUNTYFP'] = df['COUNTYFP'].astype(str)
            # Add leading zeros to ensure 5 characters
            df['COUNTYFP'] = df['COUNTYFP'].str.zfill(5)
            # Merge 'state' and 'county' if missing
            if 'state' not in df.columns and 'county' not in df.columns:
                df = df.merge(zip_relations[['state', 'county']], on='COUNTYFP', how='left')
        return df

    def preprocess_numeric_columns(df):
        excluded_cols = {'zipcode', 'city', 'county', 'state', 'COUNTYFP', 'Date'}
        for col in df.columns:
            if col not in excluded_cols:
                df[col] = pd.to_numeric(df[col], errors='ignore')
        return df

    def preprocess_state_column(df):
        if 'state' in df.columns:
            if df['state'].str.len().eq(2).all():
                df['state'] = df['state'].map(state_map).fillna(df['state'])
        return df

    def preprocess_date_column(df, time_period):
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            if time_period == 'day':
                df['Time_Group'] = df['Date']
            elif time_period == 'week':
                df['Time_Group'] = df['Date'].dt.to_period('W').apply(lambda r: r.start_time)
            elif time_period == 'month':
                df['Time_Group'] = df['Date'].dt.to_period('M').apply(lambda r: r.start_time)
            elif time_period == 'quarter':
                df['Time_Group'] = df['Date'].dt.to_period('Q').apply(lambda r: r.start_time)
            elif time_period == 'year':
                df['Time_Group'] = df['Date'].dt.year
        elif 'Year' in df.columns:
            df['Time_Group'] = df['Year']
        else:
            raise KeyError("DataFrame must have either 'Date' or 'Year' column for time-based aggregation.")
        return df

    def infer_missing_geography(df, target_level):
        if target_level == 'county':
            if 'county' not in df.columns:
                if 'zipcode' in df.columns:
                    df = df.merge(zip_relations[['zipcode', 'county', 'state']], on='zipcode', how='left')
                elif 'city' in df.columns and 'state' in df.columns:
                    df = df.merge(zip_relations[['city', 'state', 'county']].drop_duplicates(), 
                                  on=['city', 'state'], how='left')
                else:
                    raise KeyError("To aggregate by 'county', the DataFrame must have either 'county' and 'state', "
                                   "'zipcode', or 'city' and 'state'.")
        elif target_level == 'city':
            if 'city' not in df.columns:
                if 'zipcode' in df.columns:
                    df = df.merge(zip_relations[['zipcode', 'city', 'state']], on='zipcode', how='left')
                else:
                    raise KeyError("To aggregate by 'city', the DataFrame must have either 'city' and 'state' or 'zipcode'.")
        elif target_level == 'state':
            if 'state' not in df.columns:
                if 'zipcode' in df.columns:
                    df = df.merge(zip_relations[['zipcode', 'state']], on='zipcode', how='left')
                else:
                    raise KeyError("To aggregate by 'state', the DataFrame must have either 'state' or 'zipcode'.")
        return df

    def map_geo_hierarchy(df, target_level):
        df = infer_missing_geography(df, target_level)
        if target_level == 'city':
            df['GEO_ID'] = df['city'] + ', ' + df['state']
        elif target_level == 'county':
            df['GEO_ID'] = df['county'] + ', ' + df['state']
        elif target_level == 'state':
            df['GEO_ID'] = df['state']
        else:
            df['GEO_ID'] = df['zipcode']
        if df['GEO_ID'].isnull().any():
            raise ValueError("Failed to map all rows to the target geographic level.")
        return df

    def aggregate_columns(df, group_cols, numeric_agg, char_agg):
        numeric_cols = df.select_dtypes(include=['number']).columns.difference(['Time_Group'])
        char_cols = df.select_dtypes(include=['object']).columns.difference(group_cols + ['Time_Group'])
        agg_dict = {col: numeric_agg.get(col, agg_numeric_geo) for col in numeric_cols}
        agg_dict.update({col: char_agg.get(col, agg_character_geo) for col in char_cols})
        df = df.dropna(subset=numeric_cols.union(char_cols))
        grouped = df.groupby(group_cols).agg(agg_dict).reset_index()
        return grouped

    aggregated_data = []
    for df in data:
        df = preprocess_zipcode_column(df)
        df = preprocess_countyfp_column(df)
        df = preprocess_numeric_columns(df)
        df = preprocess_state_column(df)
        df = preprocess_date_column(df, time_period)
        df = map_geo_hierarchy(df, level)
        group_cols = ['Time_Group', 'GEO_ID']
        df = aggregate_columns(df, group_cols, col_specific_agg_num_geo, col_specific_agg_chr_geo)
        aggregated_data.append(df)

    result = aggregated_data[0]
    for df in aggregated_data[1:]:
        result = result.merge(df, how='outer', on=['Time_Group', 'GEO_ID'], suffixes=('', '_dup'))
        result = result.loc[:, ~result.columns.str.endswith('_dup')]

    columns_to_drop = ['ST', 'state', 'county', 'zipcode', 'Date', 'city']
    result.drop(columns=[col for col in columns_to_drop if col in result.columns], inplace=True, errors='ignore')
    return result