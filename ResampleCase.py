import os, argparse, string, re, sys, glob
from time import time

def BFResample(reference,moving,tfm,output,interp='Linear'):
  CMD = '/home/fedorov/src/Release/Slicer3-build/Slicer3 --launch BRAINSResample --referenceVolume '+reference+' --inputVolume '+moving+' --outputVolume '+output+' --warpTransform '+tfm
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

parser = argparse.ArgumentParser(description="Run various registration experiments for a given case number")
parser.add_argument('case',help='case to be processed')

args = parser.parse_args()

case = args.case

IntraDir = 'Data/Case'+case+'/IntraopImages'
RegDir = 'Data/Case'+case+'/Slicer3registration'
ResDir='Slicer3verification/Case'+case
TempDir='TempDir'
try:
  os.mkdir(ResDir)
except:
  pass


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

# moving image/mask will always be the same
movingImage = IntraDir+'/CoverProstate.nrrd'

for nid in needleImageIds:
  bsplineTfm=None

  nidStr=str(nid)

  fixedImage = IntraDir+'/'+nidStr+'.nrrd'

  # check if there is a matching TG
  bsplineTfm = RegDir+'/'+nidStr+'-IntraIntra-BSpline-Attempt2.tfm'
  if not os.path.isfile(bsplineTfm):
    bsplineTfm = RegDir+'/'+nidStr+'-IntraIntra-BSpline-Attempt1.tfm'
  if not os.path.isfile(bsplineTfm):
    print 'Failed to find ANY transform!'
    exit()

  resampled = ResDir+'/'+nidStr+'-BSpline_resampled.nrrd'

  if not IsBSplineTfmValid(bsplineTfm):
    print 'BSpline transform is not valid! Will skip needle image ',nid
    continue

  BFResample(reference=fixedImage,moving=movingImage,tfm=bsplineTfm,output=resampled)
