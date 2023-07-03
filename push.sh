#! /bin/bash

eval "$(ssh-agent -s)"
ssh-add ./sessions/ssh/kalvin_git_key
git 