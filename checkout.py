#!/usr/bin/python3
import argparse, os

def setupArgparse(branches):
    parser = argparse.ArgumentParser(description="Checkout or remove branches (via git worktree) listed in branches.txt. Every checkout creates a git worktree in src/ and a deploy worktree in deploy/", prefix_chars='-+')
    parser.add_argument("--deploy", action="store_true", help="set deploy branches to current status")

    # automatically create flags from branches.txt
    for branch in branches:
        splitted = branch.split("_")
        shortform = ""
        for word in splitted:
            shortform += word[0]
        # flag to checkout a branch + deploy branch
        parser.add_argument("+{}".format(shortform), "++{}".format(branch), help="checkout {} in src & deploy branch".format(branch), action="store_const", const=1, default=0)    
        # flag to remove a branch + deploy branch
        parser.add_argument("-{}".format(shortform), "--{}".format(branch), help="remove {} in src & deploy branch".format(branch), action="store_const", const=2, default=0)
    return parser.parse_args()


def createDeployBranch(branch_name):
    cmd = "cd src/{} ; git checkout -b {}_deploy ; git checkout {} ; cd .. ; cd ..; git worktree add deploy/{}_deploy".format(branch_name, branch_name, branch_name, branch_name)
    os.system(cmd)


def updateDeployBranches():
    os.chdir("src")
    my_branches = os.listdir(os.getcwd())
    for branch in my_branches:
        cmd = "cd {} && git pull".format(branch)
        os.system(cmd)

    os.chdir("../deploy")
    my_deploy_branches = os.listdir(os.getcwd())
    for deploy_branch in my_deploy_branches:
        parent_branch = deploy_branch[:-7]
        cmd = "cd {} ; git rebase {}".format(deploy_branch, parent_branch)
        os.system(cmd)
    os.chdir("..")    


def handleFlags(flags, branches):
    if flags["deploy"]:
        # update deploy branches  
        updateDeployBranches()

    for branch_name in branches:
        # checkout branches and create local deploy branches
        if flags[branch_name] == 1:   
            cmd = "git worktree add src/{}".format(branch_name)
            os.system(cmd)
            # create local deploy branch
            createDeployBranch(branch_name)

        # remove branches
        if flags[branch_name] == 2: 
            cmd = "git worktree remove {} ; git worktree remove {}_deploy".format(branch_name, branch_name)
            os.system(cmd)    

           
def main():
    branches = open("branches", "r").read().splitlines()
    args = setupArgparse(branches)
    # arguments to dict
    flags = vars(args)
    handleFlags(flags, branches)

    
if __name__ == '__main__':
    main()
