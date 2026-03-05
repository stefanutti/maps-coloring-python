import pandas as pd
from statsmodels.tsa.api import VAR

data = pd.read_csv("example_var_data.csv", index_col=0, parse_dates=True)

model = VAR(data)
results = model.fit(maxlags=5)

print(results.summary())
forecast = results.forecast(data.values[-5:], steps=10)

print(forecast)
