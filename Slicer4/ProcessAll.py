import os,sys

cmd = sys.argv[1]
for i in range(51,100):
  os.system('python '+cmd+' '+str(i))
  # print i,' ready'
