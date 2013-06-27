def IsBSplineTfmValid(tfm):
    f=open(tfm,'r')
    nTransforms = 0
    for l in f:
      if string.find(l,'# Transform') != -1:
        print l
        nTransforms = nTransforms+1
    return nTransforms == 2
