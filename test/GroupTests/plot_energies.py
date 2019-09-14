import numpy as np
import matplotlib.pyplot as plt
from g_library import *

file = 'HeH_energies.dat'
data,klist = read_datafile(file)
kdim=len(klist)
datadim = len(data[klist[0]])
print(data,klist)

#xmin = 1
#xmax = datadim
#ymin = 0
#ymax = +800

#
plt.title('HeH+ energy with RyRz (d=2) vs He-H distance ')

x = data[klist[0]]
y1 = data[klist[1]]
y2 = data[klist[2]]

index=np.arange(datadim)
yzero=0*index
p = data[klist[1]]

plt.plot(x,y1,lw=1,color='black')
plt.plot(x,y1,'ro',color='green')

plt.plot(x,y2,lw=1,color='black')
plt.plot(x,y2,'ro',color='red')

plt.xlabel('Distance (Ang.)')
plt.ylabel('     Energy (Hartree) ')

#plt.title(klist[0])

plt.show()

