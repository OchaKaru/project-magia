#! /bin/bash

git config --global user.email "school.kalvin.g@gmail.com"
git config --global user.name "Kalvin Garcia"

git add .
git commit

eval "$(ssh-agent -s)"
ssh-add ./sessions/ssh/kalvin_git_key

git push
