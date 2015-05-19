import re, string, glob, shutil, os

segPath = 'TobiasSegmentations-new'
dataPath = 'Data'

for c in range(51,52):
  print 'Case',c
  try:
    orig = glob.glob(segPath+'/Case'+"%03i" % c+'*')
    origFile = orig[0]
    destFile = dataPath+'/Case'+str(c)+'/IntraopImages/CoverProstate-TG.nrrd'
    shutil.copyfile(origFile,destFile)
    destFile = dataPath+'/Case'+str(c)+'/IntraopImages/CoverProstate-label.nrrd'
    shutil.copyfile(origFile,destFile)
    # also make a symbolic link to the latest CoverProstate scan
    coverProstates = glob.glob(dataPath+'/Case'+str(c)+'/IntraopImages/CoverProstate[1-9]*.nrrd')
    coverProstateLink = dataPath+'/Case'+str(c)+'/IntraopImages/CoverProstate.nrrd'
    os.remove(coverProstateLink)
    coverProstates.sort()
    shutil.copyfile(coverProstates[-1],coverProstateLink)
    try:
      os.symlink(coverProstates[-1],coverProstateLink)
    except:
      print 'Failed to make a link'
  except Exception as e:
    print 'Failed',e
