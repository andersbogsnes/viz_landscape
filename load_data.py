import pandas as pd
import numpy as np

def load_data():
    df = pd.read_csv('./data/crime.csv', encoding='latin-1')

    df['OCCURRED_ON_DATE'] = pd.to_datetime(df.OCCURRED_ON_DATE)
    df['DAY_OF_WEEK'] = pd.Categorical(df.DAY_OF_WEEK, 
                                       categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], 
                                       ordered=True)
    df['SHOOTING'] = np.where(df.SHOOTING == 'Y', 1, 0)
    return df