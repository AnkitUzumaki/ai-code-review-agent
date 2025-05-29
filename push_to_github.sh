#!/bin/bash
cd /home/uzumaki007/ai_code_review_agent
git init
git config --global user.name "AnkitUzumaki"
git config --global user.email "cankit5687@gmail.com"
cp ai.gitignore .gitignore
git add .
git commit -m "Initial push of AI Code Review Agent project"
git remote add origin https://github.com/AnkitUzumaki/ai-code-review-agent.git
git branch -M main
git push -u origin main
