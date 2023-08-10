import numpy as np
import pandas as pd
from math import *    #only need the sqrt funtion to calculate distance

# default_X = np.array([0,0,6.25,8.75,3.25])           #default axis x of id 3,4,5,6,8
# default_Y = np.array([0.25,2.25,1.25,0.25,1.25])     #default axis y of id 3,4,5,6,8

default_X = np.array([0,0,6.25,8.75])           #default axis x of id 3,4,5,6
default_Y = np.array([0.25,2.25,1.25,0.25])     #default axis y of id 3,4,5,6
#--------------------------------value of all known-points------------------------------
Var = np.array([34.43, 22.03, 28.76, 24.78])    #this is default-type value of all known-points
#---------------------------------------------------------------------------------------

one_point_X = 3.25
one_point_Y = 1.25

class Kriging:
   #--------------------------------resolution---------------------------------------
   resolution = 100 
   resolutionX = 100
   resolutionY = 80
   #---------------------------------------------------------------------------------

   #----------------------------------X,Y--------------------------------------------
   default_X = np.array([0,0,6.25,8.75])           #default axis x of id 3,4,5,6
   default_Y = np.array([0.25,2.25,1.25,0.25])     #default axis y of id 3,4,5,6
   #---------------------------------------------------------------------------------

   #--------------------------------value of all known-points------------------------------
   Var = np.array([34.43, 22.03, 28.76, 24.78])    #this is default-type value of all known-points
   #---------------------------------------------------------------------------------------


   #using the spherical variogram

   nugget = 2.5
   sill = 7.5
   rang = 10

   def __init__(self, resolutionX, resolutionY, arrayVar, arrayX, arrayY):      
      self.resolutionX = resolutionX
      self.resolutionY = resolutionY
      self.default_X = np.array(arrayX)
      self.default_Y = np.array(arrayY)
      self.Var = np.array(arrayVar)
      print("SELF>VARRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
      print(self.Var)
   def semivariance(self,h):
      nug = self.nugget 
      sill = self.sill 
      ran = self.rang
      sv = nug + sill*(3/2*h/ran-0.5*(h/ran)**3)
      if sv.shape[0] > 1:
         onescol = np.ones(sv.shape[0])         #shape[0] is number of rows, shape[1] is number of coloums
         sv = np.insert(sv, sv.shape[1], onescol, axis=1)
         onesrow = np.ones(sv.shape[1])
         sv = np.insert(sv, sv.shape[0], onesrow, axis=0)
         sv[sv.shape[0]-1][sv.shape[1]-1] = 0  # change number at the corner at the end of the matrix to 0
      else:
         onescol = np.ones(sv.shape[0])
         sv = np.insert(sv, sv.shape[1], onescol, axis=1)
         sv = sv.transpose()       #vì cái sv đang ở dạng ma trận ngang 1 hàng, mình đưa về ma trận dọc 1 cột 
      return sv


   def distancematrix(self,X,Y):   #distance matrix of known-points
      #X is list of all x-axis points, Y is list of all coresponding x-axis points
      templist = []
      for i,j in zip(X,Y):
         for e,d in zip(X,Y):
            dist = sqrt(((i-e)**2+(j-d)**2))
            templist.append(dist)
      distancemat = np.array([templist[x:x+len(X)] for x in range(0, len(templist), len(X))])
      return distancemat


   def distancetoU(self,X1,Y1,X2,Y2):       #distance to Unknown point 
      #X1,Y1 is x axis and y axis of unknown point, X2 is list of all x-axis known-points, Y2 is corespond
      lst = []
      for k,l in zip(X2,Y2):
         dist = sqrt(((X1-k)**2)+(Y1-l)**2)
         lst.append(dist)
      uknown = np.array([lst])
      return uknown


   def OK(self, uknownX, uknownY):
      Variable = self.Var
      datax=self.default_X
      datay=self.default_Y
      #datax, datay are (x,y) of all points that we have
      #uknownX and uknownY are the (x,y) of the unknown point
      #Variable hình như là value của các điểm
      Var1 = np.reshape(Variable, (Variable.shape[0],1))
      Var1 = Variable.transpose()
      matdist_N = self.distancematrix(datax, datay)
      matdist_U = self.distancetoU(uknownX, uknownY, datax, datay)
      N_SV = self.semivariance(matdist_N)
      U_SV = self.semivariance(matdist_U)
      inv_N_SV = np.linalg.inv(N_SV)         #ma trận nghịch đảo của cái ma trận lớn
      Weights = np.matmul(inv_N_SV,U_SV)    #nhân ma trận nghịch đảo với cái ma trận 1 cột
      Weights = np.delete(Weights, Weights.shape[0]-1, 0)   
      Estimation = np.dot(Var1, Weights) 
      return Estimation[0] 


   def interpolation(self):
      Variable = self.Var
      ResolutionX = self.resolutionX
      ResolutionY = self.resolutionY
      X_mesh = np.linspace(0, 9, ResolutionX)   
      Y_mesh = np.linspace(0, 4, ResolutionY)    
      XX, YY = np.meshgrid(X_mesh, Y_mesh)
      EX = []
      EY = []
      EZ = []
      for x in np.nditer(XX):
         EX.append(float(x))
      for y in np.nditer(YY):
         EY.append(float(y))
      Grid1 = pd.DataFrame(data={'X':EX, 'Y':EY})
      for index, rows in Grid1.iterrows():
         estimated = self.OK(rows['X'], rows['Y'])
         EZ.append(round(estimated,2))
      Grid = pd.DataFrame(data={'X':EX, 'Y':EY, 'Z':EZ})
      print("EXXXXXXXXXXXXXXXXXXXXXXX")
      print(EX)
      
      return [EX, EY, EZ]
      # return Grid




