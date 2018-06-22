import pandas as pd
import numpy as np
import random as rnd

df = pd.DataFrame(columns = ['m_slr','m_neu','cross'])

X,Y = np.mgrid[slice(1,10,1),slice(1,10,1)]

xMax = 100
yMax = 50

i = 0
for x in range(0, xMax):
    for y in range(0,yMax):
        cs = rnd.uniform(1.5,2.5)
        rndx = rnd.uniform(0,xMax)
        rndy = rnd.uniform(0,yMax)
        df.loc[i] = [rndx,rndy,cs]
        i += 1

print(df)

df.to_csv('exampleData2.csv')
