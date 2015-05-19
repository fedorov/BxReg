import os, argparse, string, re, sys, glob
from time import time

def TransformFiducials(ref, mov, fidIn, tfmIn, fidOut):

 CMD="~/bitbucket/SlicerCLITools-build/TransformFiducialList --referenceimage "+ref+" --movingimage "+mov+" --fiducialsfile "+fidIn+" --inputtransform "+tfmIn+" --outputfile "+fidOut
 print CMD
  
 ret = os.system(CMD)
 if ret:
   exit()


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

def IsBSplineTfmValid(tfm):
  f=open(tfm,'r')
  nTransforms = 0
  for l in f:
    if string.find(l,'# Transform') != -1:
      nTransforms = nTransforms+1
  return nTransforms == 2

parser = argparse.ArgumentParser(description="Run various registration experiments for a given case number")
parser.add_argument('case',help='case to be processed')
parser.add_argument('--needle',help='needle confirmation image to register')

args = parser.parse_args()

case = args.case
needleReq = args.needle

IntraDir = 'Case'+case+'/IntraopImages'
PreopDir = 'PreopData'
RegDir='Case'+case+'/PreopIntraopRegistration'
TempDir='TempDir'
try:
  os.mkdir(RegDir)
except:
  pass


# 1. run preop/intraop registration

# 2. for each needle image, run intraop/intraop registration using different
# registration modes

#   list all needle image ids first
needleImageIds = []
if not needleReq:
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

# moving image/mask will always be the same
movingImage = PreopDir+'/Case'+case+'_preop.nrrd'
movingMask = PreopDir+'/Case'+case+'_preop-TG.nrrd'
fixedImage = IntraDir+'/CoverProstate.nrrd'
fixedMask = IntraDir+'/CoverProstate-TG.nrrd'

latestRigidTfm = 'Identity.tfm'
latestMovingMask = movingMask

# try to read the registration log
regTimesLog = open(RegDir+'/PreIntra_registration_times.log','a')

bsplineTfm = RegDir+'/Case'+case+'-PreIntra-BSpline.tfm'
affineTfm = RegDir+'/Case'+case+'-PreIntra-Affine.tfm'
rigidTfm = RegDir+'/Case'+case+'-PreIntra-Rigid.tfm'

startTime = time()
BFRegister(fixed=fixedImage,moving=movingImage,fixedMask=fixedMask,movingMask=movingMask,rigidTfm=rigidTfm,bsplineTfm=bsplineTfm,affineTfm=affineTfm)
endTime = time()
regTimesLog.write(str(case)+';'+str(endTime-startTime)+';')

# warp the preop targets
fidList = PreopDir+'/Case'+case+'_consensus_targets.fcsv'
registeredTargets = IntraDir+'/Case'+case+'_CoverProstate-registered_targets.fcsv'
TransformFiducials(ref=fixedImage,mov=movingImage,fidIn=fidList,tfmIn=bsplineTfm,fidOut=registeredTargets)


