import markup, sys, glob, string, re, os

def humanSort(l):
  """ Sort the given list in the way that humans expect. 
      Conributed by Yanling Liu
  """ 
  convert = lambda text: int(text) if text.isdigit() else text 
  alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
  l.sort( key=alphanum_key )


input1 = sys.argv[1]
output = sys.argv[2]

input1FilesBefore = glob.glob(input1+'/*_before.gif')
#input1FilesAfter = glob.glob(inputDir+'/*gif')
#input2FilesBefore = glob.glob(inputDir+'/*gif')
#input2FilesAfter = glob.glob(inputDir+'/*gif')
cases = {os.path.split(x)[1].split('_')[0] for x in input1FilesBefore}


for c in cases:
  pf = open(output+'/'+c+'_page.html','w')
  page = markup.page()
  page.init()

  page.h2()
  page.p(c)
  page.p.close()
  page.h2.close()
  imagesForCase = [x for x in input1FilesBefore if os.path.split(x)[1].startswith(c)]
  humanSort(imagesForCase)

  page.table()

  for i in range(len(imagesForCase)):
    needleId = imagesForCase[i].split('_')[1]
    '''
    page.h3()
    page.p('Confirmation image '+needleId)
    page.p.close()
    page.h3.close()
    '''
    beforeImage = input1+'/'+c+'_'+needleId+'_before.gif'
    afterImage = input1+'/'+c+'_'+needleId+'_after.gif'

    if not (os.path.exists(beforeImage) and os.path.exists(afterImage)):
      continue

    page.tr()
    page.td()
    page.img(src=beforeImage,width=700)
    page.td.close()
    page.td()
    page.img(src=afterImage,width=700)
    page.td.close()
    page.tr.close()

  page.table.close()
  
  page.hr()
  page.br()
  page.br()
  page.br()

  for c in page.content:
    pf.write(str(c)+'\n')

  pf.close()

