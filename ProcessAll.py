import os,sys

cmd = sys.argv[1]
for i in range(11,51):
  os.system('python '+cmd+' '+str(i))
  # print i,' ready'
