import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('prp_vs_trad.csv')

df['timestamp'] = pd.to_datetime(df['timestamp'])

df_traditional = df[df['method'] == 'Traditional']
df_prp = df[df['method'] == 'PRP']

plt.figure(figsize=(10, 6))

plt.plot(df_traditional['timestamp'], df_traditional['cold_start_duration'], label="Traditional Cold Start", color='blue', marker='o')

plt.plot(df_prp['timestamp'], df_prp['cold_start_duration'], label="PRP Algorithm", color='green', marker='s')

plt.title('Cold Start Duration Comparison: PRP vs. Traditional Method')
plt.xlabel('Time')
plt.ylabel('Cold Start Duration (ms)')
plt.legend()

plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
