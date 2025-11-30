# Introduction
This reporepository is split from ```https://github.com/EfiPy/EfiPy2``` with following git command
```
$ git log -1
commit 5ded62bd1c8ebf335248b3812a8467f5b762779a (HEAD -> main, origin/main, origin/HEAD, Yesterday)
Author: MaxWu <EfiPy.Core@gmail.com>
Date:   Sat Nov 29 10:20:11 2025 +0800

    Correct TCG_SPDM strings
$
$ git subtree split --prefix=Efi/Apps/ -b EfiPy2Apps
Created branch 'EfiPy2Apps'
222ffeb0de3cd6e4f8935bebf1ea565544bde9e2
$
$ git switch EfiPy2Apps
Switched to branch 'EfiPy2Apps'
$
$ git branch -d main
warning: deleting branch 'main' that has been merged to
         'refs/remotes/origin/main', but not yet merged to HEAD
Deleted branch main (was 5ded62b).
$
$ git branch -m main
$
$ git remote set-url origin git@github.com:EfiPy/EfiPy2Apps.git
$
$ rm -rf Network/
$
$ git add Network
$
$ git commit -m "Rmove non-used folder"
[main cc24465] Rmove non-used folder
 4 files changed, 4 insertions(+), 1 deletion(-)
 create mode 100644 .gitmodules
 delete mode 160000 Network
 rename {EfiPy2Sample => NetworkApps}/ifconfig4.py (100%)
 create mode 160000 SimpleFileRemoteCopy
$
$ git submodule add git@github.com:EfiPy/SimpleFileRemoteCopy.git SimpleFileRemoteCopy
Cloning into 'D:/code/EfiPyLab/EfiPy2_Pub/EfiPy2Apps/SimpleFileRemoteCopy'...
remote: Enumerating objects: 22, done.
remote: Counting objects: 100% (22/22), done.
remote: Compressing objects: 100% (18/18), done.
remote: Total 22 (delta 6), reused 17 (delta 4), pack-reused 0 (from 0)
Receiving objects: 100% (22/22), 4.67 KiB | 4.67 MiB/s, done.
Resolving deltas: 100% (6/6), done.
warning: in the working copy of '.gitmodules', LF will be replaced by CRLF the next time Git touches it
$
$ mkdir NetworkApps
$
$ git mv EfiPy2Sample/ifconfig4.py NetworkApps/
```