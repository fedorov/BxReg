import SimpleITK as sitk
import glob, sys, string, os

for c in range(11,102):
  imageName = 'Data/Case'+str(c)+'/IntraopImages/CoverProstate-TG.nrrd'
  if not os.path.exists(imageName):
    continue

  image = sitk.ReadImage(imageName)
  stat = sitk.LabelStatisticsImageFilter()
  stat.Execute(image,image)
  spacing = image.GetSpacing()
  vol = stat.GetCount(1)*spacing[0]*spacing[1]*spacing[2]/1000.
  print str(c)+','+str(vol)
