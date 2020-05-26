"""

  file_regex_search.py

  Recursive file contents pattern matching, equivelent to something like:
    sudo find / -name "*.sh" | xargs egrep "pass(wd|word)"

"""

import os, re

## where do we start our search?
base_dir = "/"

## filter on filenames?
file_regex = re.compile(r'.*\.sh$')

## what are we looking for in the file?
#content_regex = re.compile(r'\b\w{4}\b')
content_regex = re.compile(r'.*passwo?r?d.*')

## Go find it
for root, dirs, files in os.walk(base_dir):
  for file in filter(lambda f: file_regex.match(f), files):
    #print(file)
    path = os.path.join(root,file)
    with open(path, "r") as fh:
      for line in fh:
        line_matches = content_regex.findall(line)
        for match in line_matches:
          print("%s:  [%s]" % (path, match))
