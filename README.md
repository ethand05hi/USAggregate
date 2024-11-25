# USAggregate

USAggregate is a Python package for aggregating and merging US relational data frames. Current version is 1.1.1.

## Example Use Case

Merging demographic data at the zip code level with ice cream sales data at the city level to measure the correlation between demographics and ice cream sales at the county level.

## Installation

You can install the package using pip:

```{sh}
pip install USAggregate
```
## Use Notes

Users will need to manually change geographic identifier columns to 'tract', 'zipcode', 'city', 'county', 'COUNTYFP' or 'state'. Tracts can be aggregated to further levels without additional info. Zip codes can be aggregated to further levels without additional info. Data at the city our county levels will need state information as well due to duplicate names. If each data frame you wish to aggregate has a year identifier and would like to group by year, name the column 'Year'. If you would like to group by other timeframes (day, week, month, and quarter are available options) label your columns 'Date'. In this version, users can also specify specific columns they would like to be aggregated using a method differing from the global option set. 

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

