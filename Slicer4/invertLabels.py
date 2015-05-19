import SimpleITK as sitk
import sys, os, glob, string

for case in range(52,102):
  #case = sys.argv[1]
  caseDir = 'Case'+str(case)

  inputDir = 'Data/'+caseDir+'/IntraopImages'

  inputLabelName = inputDir+'/CoverProstate-TG.nrrd'
  outputLabelName = inputDir+'/CoverProstate-NONTG.nrrd'
  try:
    inputLabel = sitk.ReadImage(inputLabelName)
  except:
    continue
  changeFilter = sitk.ChangeLabelImageFilter()
  changeMap = sitk.DoubleDoubleMap()
  
  changeMap[0] = 1
  changeMap[1] = 0
  
  changedLabel = changeFilter.Execute(inputLabel, changeMap)
  sitk.WriteImage(changedLabel, outputLabelName, True)
  
  print(str(case)+' done')
