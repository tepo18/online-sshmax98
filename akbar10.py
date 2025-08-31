#!/bin/bash

CYAN="\e[36m"
GREEN="\e[32m"
YELLOW="\e[33m"
RESET="\e[0m"

BASE_PATH="$HOME"
DOWNLOAD_DIR="/sdcard/Download/Akbar98"

# Set Git username and email globally
git config --global user.name "tepo18"
git config --global user.email "tepo18@example.com"
git config --global credential.helper store

echo -e "${CYAN}Have you already cloned the repo?${RESET}"
echo "1) No, clone a new repo"
echo "2) Yes, repo already cloned"
echo -ne "${CYAN}Enter choice (1 or 2): ${RESET}"
read -r CLONE_CHOICE

if [ "$CLONE_CHOICE" == "1" ]; then
    echo -ne "${CYAN}Enter GitHub repo name (e.g. reza-shah1320): ${RESET}"
    read -r REPO_NAME
    REPO_PATH="$BASE_PATH/$REPO_NAME"

    if [ -d "$REPO_PATH" ]; then
        echo -e "${YELLOW}Folder '$REPO_PATH' already exists!${RESET}"
    else
        echo -e "${GREEN}Cloning repo from GitHub...${RESET}"
        git clone "https://github.com/tepo18/$REPO_NAME.git" "$REPO_PATH"
        if [ $? -ne 0 ]; then
            echo -e "${YELLOW}Failed to clone repo. Exiting.${RESET}"
            exit 1
        fi
    fi

elif [ "$CLONE_CHOICE" == "2" ]; then
    echo -ne "${CYAN}Enter existing repo folder name: ${RESET}"
    read -r REPO_NAME
    REPO_PATH="$BASE_PATH/$REPO_NAME"

    if [ ! -d "$REPO_PATH" ]; then
        echo -e "${YELLOW}Folder '$REPO_PATH' not found! Exiting.${RESET}"
        exit 1
    fi
else
    echo -e "${YELLOW}Invalid choice. Exiting.${RESET}"
    exit 1
fi

cd "$REPO_PATH" || { echo -e "${YELLOW}Cannot enter repo folder. Exiting.${RESET}"; exit 1; }

# ===== GitHub Credential Setup =====
if ! grep -q "github.com" ~/.git-credentials 2>/dev/null; then
    echo -ne "${CYAN}Enter your GitHub username: ${RESET}"
    read -r GIT_USER
    echo -ne "${CYAN}Enter your GitHub token (not password!): ${RESET}"
    read -rs GIT_PASS
    echo
    echo "https://$GIT_USER:$GIT_PASS@github.com" >> ~/.git-credentials
    echo -e "${GREEN}Credentials saved permanently.${RESET}"
else
    echo -e "${GREEN}Using saved GitHub credentials from ~/.git-credentials${RESET}"
fi

while true; do
    echo -e "\n${CYAN}Select an option:${RESET}"
    echo "1) Create new file"
    echo "2) Edit existing file"
    echo "3) Delete a file"
    echo "4) Commit changes"
    echo "5) Push to GitHub (with sublinks)"
    echo "6) Copy content from download folder to repo file"
    echo "7) Run checker scripts"
    echo "8) Rename files / change file extensions"
    echo "9) Exit"
    echo -ne "${CYAN}Choice: ${RESET}"
    read -r CHOICE

    case $CHOICE in
        1)
            echo -ne "${CYAN}Enter new filename to create: ${RESET}"
            read -r NEWFILE
            if [ -e "$NEWFILE" ]; then
                echo -e "${YELLOW}File already exists.${RESET}"
            else
                touch "$NEWFILE"
                echo -e "${GREEN}File '$NEWFILE' created.${RESET}"
            fi
            ;;
        2)
            echo -ne "${CYAN}Enter filename to edit: ${RESET}"
            read -r EDITFILE
            if [ ! -e "$EDITFILE" ]; then
                echo -e "${YELLOW}File does not exist.${RESET}"
            else
                nano "$EDITFILE"
            fi
            ;;
        3)
            echo -ne "${CYAN}Enter filename to delete: ${RESET}"
            read -r DELFILE
            if [ ! -e "$DELFILE" ]; then
                echo -e "${YELLOW}File does not exist.${RESET}"
            else
                rm -i "$DELFILE"
                echo -e "${GREEN}File deleted.${RESET}"
            fi
            ;;
        4)
            git status
            echo -ne "${CYAN}Enter commit message (leave empty for default): ${RESET}"
            read -r MSG
            git add .
            if [ -z "$MSG" ]; then
                MSG="auto update from script"
            fi
            git commit -m "$MSG" && echo -e "${GREEN}Changes committed.${RESET}" || echo -e "${YELLOW}Nothing to commit.${RESET}"
            ;;
        5)
            echo -ne "${CYAN}Push changes to GitHub? (yes/no): ${RESET}"
            read -r PUSH_ANSWER
            if [ "$PUSH_ANSWER" == "yes" ]; then
                if git rev-parse --git-dir >/dev/null 2>&1; then
                    REBASE_STATE=$(git rev-parse --git-dir)/rebase-merge
                    if [ -d "$REBASE_STATE" ]; then
                        echo -e "${YELLOW}Detected ongoing rebase. Aborting it...${RESET}"
                        git rebase --abort
                    fi
                fi

                branch_name=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
                if [ "$branch_name" = "HEAD" ] || [ -z "$branch_name" ]; then
                    branch_name="auto-push-branch"
                    git switch -c "$branch_name"
                fi

                git add -A
                echo -ne "${CYAN}Enter commit message (leave empty for default): ${RESET}"
                read -r MSG
                if [ -z "$MSG" ]; then
                    MSG="auto update from script"
                fi
                git commit -m "$MSG" --allow-empty
                git push "https://github.com/tepo18/$REPO_NAME.git" --force && echo -e "${GREEN}Pushed successfully.${RESET}" || echo -e "${YELLOW}Push failed.${RESET}"

                echo "" > links.md
                CHANGED_FILES=$(git diff --name-only HEAD~1)
                for FILE in $CHANGED_FILES; do
                    RAW_URL="https://raw.githubusercontent.com/tepo18/$REPO_NAME/main/$FILE"
                    echo "$RAW_URL" >> links.md
                done
                LAST_LINK=$(tail -n 1 links.md)
                if [ -n "$LAST_LINK" ]; then
                    echo "$LAST_LINK" | termux-clipboard-set
                    echo -e "${CYAN}Last sublink copied to clipboard:${RESET} $LAST_LINK"
                fi
                echo -e "${GREEN}All sublinks saved in links.md.${RESET}"
            else
                echo "Push canceled."
            fi
            ;;
        6)
            echo -ne "${CYAN}Enter source filename inside download folder ($DOWNLOAD_DIR): ${RESET}"
            read -r SRCFILE
            SRC_PATH="$DOWNLOAD_DIR/$SRCFILE"
            if [ ! -f "$SRC_PATH" ]; then
                echo -e "${YELLOW}Source file '$SRC_PATH' not found.${RESET}"
                continue
            fi
            echo -ne "${CYAN}Enter target filename inside repo folder: ${RESET}"
            read -r TARGETFILE
            cat "$SRC_PATH" > "$TARGETFILE"
            echo -e "${GREEN}Content from '$SRC_PATH' copied to '$TARGETFILE'.${RESET}"
            ;;
        7)
            echo -e "${CYAN}Select which checker to run:${RESET}"
            echo "1) chek.py (repo: sab-vip10)"
            echo "2) chek1.py (repo: sab-vip10)"
            echo "3) chek.py (repo: reza-shah1320)"
            echo -ne "${CYAN}Choice: ${RESET}"
            read -r CHEK_CHOICE

            case $CHEK_CHOICE in
                1)
                    if [ -f "./chek.py" ]; then
                        echo -e "${GREEN}Running chek.py from sab-vip10...${RESET}"
                        python3 ./chek.py
                    else
                        echo -e "${YELLOW}chek.py not found in repo.${RESET}"
                    fi
                    ;;
                2)
                    if [ -f "./chek1.py" ]; then
                        echo -e "${GREEN}Running chek1.py from sab-vip10...${RESET}"
                        python3 ./chek1.py
                    else
                        echo -e "${YELLOW}chek1.py not found in repo.${RESET}"
                    fi
                    ;;
                3)
                    if [ -f "./chek.py" ]; then
                        echo -e "${GREEN}Running chek.py from reza-shah1320...${RESET}"
                        python3 ./chek.py
                    else
                        echo -e "${YELLOW}chek.py not found in repo.${RESET}"
                    fi
                    ;;
                *)
                    echo -e "${YELLOW}Invalid choice!${RESET}"
                    ;;
            esac
            ;;
        8)
            echo -e "${CYAN}Rename files / change file extensions:${RESET}"
            echo -ne "${CYAN}Enter current filename: ${RESET}"
            read -r CURRENT
            if [ ! -e "$CURRENT" ]; then
                echo -e "${YELLOW}File not found.${RESET}"
                continue
            fi
            echo -ne "${CYAN}Enter new filename (with optional new extension): ${RESET}"
            read -r NEWNAME
            mv "$CURRENT" "$NEWNAME" && echo -e "${GREEN}Renamed to '$NEWNAME'.${RESET}" || echo -e "${YELLOW
