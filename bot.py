import os
import random
import subprocess
import string
from datetime import datetime
from github import Github

# Config
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Random number of commits each day
commit_count = random.randint(8, 20)

def run(cmd):
    print(f"$ {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def random_suffix(length=6):
    """Generate a random string for commit variation"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def create_daily_file(commit_count):
    """Create a daily file with randomized commits"""
    today_str = datetime.utcnow().strftime("%Y%m%d")
    filename = f"bot_day_{today_str}.txt"
    with open(filename, "w") as f:
        for i in range(commit_count):
            f.write(f"Daily auto commit {i} — {random_suffix()}\n")
    run(f"git add {filename}")
    run(f"git commit -m 'Daily auto commits for {today_str}'")
    return filename

def update_master_file(commit_count):
    """Append today's commits to bot_master.txt"""
    master_file = "bot_master.txt"
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    with open(master_file, "a") as f:
        for i in range(commit_count):
            f.write(f"{today_str} — Daily auto commit {i} — {random_suffix()}\n")
    run(f"git add {master_file}")
    run(f"git commit -m 'Update master file for {today_str}'")

def update_log(commit_count):
    """Append today's summary to bot_log.txt"""
    log_file = "bot_log.txt"
    today = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    entry = f"{today} — {commit_count} commits added.\n"
    with open(log_file, "a") as f:
        f.write(entry)
    run(f"git add {log_file}")
    run(f"git commit -m 'Update log for {today}'")

def main():
    branch_name = "bot-commits"

    # Setup git identity
    run("git config --global user.name 'github-bot'")
    run("git config --global user.email 'bot@example.com'")

    # Ensure latest main
    run("git fetch origin")
    run("git checkout main")
    run("git pull origin main")

    # Switch to bot branch (create if missing)
    try:
        run(f"git checkout {branch_name}")
    except:
        run(f"git checkout -b {branch_name}")

    # Create daily file with randomized commits
    create_daily_file(commit_count)

    # Update master summary file
    update_master_file(commit_count)

    # Update log file
    update_log(commit_count)

    # Push changes
    run(f"git push origin {branch_name}")

    # GitHub API
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)

    # Rolling PR
    prs = repo.get_pulls(state="open", head=f"{repo.owner.login}:{branch_name}")
    if prs.totalCount > 0:
        pr = prs[0]
        pr.edit(body=f"Rolling PR — added {commit_count} commits today.")
    else:
        pr = repo.create_pull(
            title="Rolling Daily Bot Commits",
            body=f"Started with {commit_count} commits today.",
            head=branch_name,
            base="main"
        )

    # Review + merge
    pr.create_review(body="Automated approval ✅", event="APPROVE")
    pr.merge(merge_method="squash")

if __name__ == "__main__":
    main()
