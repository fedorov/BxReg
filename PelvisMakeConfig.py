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

parser = argparse.ArgumentParser(description="Run various registration experiments for a given case number")
parser.add_argument('case',help='case to be processed')

args = parser.parse_args()

case = args.case

IntraDir = 'Case'+case+'/IntraopImages'
RegDir = 'Case'+case+'/PelvisRegistration2attempts'
ResDir='PelvisRegistrationVisualVerification/Case'+case

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

configFile = open('PelvisRegistrationVisualVerification/Case'+case+'_VisAIRe.conf','w')

# moving image/mask will always be the same
movingImage = IntraDir+'/CoverProstate.nrrd'

configFile.write('[MovingImage]\n')
configFile.write(os.path.abspath(movingImage)+'\n')

configFile.write('[FixedImages]\n')
for nid in needleImageIds:
  nidStr=str(nid)
  fixedImage = IntraDir+'/'+nidStr+'.nrrd'
  configFile.write(os.path.abspath(fixedImage)+'\n')

configFile.write('[RegisteredImages]\n')
for nid in needleImageIds:
  nidStr=str(nid)
  resampled = ResDir+'/'+nidStr+'-Rigid_resampled.nrrd'
  configFile.write(os.path.abspath(resampled)+'\n')

# assessment questions; format:
#   comment; type=[binary,number];
configFile.write('[AssessmentQuestions]\n')
configFile.write('Did registration improve alignment?;binary;\n')
configFile.write('Is registered image of diagnostic quality?;binary;\n')
configFile.write('Quantitative assessment of mis-registration (if available);numeric;\n')

configFile.write('[CaseName]\n')
configFile.write('BxCase'+case+'\n')

configFile.close()
