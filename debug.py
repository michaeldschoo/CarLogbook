import pandas as pd
import io

with open('myDeductionExpenses.csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
csv_data = "".join(lines[4:335])
df = pd.read_csv(io.StringIO(csv_data), index_col=False)
print("Columns length:", len(df.columns))
print("Head Date:")
print(df['Date'].head(5))
print("Head Vehicle:")
print(df['Vehicle'].head(5))
