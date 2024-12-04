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

Users will need to manually  split any joint geographic identifiers (as seen in ACS data).

## Supported Geographic Identifier Column names
<<<<<<< HEAD
As of 1.1.12, no need to manually rename colums
=======
TRACT: Census tract 11 digit numeric code. No need to worry about missing leading 0s.

COUNTYFP: 3 digit FIPS code referring to county. No need to worry about missing leading 0s.

STATEFP: 2 digit FIPS code referring to state. No need to worry about missing leading 0s.

STATECOUNTYFP: 5 digit combined state and county FIPS code. No need to worry about missing leading 0s.

zipcode: 5 digit zip code. No need to worry about missing leading 0s or extended zip codes including a '-'. 

city: City name (e.g. 'Los Angeles').

county: County name (e.g. 'Los Angeles County')

state: Full state name OR abbreviation (e.g. 'California' OR 'CA')
>>>>>>> 936830d894219f7f5c8a2822b1e7aea034bda1a9

## Aggregation Levels Logic
'TRACT' data can be aggregated to the 'tract' (identity), 'county', or 'state' level.

'zipcode' data can be aggregated to the 'zipcode' (identity), 'city', 'county', or 'state level.

'city' data can be aggregated to the 'city' (identity), 'county', or 'state' level.

'county' data can be aggregated to the 'county' (identity), or 'state' level.

'state' data can be aggregated to the 'state' (identity) level.

## Aggregation Requirements
Census Tract: To aggregate a data frame at the 'tract' (column name 'TRACT') level up to any of the supported levels, no additional geographic information is needed in the data frame.

Zip Code: To aggregate a data frame at the 'zipcode' (column name 'zipcode') level up to any of the supported levels, no additional geographic information is needed in the data frame.

<<<<<<< HEAD
City: To aggregate a data frame at the 'city' level up to any of the supported levels, state information is needed as well.

County: To aggregate a data frame at the 'county' level, state information is needed as well.
=======
City: To aggregate a data frame at the 'city' (column name 'city') level up to any of the supported levels, state information (column names 'state', 'STATEFP', or 'STATECOUNTYFP) is needed as well.

County: To aggregate a data frame at the 'county' (column names 'county', 'COUNTYFP', or 'STATECOUNTYFP) level, state information (column names 'state', 'STATEFP', or 'STATECOUNTYFP) is needed as well.
>>>>>>> 936830d894219f7f5c8a2822b1e7aea034bda1a9


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
    'Double stack burger zip': ['98199', '98103', '98001', '98002', '91360', '91358', '93001', '93003', '98199', '98103', '98001', '98002', '91360', '91358', '93001', '93003'],
    'value1': [np,nan, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2],
    'chr1': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],
    'Year': [2010, 2010, 2010, 2010, 2010, 2010, 2010, 2010, 2011, 2011, 2011, 2011, 2011, 2011, 2011, 2011]
})

data_city = pd.DataFrame({
    'Bacon cheeseburger locations': ['Seattle', 'Auburn', 'Thousand Oaks', 'Ventura', 'Seattle', 'Auburn', 'Thousand Oaks', 'Ventura'],
    'state of the double': ['WA', 'WA', 'CA', 'CA', 'WA', 'WA', 'CA', 'CA'],
    'value2': [np.nan, '2', '3', '4', '1', '2', '3', '4'],
    'chr2': [np.nan, 'J', 'K', 'L', 'I', 'J', 'K', 'L'],
    'Date': ['1/1/2010', '1/1/2010', '1/1/2010', '1/1/2010', '1/1/2011', '1/1/2011', '1/1/2011', '1/1/2011']
})

data_county = pd.DataFrame({
    'what are those state subdivisions called': ['King County', 'Ventura County', 'King County', 'Ventura County'],
    'sTaTe name': ['Washington', 'California', 'Washington', 'California'],
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

