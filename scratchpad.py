# used for playing with random dev code

#%%

import re

url = 'http://34.73.124.145:19999/host/devml/#menu_ml_detector_info;after=1630005942000;before=1630006622000;theme=slate'
#url = 'http://34.73.124.145:19999/#menu_ml_detector_info;after=1630005942000;before=1630006622000;theme=slate'

child_host = re.search('/host/(.*)/', url)
child_host = child_host.group(1) if child_host else None

print(child_host)


#%%

#%%