import os, sys, re, string, glob

def InvertMask(input,output):
  CMD='/Users/fedorov/Software/sandbox/RegistrationTools/build/InvertMask '+input+' '+output
  os.system(CMD)

IntraDir = 'Case'+sys.argv[1]

TGs = glob.glob(IntraDir+'/IntraopImages/*TG.nrrd')

for tg in TGs:
  pelvis = tg.replace('TG','NONTG')
  InvertMask(tg,pelvis)

