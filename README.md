# USAggregate

USAggregate is a Python package for aggregating and merging US geographic data frames.

## Installation

You can install the package using pip:

```{sh}
pip install USAggregate
```

Below is an example of package usage.

```{python}
import pandas as pd
from USAggregate import usaggregate

data_zip = pd.DataFrame({
    'zip': ['98199', '98103', '98001', '98002', '91360', '91358', '93001', '93003'],
    'value1': [1, 2, 3, 4, 5, 6, 7, 8],
    'chr1': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    })

data_city = pd.DataFrame({
        'city': ['Seattle', 'Auburn', 'Thousand Oaks', 'Ventura'],
        'state': ['WA', 'WA', 'CA', 'CA'],
        'value2': [1, 2, 3, 4],
        'chr2' : ['A', 'B', 'C', 'D']
    })

data_county = pd.DataFrame({
        'county': ['King County', 'Ventura County'],
        'state': ['Washington', 'California'],
        'value3': [5, 6],
        'chr3': ['G', 'H']
    })

    # Using the function
result1 = usaggregate([data_zip, data_city, data_county], level='state', agg_numeric='sum', agg_character='first')

# Example usage of usaggregate function
result = usaggregate([data_city, data_county], level='state')
print(result)

```

