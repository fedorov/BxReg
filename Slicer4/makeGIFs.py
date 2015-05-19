import sys, glob, string, os, re

def humanSort(l):
  """ Sort the given list in the way that humans expect. 
      Conributed by Yanling Liu
  """ 
  convert = lambda text: int(text) if text.isdigit() else text 
  alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
  l.sort( key=alphanum_key )

# read all snapshot files
# for each case key, sort the files
# take pairs that have the same needle id, coombine into gif

inputDir = sys.argv[1]
outputDir = sys.argv[2]

inputFiles = glob.glob(inputDir+'/*png')
cases = {os.path.split(x)[1].split('_')[0] for x in inputFiles}

for c in cases:
  imagesForCase = [x for x in inputFiles if os.path.split(x)[1].startswith(c)]
  humanSort(imagesForCase)
  # list should look like fixed_for_needle_i, registered_for_needle_i, ...,
  # moving

  print imagesForCase

  for n in range(len(imagesForCase)/2):

    fixedFileName = os.path.split(imagesForCase[n*2])[1]
    registeredFileName = os.path.split(imagesForCase[n*2+1])[1]
    movingFileName = os.path.split(imagesForCase[-1])[1]

    needleId = fixedFileName.split('_')[1]

    print needleId

    fixed = imagesForCase[n*2]
    registered = imagesForCase[n*2+1]
    moving = imagesForCase[-1]

    fixedGif = '/tmp/'+fixedFileName.split('.')[0]+'.gif'
    movingGif = '/tmp/'+movingFileName.split('.')[0]+'.gif'
    registeredGif = '/tmp/'+registeredFileName.split('.')[0]+'.gif'

    os.system('sips -s format gif '+fixed+' --out /tmp')
    os.system('sips -s format gif '+moving+' --out /tmp')
    os.system('sips -s format gif '+registered+' --out /tmp')

    beforeRegistration = outputDir+'/'+c+'_'+needleId+'_before.gif'
    afterRegistration = outputDir+'/'+c+'_'+needleId+'_after.gif'

    os.system('gifsicle --delay=100 --loop '+fixedGif+' '+movingGif+' > '+beforeRegistration)
    os.system('gifsicle --delay=100 --loop '+fixedGif+' '+registeredGif+' > '+afterRegistration)

