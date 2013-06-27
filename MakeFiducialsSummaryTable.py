import os, argparse, string, re, sys, glob
from time import time

def BFResample(reference,moving,tfm,output,interp='Linear'):
  CMD = 'Slicer3 --launch BRAINSResample --referenceVolume '+reference+' --inputVolume '+moving+' --outputVolume '+output+' --warpTransform '+tfm
  CMD = CMD + ' --interpolationMode '+interp
  ret = os.system(CMD)
  if ret:
    exit()

def IsBSplineTfmValid(tfm):
  f=open(tfm,'r')
  nTransforms = 0
  for l in f:
    if string.find(l,'# Transform') != -1:
      nTransforms = nTransforms+1
  return nTransforms == 2

def TransformFiducials(ref, mov, fidIn, tfmIn, fidOut):

 CMD="~/bitbucket/SlicerCLITools-build/TransformFiducialList --referenceimage "+ref+" --movingimage "+mov+" --fiducialsfile "+fidIn+" --inputtransform "+tfmIn+" --outputfile "+fidOut
 print CMD
  
 ret = os.system(CMD)
 if ret:
   exit()

 '''
 Case11/IntraopImages/10.nrrd --movingimage
 Case11/IntraopImages/CoverProstate.nrrd --fiducialsfile
 Case11/IntraopImages/CoverProstate-Centroid.fcsv --inputtransform
 Case11/Registration2attempts/10-IntraIntra-BSpline-Attempt1.tfm --outputfile
 Case11/Registration2attempts/10_CoverProstate-Centroid.fcsv
 '''
def tm2sec(tm):
  try:
    hhmmss = string.split(tm,'.')[0]
  except:
    hhmmss = tm

  try:
    ssfrac = float('0.'+string.split(tm,'.')[1])
  except:
    ssfrac = 0.

  if len(hhmmss)==6: # HHMMSS
    sec = float(hhmmss[0:2])*60.*60.+float(hhmmss[2:4])*60.+float(hhmmss[4:6])
  elif len(hhmmss)==4: # HHMM
    sec = float(hhmmss[0:2])*60.*60.+float(hhmmss[2:4])*60.
  elif len(hhmmss)==2: # HH
    sec = float(hhmmss[0:2])*60.*60.

  sec = sec+ssfrac

  return sec
 
def ReadInitialTime(case):

  dir='/Users/fedorov/bitbucket/prostateintraopmotion2012/Data/Case'+case+'/CoverProstate'
  subdir = os.listdir(dir)[0]
  file=dir+'/'+subdir+'/timestamp'
  f=open(file,'r')
  return tm2sec(f.read())

def ReadNeedleTime(case,nid):
  file='/Users/fedorov/bitbucket/prostateintraopmotion2012/Data/Case'+case+'/NeedleConfirmation/'+str(nid)+'/timestamp'
  f=open(file,'r')
  return tm2sec(f.read())

def ReadFiducial(fname):
  f = open(fname, 'r')
  l = f.read()
  i = l.split(',')
  return [float(i[1]),float(i[2]),float(i[3])]

parser = argparse.ArgumentParser(description="Run various registration experiments for a given case number")
parser.add_argument('case',help='case to be processed')

args = parser.parse_args()

case = args.case

IntraDir = 'Case'+case+'/IntraopImages'
RegDir = 'Case'+case+'/Registration2attempts'
ResDir='RegistrationVisualVerification/Case'+case
TempDir='TempDir'
try:
  os.mkdir(ResDir)
except:
  pass

initialPosition = ReadFiducial(IntraDir+'/CoverProstate-Centroid.fcsv')
initialTime = ReadInitialTime(case)
# print 'Initial time: ',initialTime

#   list all needle image ids first
needleImageIds = []
needleImages = glob.glob(IntraDir+'/[0-9]*nrrd')
for ni in needleImages:
  fname = string.split(ni,'/')[-1]
  #if string.find(fname,'TG') == -1:
  # keep only those images that look like 10.nrrd
  if re.match('\d+\.nrrd',fname):
    needleImageIds.append(int(string.split(fname,'.')[0]))
needleImageIds.sort()

for nid in needleImageIds:
  nidTime = ReadNeedleTime(case,nid)
  # print 'Needle time: ',nidTime
  resampled = ResDir+'/'+str(nid)+'-BSplineRegistered-centroid.fcsv'
  # resampled = ResDir+'/'+str(nid)+'-Pelvis-RigidRegistered-centroid.fcsv'
  nidPosition = ReadFiducial(resampled)
  print case,',',nid,',',nidTime-initialTime,',',nidPosition[0]-initialPosition[0],', ',nidPosition[1]-initialPosition[1],', ',nidPosition[2]-initialPosition[2]
 
  # BFResample(reference=fixedImage,moving=movingImage,tfm=bsplineTfm,output=resampled)  
