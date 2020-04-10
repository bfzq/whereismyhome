#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(style="whitegrid")
rs = np.random.RandomState(365)
values = rs.randn(365, 5).cumsum(axis=0)
dates = pd.date_range("1 1 2016", periods=365, freq="D")
data = pd.DataFrame(values, dates, columns=["A", "B", "C", "D", "E"])
data = data.rolling(7).mean()

values1=((2,2,5),(7,5,6),(3,4,1))
date_list = [
    datetime(2018, 10, 1),
    datetime(2018, 10, 2),
    datetime(2018, 10, 5),
]
data1 = pd.DataFrame(values1, date_list, columns=["A", "B", "C"])
sns.lineplot(data=data1, palette="tab10", linewidth=2.5)
plt.show()
