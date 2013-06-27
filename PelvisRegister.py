import os, argparse, string, re, sys, glob
from time import time

def BFRegister(fixed=None,moving=None,fixedMask=None,movingMask=None,rigidTfm=None,affineTfm=None,bsplineTfm=None,initializer=None,log=None,initTfm=None,initialTfm=None):
  if fixedMask != None or movingMask != None:
    CMD="Slicer3 --launch BRAINSFitIGT --fixedVolume "+fixed+" --movingVolume "+moving+" --debugNumberOfThreads 1 --maskProcessingMode ROI --numberOfIterations 500 "
  else:
    CMD="Slicer3 --launch BRAINSFitIGT --fixedVolume "+fixed+" --movingVolume "+moving+" --debugNumberOfThreads 1 --maskProcessingMode NOMASK --numberOfIterations 500 "

  if fixedMask:
    CMD = CMD+" --fixedBinaryVolume "+fixedMask
  if movingMask:
    CMD = CMD+" --movingBinaryVolume "+movingMask
  if initializer:
    CMD = CMD+" "+initializer
  if initTfm:
    CMD = CMD+' --initialTransformDebug '+initTfm
  if rigidTfm:
    CMD = CMD+" --useRigid --outputTransform "+rigidTfm
  if affineTfm:
    CMD = CMD+" --useAffine --affineTransformDebug "+affineTfm
  if bsplineTfm:
    CMD = CMD+" --useROIBSpline --bsplineTransform "+bsplineTfm  
  #CMD = CMD+" --useGeometryAlign "
  #if fixedMask and movingMask:
  #  CMD = CMD+' --useCenterOfROIAlign '

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
RegDir='Case'+case+'/PelvisRegistration2attempts'
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
movingImage = IntraDir+'/CoverProstate.nrrd'
movingMask = IntraDir+'/CoverProstate-NONTG.nrrd'

latestRigidTfm = 'Identity.tfm'
latestMovingMask = movingMask

# try to read the registration log
regTimesLog = open(RegDir+'/'+case+'_registration_times.log','a')

for nid in needleImageIds:
  success = False
  rigidTfm=None
  affineTfm=None
  bsplineTfm=None
  attempt = ''

  nidStr=str(nid)

  fixedImage = IntraDir+'/'+nidStr+'.nrrd'

  log = RegDir+'/'+nidStr+'_registration.log'

  # check if there is a matching TG
  fixedMask = 'FFFF' #IntraDir+'/'+nidStr+'-PELVIS.nrrd'
  if not os.path.isfile(fixedMask):
    bsplineTfm = RegDir+'/'+nidStr+'-IntraIntra-BSpline-Attempt1.tfm'
    rigidTfm = RegDir+'/'+nidStr+'-IntraIntra-Rigid-Attempt1.tfm'
    fixedMask = TempDir+'/'+str(case)+'_'+nidStr+'-Resampled-'+string.split(latestMovingMask,'/')[-1]
    BFResample(reference=fixedImage,moving=latestMovingMask,tfm=latestRigidTfm,output=fixedMask,interp='NearestNeighbor')
    # since we have only one mask, we cannot use a smarter initialization procedure
    startTime = time()
    BFRegister(fixed=fixedImage,moving=movingImage,fixedMask=fixedMask,rigidTfm=rigidTfm,log=log,initialTfm=latestRigidTfm)
    # try to register without using mask
    # BFRegister(fixed=fixedImage,moving=movingImage,rigidTfm=rigidTfm,log=log,initialTfm=latestRigidTfm)
    endTime = time()
    attempt='Attempt1'
  else:
    bsplineTfm = RegDir+'/'+nidStr+'-IntraIntra-BSpline-Attempt2.tfm'
    rigidTfm = RegDir+'/'+nidStr+'-IntraIntra-Rigid-Attempt2.tfm'
    initTfm = RegDir+'/'+nidStr+'-IntraIntra-Init-Attempt2.tfm'
    startTime = time()
    BFRegister(fixed=fixedImage,moving=movingImage,movingMask=movingMask,fixedMask=fixedMask,rigidTfm=rigidTfm,log=log,initTfm=initTfm)
    endTime = time()
    attempt='Attempt1'

  latestRigidTfm = rigidTfm

  regTimesLog.write(str(case)+';'+str(nid)+';'+attempt+';'+str(endTime-startTime)+';')
  '''

  #   prepare the parameters
  #   2.1: run with the CoverProstate mask only first
  
  rigidTfm = RegDir+'/'+nidStr+'_IntraIntraRigid_FixedMaskOnly.tfm'
  #affineTfm = RegDir+'/'+nidStr+'_IntraIntraAffine_FixedMaskOnly.tfm'
  bsplineTfm = RegDir+'/'+nidStr+'_IntraIntraBSpline_FixedMaskOnly.tfm'
  log = RegDir+'/'+nidStr+'_FixedMaskOnly.log'

  if latestRigidTfm:
    # first apply the transformation to the mask from the moving image
    movingMaskResampled = IntraDir+'/Registration/'+nidStr+'_ResampledFixedMask.nrrd'
    BFResample(reference=fixedImage,moving=movingMask,tfm=latestRigidTfm,output=movingMaskResampled,interp='NearestNeighbor')
    BFRegister(fixed=fixedImage,moving=movingImage,fixedMask=movingMaskResampled,rigidTfm=rigidTfm,affineTfm=affineTfm,bsplineTfm=bsplineTfm,log=log,initialTfm=latestRigidTfm)
  else:

 
  
  # 2.2: run with the same mask for fixed and moving
  rigidTfm = RegDir+'/'+nidStr+'_IntraIntraRigid_SameFixedMovingMasks.tfm'
  #affineTfm = RegDir+'/'+nidStr+'_IntraIntraAffine_SameFixedMovingMasks.tfm'
  bsplineTfm = RegDir+'/'+nidStr+'_IntraIntraBSpline_SameFixedMovingMasks.tfm'
  log = RegDir+'/'+nidStr+'_SameFixedMovingMasks.log'

  BFRegister(fixed=fixedImage,moving=movingImage,movingMask=movingMask,fixedMask=movingMask,rigidTfm=rigidTfm,affineTfm=affineTfm,bsplineTfm=bsplineTfm,log=log)
  success = success or IsBSplineTfmValid(bsplineTfm)
  

  # 2.3: run with the latest needle confirmation mask available
  rigidTfm = RegDir+'/'+nidStr+'_IntraIntraRigid_LatestMask.tfm'
  #affineTfm = RegDir+'/'+nidStr+'_IntraIntraAffine_LatestMask.tfm'
  bsplineTfm = RegDir+'/'+nidStr+'_IntraIntraBSpline_LatestMask.tfm'
  initTfm = RegDir+'/'+nidStr+'_IntraIntraInit_LatestMask.tfm'
  log = RegDir+'/'+nidStr+'_LatestMask.log'
  
  latestFixedMask=None
  for nidtg in needleImageIds:
    if nidtg>nid:
      break
    nidtgFile = IntraDir+'/'+str(nidtg)+'-TG.nrrd'
    if os.path.isfile(nidtgFile):
      latestFixedMask = nidtgFile

  if latestFixedMask:

    if latestRigidTfm:
      BFRegister(fixed=fixedImage,moving=movingImage,movingMask=movingMask,fixedMask=latestFixedMask,rigidTfm=rigidTfm,affineTfm=affineTfm,bsplineTfm=bsplineTfm,log=log,initTfm=initTfm,initialTfm=latestRigidTfm)
    else:
      BFRegister(fixed=fixedImage,moving=movingImage,movingMask=movingMask,fixedMask=latestFixedMask,rigidTfm=rigidTfm,affineTfm=affineTfm,bsplineTfm=bsplineTfm,log=log,initTfm=initTfm)

    success = success or IsBSplineTfmValid(bsplineTfm)

    
    # 2.4: take the initial transform and run with just the fixed mask
    rigidTfm = RegDir+'/'+nidStr+'_IntraIntraRigid_WithInitTfm.tfm'
    #affineTfm = RegDir+'/'+nidStr+'_IntraIntraAffine_LatestMask.tfm'
    bsplineTfm = RegDir+'/'+nidStr+'_IntraIntraBSpline_WithInitTfm.tfm'
    log = RegDir+'/'+nidStr+'_WithInitTfm.log'
  
    # NOTE: no moving mask!
    BFRegister(fixed=fixedImage,moving=movingImage,fixedMask=latestFixedMask,rigidTfm=rigidTfm,affineTfm=affineTfm,bsplineTfm=bsplineTfm,log=log,initialTfm=initTfm)   
    success = success or IsBSplineTfmValid(bsplineTfm)
    
  else:
    print 'Cannot do mode 2.3 because no needle image masks found!'

  if not success:
    print "None of the registration approaches succeeded"
    print "Latest needle image was ",nid
    exit()
  '''
