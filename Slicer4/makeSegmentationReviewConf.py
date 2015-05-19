import re, string, glob, shutil, os
import ConfigParser as conf

segPath = '/Users/fedorov/Documents/Projects\ (original)/BxRetrospectiveAccuracyEvaluation/TobiasSegmentations-new'
dataPath = 'Data'
confPath = '/Users/fedorov/Documents/Projects\ (original)/BxRetrospectiveAccuracyEvaluation/SegmentationsReviewConf'

for c in os.listdir(dataPath)
  print 'Case',c
  conf = open(confPath+'/'+c+'.conf','w')
  cf = conf.SafeConfigParser()
  cf.optionxform = str
  cf.add_section('MovingData')
  cf.set('MovingData','ImagesPath',
  
  try:
    orig = glob.glob(segPath+'/Case'+"%03i" % c+'*')
    origFile = orig[0]
    destFile = dataPath+'/Case'+str(c)+'/IntraopImages/CoverProstate-TG.nrrd'
    shutil.copyfile(origFile,destFile)
    # also make a symbolic link to the latest CoverProstate scan
    coverProstates = glob.glob(dataPath+'/Case'+str(c)+'/IntraopImages/CoverProstate[1-9]*.nrrd')
    coverProstateLink = dataPath+'/Case'+str(c)+'/IntraopImages/CoverProstate.nrrd'
    coverProstates.sort()
    try:
      os.symlink(coverProstates[-1],coverProstateLink)
    except:
      print 'Failed to make a link'
  except Exception as e:
    print 'Failed',e
