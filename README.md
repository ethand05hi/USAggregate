# USAggregate

USAggregate is a Python package for aggregating and merging US relational data frames. Current version is 1.1.11.

## Example Use Case

Merging demographic data at the zip code level with ice cream sales data at the city level to measure the correlation between demographics and ice cream sales at the county level.

## Installation

You can install the package using pip:

```{sh}
pip install USAggregate
```
## Use Notes

Users will need to manually change geographic identifier columns as well as split any joint geographic identifiers (as seen in ACS data).

Below is a list of accepted geographic identifier column names followed by a description.

## Supported Geographic Identifier Column names
As of 1.1.12, no need to manually rename colums

## Aggregation Levels Logic
'TRACT' data can be aggregated to the 'tract' (identity), 'county', or 'state' level.

'zipcode' data can be aggregated to the 'zipcode' (identity), 'city', 'county', or 'state level.

'city' data can be aggregated to the 'city' (identity), 'county', or 'state' level.

'county' data can be aggregated to the 'county' (identity), or 'state' level.

'state' data can be aggregated to the 'state' (identity) level.

## Aggregation Requirements
Census Tract: To aggregate a data frame at the 'tract' (column name 'TRACT') level up to any of the supported levels, no additional geographic information is needed in the data frame.

Zip Code: To aggregate a data frame at the 'zipcode' (column name 'zipcode') level up to any of the supported levels, no additional geographic information is needed in the data frame.

City: To aggregate a data frame at the 'city' (column name 'city') level up to any of the supported levels, state information (column names 'state', 'STATEFP', or 'STATECOUNTYFP) is needed as well.

County: To aggregate a data frame at the 'county' (column names 'county', 'COUNTYFP', or 'STATECOUNTYFP) level, state information (column names 'state', 'STATEFP', or 'STATECOUNTYFP) is needed as well.

## Supported Aggregation Methods
Numeric: 'mean', 'median', 'mode', 'sum', 'first', 'last', 'min', 'max'.

String: 'first', 'last', 'mode'.

## Additional Notes on Time Grouping
If you wish to group by time, set the 'time_period' argument to either 'year', 'quarter', 'month', 'week', or 'day'. If you have a year identifier in your data, set that column name to 'Year'. If your time identifier column is in the date format, set that column name to 'Date'.

Below is an example of package usage.

```{python}
import pandas as pd
import numpy as np
from USAggregate import usaggregate

data_zip = pd.DataFrame({
    'zipcode': ['98199', '98103', '98001', '98002', '91360', '91358', '93001', '93003', '98199', '98103', '98001', '98002', '91360', '91358', '93001', '93003'],
    'value1': [np,nan, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2],
    'chr1': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
    'Year': [2010, 2010, 2010, 2010, 2010, 2010, 2010, 2010, 2011, 2011, 2011, 2011, 2011, 2011, 2011, 2011]
})

data_city = pd.DataFrame({
    'city': ['Seattle', 'Auburn', 'Thousand Oaks', 'Ventura', 'Seattle', 'Auburn', 'Thousand Oaks', 'Ventura'],
    'state': ['WA', 'WA', 'CA', 'CA', 'WA', 'WA', 'CA', 'CA'],
    'value2': [np.nan, '2', '3', '4', '1', '2', '3', '4'],
    'chr2': [np.nan, 'J', 'K', 'L', 'I', 'J', 'K', 'L'],
    'Date': ['1/1/2010', '1/1/2010', '1/1/2010', '1/1/2010', '1/1/2011', '1/1/2011', '1/1/2011', '1/1/2011']
})

data_county = pd.DataFrame({
    'county': ['King County', 'Ventura County', 'King County', 'Ventura County'],
    'state': ['Washington', 'California', 'Washington', 'California'],
    'value3': [5, 6, 5, 6],
    'chr3': ['M', 'N', 'M', 'N'],
    'Year': ['2010', '2010', '2011', '2011']
})

df = usaggregate(
    data=[data_city, data_zip, data_county],
    level='county',
    agg_numeric_geo='sum',
    agg_character_geo='first',
    col_specific_agg_num_geo={'value2': 'mean'},
    col_specific_agg_chr_geo={'chr1': 'last'},
    time_period='year'
)

print(df)

```

