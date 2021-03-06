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

parser = argparse.ArgumentParser(description="Run various registration experiments for a given case number")
parser.add_argument('case',help='case to be processed')

args = parser.parse_args()

case = args.case

IntraDir = 'Case'+case+'/IntraopImages'
RegDir = 'Case'+case+'/PelvisRegistration2attempts'
#RegDir = 'Case'+case+'/Registration2attempts'
ResDir='RegistrationVisualVerification/Case'+case
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

print needleImageIds

# moving image/mask will always be the same
movingImage = IntraDir+'/CoverProstate.nrrd'

for nid in needleImageIds:
  bsplineTfm=None

  nidStr=str(nid)

  fixedImage = IntraDir+'/'+nidStr+'.nrrd'

  # check if there is a matching TG
  bsplineTfm = RegDir+'/'+nidStr+'-IntraIntra-Rigid-Attempt2.tfm'
  if not os.path.isfile(bsplineTfm):
    bsplineTfm = RegDir+'/'+nidStr+'-IntraIntra-Rigid-Attempt1.tfm'
  if not os.path.isfile(bsplineTfm):
    print 'Failed to find ANY transform!'
    exit()

  resampled = ResDir+'/'+nidStr+'-Pelvis-RigidRegistered-centroid.fcsv'
  fidList = IntraDir+'/CoverProstate-Centroid.fcsv'

  #if not IsBSplineTfmValid(bsplineTfm):
  #  print 'BSpline transform is not valid! Will skip needle image ',nid
  #  continue

  TransformFiducials(ref=fixedImage,mov=movingImage,fidIn=fidList,tfmIn=bsplineTfm,fidOut=resampled)
  # BFResample(reference=fixedImage,moving=movingImage,tfm=bsplineTfm,output=resampled)
