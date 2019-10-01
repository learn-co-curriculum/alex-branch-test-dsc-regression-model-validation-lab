import json
import os
import subprocess
from git import Repo, Git, GitCommandError
import sys

print('Heyyyyyyyyyyyyyyyyyyyyyyyy')
print(os.getcwd())
repo = Repo(os.getcwd())
