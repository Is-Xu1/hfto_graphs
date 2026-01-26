import pandas as pd

data = pd.read_csv("UofU 712-VS08-011_BHA 14 - output data.csv", skiprows=35)
data["DateTime"] = pd.to_datetime(data["DateTime"], format="%Y/%m/%d %H:%M:%S.%f")
data["Timeframe"] = (data["DateTime"].shift(-1) - data["DateTime"]\
                     ).where((data["Surface_GC_OnBottom(bool)"] == 1), pd.Timedelta(0))
total_timedelta = data["Timeframe"].sum()
print(total_timedelta)