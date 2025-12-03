import pandas as pd
import numpy as np

grouped = df.groupby('workArea').agg({
    'workArea': 'count',  # count of facilities
    'priority': 'sum'      # sum of priority
}).rename(columns={'workArea': 'Number of Facilities per Work Area', 
                   'priority': 'priority_sum'})

grouped['Totally Priority per Work Area, Adjusted for Size'] = (
    grouped['priority_sum'] / np.sqrt(grouped['Number of Facilities per Work Area'])
)

result = (grouped.drop(columns=['priority_sum'])
          .sort_values('Totally Priority per Work Area, Adjusted for Size')
          .reset_index())
