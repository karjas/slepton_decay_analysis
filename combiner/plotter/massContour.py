import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import sys
import pprint
import math

def pColormeshPlot(fin, fout = -1, replace = False, step = 1, smooth = True, log=True ):
    '''Function for creating logarithmic colormesh from the given data. The plots are saved as .pdf in a subdirectory within the working folder.
    The function works by creating a grid of points and then assigning data to closest cell, thus allowing the function to run on unfinished data samples.

    '''

    
    if not os.path.exists(fin):
        print("Please enter a valid path")
        sys.exit(1)
    
    data = pd.read_csv(fin)

    
    req = ["m_slr","m_ne","cross"]
    if  len(set(data.columns).intersection(req)) == 3:
        x = [int(i) for i in data["m_slr"]]
        y = [int(i) for i in data["m_ne"]]
        z = data["cross"]
    
    else:
        print("Please include the columns m_slr,m_ne and cross in your file")
        sys.exit(1)

    x_max = max(x)
    x_min = min(x)
    y_max = max(y)
    y_min = min(y)
    z_max = max(z)
    z_min = min(z)
    xx, yy = np.meshgrid(np.arange(x_min, x_max+step,step), np.arange(y_min,y_max+step,step))
    
    ZZ = np.ones(xx.shape)*0
    for i in range(len(x)):
        idx = (x[i]-x_min)/step
        idy = (y[i]-y_min)/step
        ZZ[idy][idx]=max(z[i],ZZ[idy][idx])
    
    if smooth:
        B = np.array([[1,1,1],[1,0,1],[1,1,1]])*1.0/8
        ZZ = smoothen(ZZ,B)
    
    ZZ = ZZ*1000 #Scaling

    if fout == -1:
        name = fin.split("/")

        dirout = name[len(name) - 1].replace(".csv","")
        #print(fout)
        if not os.path.exists(dirout):
            os.makedirs(dirout)
        if replace:
            title = dirout
        else:
            fout = dirout+"_"
            print(fout)
         
            runid = 0
    
            while os.path.exists("{}/{}{:02d}.pdf".format(dirout,fout,runid)):
                runid += 1
            title = "{}{:02d}".format(fout,runid)
        print(title)
    fig = plt.figure(figsize=(7,7))
    ax = fig.add_subplot(111)
    if log:
        ZZ = np.ma.log10(ZZ)
    
    img = ax.pcolormesh(xx,yy,ZZ, cmap = plt.cm.get_cmap('Blues'))
    
    Mlep = np.arange(x_min,x_max)
    Mneu = Mlep - 10

    Mkin = Mlep
    
    ax.plot(Mlep,Mneu)
    ax.plot(Mlep,Mkin)

    fig.colorbar(img, ax=ax)
    ax.set_xlabel(r'$m_{\tilde{l}}$    [GeV]')
    ax.set_ylabel(r'$m_{\tilde{\chi_1^0}}$    [GeV]')
    ax.set_title(title)
    ax.set_ylim([y_min,y_max])
    plt.savefig(dirout+"/"+title+'.pdf', format='pdf')

def smoothen(A, B, cut=-6):
    '''If a point is 0, then it is replaced by the unweighted average of its neighbours'''
    BmidX = (B.shape[0]+1)/2
    BmidY = (B.shape[1]+1)/2
    maxX = A.shape[0]
    maxY = A.shape[1]

    out = np.zeros(A.shape)

    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            
            if A[i][j] == 0:
                s = 0
                for ib in range(B.shape[0]):
                    for jb in range(B.shape[1]):
                        di = ib-BmidX
                        dj = jb-BmidY
                        
                        if 0 < i + di and i + di < maxX and 0 < j + dj and j + dj < maxY:
                            s += B[ib][jb]*A[i+di][j+dj]
                
                out[i][j] = s
            else:
                out[i][j] = A[i][j]

            if out[i][j] < math.pow(10,cut):
                out[i][j] = 0  # A cut for better looking graphs
    return out    

    #print(nozeros)

if __name__ == '__main__':
        pColormeshPlot(sys.argv[1],replace = True,smooth=True, step = 5)
    

























#lol
