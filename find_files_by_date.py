#%%
import os
import re
import datetime

#%%

def filetree(top):
    for dirpath, _, fnames in os.walk(top):
        for fname in fnames:
            json_ = "(-t\d\d)*\.json"
            transcript_ = "-t\d\d\.json"
            yield {
                "filename": os.path.join(dirpath, fname),
                "case_id": re.sub(json_, "", fname),
                "type": "transcript"
                if re.search(transcript_, fname)
                else "vote_summary_file",
            }

x = filetree('./data')
# %%
