import pandas as pd
import numpy as np

# Wyznaczenie funkcji opisującej zmęczenie
df = pd.read_csv('mock_data.csv')

coeffs = np.polyfit(df['Day_progress'], df['Yawns_increase'], 2)

polynomial = np.poly1d(coeffs)
print(polynomial)