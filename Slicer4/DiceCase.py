import os, argparse, string, re, sys, glob
from time import time

def BFRegister(fixed=None,moving=None,fixedMask=None,movingMask=None,rigidTfm=None,affineTfm=None,bsplineTfm=None,initializer=None,log=None,initTfm=None,initialTfm=None):
  CMD="Slicer3 --launch BRAINSFitIGT --fixedVolume "+fixed+" --movingVolume "+moving+" --debugNumberOfThreads 1 --maskProcessingMode ROI --numberOfIterations 500 "

  if fixedMask:
    CMD = CMD+" --fixedBinaryVolume "+fixedMask
  if movingMask:
    CMD = CMD+" --movingBinaryVolume "+movingMask
  if initializer:
    CMD = CMD+" "+initializer
  if initTfm:
    CMD = CMD+' --initialTransformDebug '+initTfm
  if rigidTfm:
    CMD = CMD+" --useRigid --rigidTransformDebug "+rigidTfm
  if affineTfm:
    CMD = CMD+" --useAffine --affineTransformDebug "+affineTfm
  if bsplineTfm:
    CMD = CMD+" --useROIBSpline --bsplineTransform "+bsplineTfm  
  if fixedMask and movingMask:
    CMD = CMD+' --useCenterOfROIAlign '

  if initialTfm and not initializer:
    CMD = CMD+' --initialTransform '+initialTfm

  print "About to run ",CMD

  if log:
    CMD = CMD+" | tee "+log

  ret = os.system(CMD)
  if ret:
    exit()

def BFResample(reference,moving,tfm,output,interp='Linear'):
  CMD = 'Slicer3 --launch BRAINSResample --referenceVolume '+reference+' --inputVolume '+moving+' --outputVolume '+output+' --warpTransform '+tfm
  CMD = CMD + ' --interpolationMode '+interp
  ret = os.system(CMD)
  if ret:
    exit()

def GetDice(reference,moving, result):
  CMD = '~/Software/sandbox/RegistrationTools/build/AssessOverlap '+reference+' '+moving+' | tee '+result
  ret = os.system(CMD)
  if ret:
    exit()

def IsBSplineTfmValid(tfm):
  try:
    f=open(tfm,'r')
  except:
    return False
  nTransforms = 0
  for l in f:
    if string.find(l,'# Transform') != -1:
      nTransforms = nTransforms+1
  return nTransforms == 2

parser = argparse.ArgumentParser(description="Run various registration experiments for a given case number")
parser.add_argument('case',help='case to be processed')

args = parser.parse_args()

case = args.case

SegDir = 'Segmentations/Case'+case+'-ManualSegmentations'
RegDir='Case'+case+'/Registration2attempts'
TempDir='TempSegRegDir'
IntraDir='Case'+case+'/IntraopImages'
try:
  os.mkdir(RegDir)
except:
  pass


# 1. run preop/intraop registration

# 2. for each needle image, run intraop/intraop registration using different
# registration modes

#   list all needle image ids first
needleImageIds = []
if 1:
  needleImages = glob.glob(IntraDir+'/[0-9]*nrrd')
  for ni in needleImages:
    fname = string.split(ni,'/')[-1]
    #if string.find(fname,'TG') == -1:
    # keep only those images that look like 10.nrrd
    if re.match('\d+\.nrrd',fname):
      needleImageIds.append(int(string.split(fname,'.')[0]))
  needleImageIds.sort()
else:
  needleImageIds = [int(needleReq)]

lastId = str(needleImageIds[-1])
# moving image/mask will always be the same
IdentityTfm='Identity.tfm'
movingMask = SegDir+'/CoverProstate-label.nrrd'
fixedMask = SegDir+'/'+lastId+'-label.nrrd'
Tfm1='Case'+case+'/Registration2attempts/'+lastId+'-IntraIntra-BSpline-Attempt1.tfm'
Tfm2='Case'+case+'/Registration2attempts/'+lastId+'-IntraIntra-BSpline-Attempt2.tfm'

before = TempDir+'/Case'+case+'-'+lastId+'-before.nrrd'
after = TempDir+'/Case'+case+'-'+lastId+'-after.nrrd'

BFResample(fixedMask, movingMask, IdentityTfm, before, interp='NearestNeighbor')

if IsBSplineTfmValid(Tfm2):
  BFResample(fixedMask, movingMask, Tfm2, after, interp='NearestNeighbor')
else:
  BFResample(fixedMask, movingMask, Tfm1, after, interp='NearestNeighbor')

diceBefore = TempDir+'/Case'+case+'_dice_before.log'
diceAfter = TempDir+'/Case'+case+'_dice_after.log'
GetDice(fixedMask, before, diceBefore)

GetDice(fixedMask, after, diceAfter)
