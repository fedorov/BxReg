import glob, string, re, os

def humanSort(l):
  """ Sort the given list in the way that humans expect. 
      Conributed by Yanling Liu
  """ 
  convert = lambda text: int(text) if text.isdigit() else text 
  alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
  l.sort( key=alphanum_key )

srcDir = 'Data'
destDir = 'FirstAndLast'

for c in range(50,102):

  if c==70 or c==78:
    continue

  needles = glob.glob(srcDir+'/Case'+str(c)+'/IntraopImages/[1-9]*.nrrd')
  covers = glob.glob(srcDir+'/Case'+str(c)+'/IntraopImages/CoverProstate*nrrd')
  humanSort(needles)
  print 'Sorted needles: ',needles
  covers.sort()

  import shutil

  try:
    os.makedirs(destDir+'/Case'+str(c))
  except:
    pass

  shutil.copyfile(needles[-1],destDir+'/Case'+str(c)+'/'+needles[-1].split('/')[-1])
  shutil.copyfile(covers[-1],destDir+'/Case'+str(c)+'/'+covers[-1].split('/')[-1])
