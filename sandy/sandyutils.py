def print_params(params):
  padding = 15
  print "\nAvailable parameters\n"
  for paramname, paramvalues in params.iteritems():
	print '\033[1m'+"["+str(paramname)+"]"+'\033[0m'
	#print "[%s]"%paramname
	for key, value in paramvalues.iteritems():
		l = padding - len(key)
		s = "\t%s:"%key
		for i in range(l):
		  s = s+" "
		s = s+str(value)
		print s
  print ""
  return

def set_params(params):
  paramnames = params.keys()
  paramnames.append("")
  pn="X"
  while (pn != ""):
    pn = raw_input('Name of the parameter or ENTER to continue: ')
    while not (pn in paramnames):
	pn = raw_input('Name of the parameter or ENTER to continue: ')
  
    if (pn != ""):
  	print "Set new value for [ %s ]: "%pn
  	pv = raw_input()
  	params[pn]['value']=pv

  return

