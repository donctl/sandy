import argparse    
from sandy.sandy import Sandy

# Handling command line arguments
parser = argparse.ArgumentParser(prog="main.py")
#parser.add_argument("-G", action="store_true", help="start the GUI (wxPython)")
#parser.add_argument("-C", action="store_true", help="start the interactive console mode")
parser.add_argument("-p", action="store", required=True, metavar="project_name", help="The name of the actual project")

args = parser.parse_args()

Sandy._settings['projectname']=args.p
sandy = Sandy()
sandy.start_console()

#if (args.C):
#    console = Console()
#    console.run()
#elif (args.G):
#     print "XX"

