from pathlib import Path
from context import finder

vtt_path = r"C:\Users\rmena\Desktop\dev\content-creation\discovery\test3.es.vtt"
vtt_path = str(Path(vtt_path))
result = finder.find_candidates(vtt_path)

# fmt:off
from pprint import pprint
pprint(result)

import pdb; pdb.set_trace()
# fmt: on
