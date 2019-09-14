
def read_datafile(filename):
  """ read datafile and make an object which is a dictionary of lists 
  it also returns the list of keys in the same order they appears in the file"""
  file_in=open(filename,"r")
  s = file_in.readline()
  nlist = s.split()
  if (nlist[0]=='#'):
    nlist.pop(0)
  nlength = len(nlist)
  data = {}
  for name in nlist:
    data[name] = []
  for line in file_in:
    l = line.strip().split()
    for n in range(nlength):
      try:
        data[nlist[n]].append(float(l[n]))
      except:
        data[nlist[n]].append(l[n])
  print("Datafile %s has %s sets of data. Each one with %s points" %(filename,len(nlist),len(data[nlist[0]])))
  return data,nlist

def parsing_properties(filename,indicator_name,property_names):
  """ returning a dictionary of lists. The keys of the dictionary are the property_names """
  file_in=open(filename,"r")
  data = {}
  for property in property_names:
    l = []
    for line in file_in:
      line = line.strip().split()
      if property in line:
        l.append(float(line[4]))
    data[property] = l
    file_in.seek(0)
  file_in.close()
  return data

def print_datafile(filename,data):
  """ print datafile from a dictionary of lists """
  file_out=open(filename,"w")
  l = list(data.keys())
  list_length = len(data[l[0]])
  print("# ",file=file_out,end="")
  for key in l: 
    print(key,file=file_out,end="\t\t") 
  print(" ",file=file_out)
  print("LUNGHEZZA LISTA",list_length)
  for i in range(0,list_length):
    for key in l: 
      print("%12.6f"% float (data[key][i]),file=file_out, end="\t") 
    print("",file=file_out)


