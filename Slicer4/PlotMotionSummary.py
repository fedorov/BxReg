from pylab import *
import os, sys, string, glob, re, numpy
import operator

def sort_table(table, col):
  return sorted(table, key=operator.itemgetter(col))

def readData(dataf):
  f = open(dataf,'r')
  d = []
  h = []
  header = True
  for l in f:
    # skip the first column
    items = string.split(l[:-1],',')[1:]
    if header:
      h = items
      header = False
    else:
      items = map(lambda x: float(x), items)
      d.append(items)

  return h,d

allTimes = []
allTimesArr = numpy.array([])

dataf = sys.argv[1]

header,data = readData(dataf)

print header

maxTime = {}

for row in data:
  try:
    maxTime[row[0]] = max(maxTime[row[0]],row[2])
  except:
    maxTime[row[0]] = row[2]

#print 'Maximum time:',maxTime
print 'Min time:',min(maxTime.values()),' max:',max(maxTime.values()),' median:',numpy.median(maxTime.values())


# add maximum case time column
for row in data:
  row.append(maxTime[row[0]])

# sort cases by the maximum dTime
dataSorted = sort_table(data, len(data[0])-1)

# show boxplots of the ordered Gland.2d and Gland.3d
plottedItemNumber = 12
print 'Plotting item number ',plottedItemNumber,', which is ',header[plottedItemNumber]
oldItem = dataSorted[0][0]
caseIDs = []
caseIDs.append(oldItem)
allItems = []
items = []
timesOrdered = [float(dataSorted[0][-1])]
for row in dataSorted:
  if row[0]!=oldItem:    
    allItems.append(items)
    # print items
    items = []
    oldItem = row[0]
    caseIDs.append(oldItem)
    timesOrdered.append(float(row[-1]))
  items.append(float(row[plottedItemNumber]))

allItems.append(items)

fig=figure()
ax1=fig.add_subplot(111)
#ax1.set_autoscale_on(False)
bp=boxplot(allItems)
#ax1.xlim([0,41])
#setp(range(11,40))
#xlabel('case ID')
#ylabel('registration time, sec')

setp(bp['medians'], lw=2)
setp(bp['fliers'], lw=2)
setp(bp['whiskers'], lw=2)
setp(bp['boxes'], lw=2)
setp(bp['caps'], lw=2)

print len(allItems)

ax2 = ax1.twinx()
print timesOrdered
print len(timesOrdered)

print 'Mean: ',mean(timesOrdered), ' Min: ',min(timesOrdered),' Max: ',max(timesOrdered)

ax2.plot(range(1,41), timesOrdered,'g-',lw=2)

xlim([0,41])
ax1.set_xlabel('case ID')
ax1.set_ylabel('axial in-plane displacement, mm')
ax2.set_ylabel('time to last needle confirmation image, min')

for tl in ax1.get_yticklabels():
  tl.set_color('b')

for tl in ax2.get_yticklabels():
  tl.set_color('g')

print caseIDs

xticks(range(1,41), map(lambda x: int(x), caseIDs))
show()



# add the line with the time until the last image

'''

for c in range(11,51):
  regTimeLog = open('Case'+str(c)+'/Registration2attempts/'+str(c)+'_registration_times.log','r')
  log = regTimeLog.readline()
  items = string.split(log, ';')
  
  # format for the log entry: case;nid;attempt;endTime-startTime;
  
  times = []
  print items
  for i in range(len(items)/4):
    times.append(float(items[i*4+3]))

  allTimes.append(times)
  allTimesArr = numpy.append(allTimesArr, times)

fig=figure()
ax1=fig.add_subplot(111)
bp=boxplot(allTimes)
setp(range(11,40))
xlabel('case ID')
ylabel('registration time, sec')
show()

print 'Total number of registrations: ',len(allTimesArr)
print 'Mean: ',numpy.mean(allTimesArr)
print 'Max: ',numpy.max(allTimesArr)
print 'Min: ',numpy.min(allTimesArr)
print 'STD: ',numpy.std(allTimesArr)

'''
