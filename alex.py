import json
import os
import subprocess
import sys

import time

# CONSTANTS
SOLUTION_TAG = "__SOLUTION__"
CURRICULUM_BRANCH = "curriculum"
MASTER_BRANCH = "master"
SOLUTION_BRANCH = "solution"
CUSTOM_COMMIT_MSG_FLAG = "-m"
REPO_DIR_NAME = "tmp"

# FUNCTIONS

def get_notebook_json(filename="index.ipynb"):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def is_markdown_cell(cell):
    return cell["cell_type"] == "markdown"


def contains_tag(line):
    # returns true for '# __SOLUTION__' or '#__SOLUTION__'
    return any(tag in line.strip().split(" ") for tag in [SOLUTION_TAG, f"#{SOLUTION_TAG}"])


def is_solution_cell(cell):
    if cell["cell_type"] != "code":
        return False

    # does any line of the cell have the SOLUTION tag anywhere in it
    found_tag = [True for line in cell["source"] if contains_tag(line)]

    return bool(len(found_tag))


# removes __SOLUTON__ line from tagged code cells
def untag(cell):
    if cell["cell_type"] != "code":
        return cell

    source = [line for line in cell["source"] if not contains_tag(line)]

    cell.update({"source": source})
    return cell


def create_master_notebook(nb):
    cells = [
        cell for cell in nb["cells"] if for_master(cell)
    ]

    nb.update({"cells": cells})
    return nb


def for_master(cell):
    return is_markdown_cell(cell) or not is_solution_cell(cell)


def for_sol(cell):
    return is_markdown_cell(cell) or is_solution_cell(cell)


def create_sol_notebook(nb):
    cells = [
        untag(cell) for cell in nb["cells"] if for_sol(cell)
    ]

    nb.update({"cells": cells})
    return nb

def write_new_notebook(notebook):
    f = open("index.ipynb", "w")
    f.write(json.dumps(notebook))
    f.close()

def notebook_to_markdown():
    os.system("jupyter nbconvert index.ipynb --to markdown")
    os.system("mv index.md README.md")


# def sync_branch(repo, branch, notebook, msg="Curriculum Auto-Sync"):
def sync_branch(branch, notebook, msg="Curriculum Auto-Sync"):
    # switch to branch, do nothing if does not exist
    try:
        checkout(branch)
        branch_exists = True
    except GitCommandError:
        print(f"{branch} branch DNE")
        branch_exists = False

    if branch_exists:
        # get all files from curriculum branch and put onto this branch,
        # (the notebook and readme will be overwritten in the subsequent steps)
        # Interesting use of the `checkout` command
        # https://superuser.com/questions/692794/how-can-i-get-all-the-files-from-one-git-branch-and-put-them-into-the-current-b/1431858#1431858
        os.system(f"git checkout ${CURRICULUM_BRANCH} .")

        # # delete current images, they'll be regenerated along with the notebook
        # os.system("rm -rf index_files")
        #
        # # write index.ipynb
        # write_new_notebook(notebook)
        #
        # # generate markdown
        # notebook_to_markdown()

        # add, commit, push
        add_and_commit(msg)
        push(branch)

def add_and_commit(commit_msg):
    os.system("git add .")
    os.system(f"git commit -m \"{commit_msg}\"")

def push(branch):
    os.system(f"git push origin {branch}")

def checkout(branch):
    os.system(f"git checkout --track origin/{branch}")

# RUN
# ======================

# os.system(f"git clone https://{os.environ['GITHUB_TOKEN']}@github.com/{os.environ['GITHUB_REPOSITORY']}.git {REPO_DIR_NAME}")
# os.system(f"cd {REPO_DIR_NAME}")

# os.system("pwd")
# os.system("ls .")
# Identity
# git_ssh_identity_file = os.path.expanduser('~/.ssh/id_rsa')
# git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file
# Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd)
# os.system(f"git config --list")
# os.system(f"git config --list")
# git remote add origin https://scuzzlebuzzle:<MYTOKEN>@github.com/scuzzlebuzzle/ol3-1.git

# repo = Repo(os.getcwd())
# repo = Repo(os.environ['GITHUB_WORKSPACE'])
# commit_message = repo.head.commit.message
# os.system(f"git config github.token {os.environ['GITHUB_TOKEN']}")
# os.system(f"git config user.name {os.environ['GITHUB_ACTOR']}")
# os.system(f"git remote set-url origin https://learn-co-curriculum:{os.environ['GITHUB_TOKEN']}@github.com/{os.environ['GITHUB_REPOSITORY']}.git")

# Configure push access using token
# os.system("git remote rm origin")
# os.system(f"git remote add origin https://learn-co-curriculum:{os.environ['GITHUB_TOKEN']}@github.com/{os.environ['GITHUB_REPOSITORY']}.git")
#
# os.system("git remote -v")
# os.system("git branch -a")
try:
    checkout(CURRICULUM_BRANCH)
except GitCommandError:
    raise Exception(f"A branch called {CURRICULUM_BRANCH} must exist")

# checkout(MASTER_BRANCH)
# time = time.time()
# os.system(f"touch {time} && echo hi >> {time}")
# os.system("git add .")
# os.system(f"git commit -m '{time}'")
# os.system("git push origin master")

commit_message = subprocess.check_output(["git", "log", "-1", "--pretty=format:%s"]).decode("utf-8")

notebook_json   = get_notebook_json()
master_notebook = create_master_notebook(dict(notebook_json)) # pass a copy
sol_notebook    = create_sol_notebook(dict(notebook_json)) # pass a copy

sync_branch(MASTER_BRANCH, master_notebook, msg=commit_message)
sync_branch(SOLUTION_BRANCH, sol_notebook, msg=commit_message)
