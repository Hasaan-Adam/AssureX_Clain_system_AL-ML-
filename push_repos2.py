import os
import subprocess

def run(cmd, cwd):
    print(f"Running: {cmd} in {cwd}")
    res = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    print("STDOUT:", res.stdout)
    if res.stderr:
        print("STDERR:", res.stderr)
    return res.returncode

root_dir = r"C:\Users\Ahmed Bilal Khan\Desktop\AssureX Claim Engine\AssureX-Claim-Engine"
frontend_dir = os.path.join(root_dir, "frontend")

# 1. FRONTEND
print("\n--- FRONTEND ---")
# Reset git completely
run("rmdir /s /q .git", frontend_dir)
# Setup proper ignore
with open(os.path.join(frontend_dir, ".gitignore"), "w") as f:
    f.write("node_modules/\ndist/\n.env\n")

run("git init", frontend_dir)
run("git checkout -b main", frontend_dir)
run("git add .", frontend_dir)
run('git commit -m "Initial Frontend Commit"', frontend_dir)
run("git remote add origin https://github.com/bkhanzaza551-a11y/assurex-claim-fronted.git", frontend_dir)
# Push
run("git push -u origin main --force", frontend_dir)


# 2. BACKEND
print("\n--- BACKEND ---")
run("rmdir /s /q .git", root_dir)
# Setup proper ignore in root to exclude frontend and other big files
with open(os.path.join(root_dir, ".gitignore"), "w") as f:
    f.write("__pycache__/\nvenv/\nnode_modules/\nfrontend/\n*.joblib\n*.db\n")

run("git init", root_dir)
run("git checkout -b main", root_dir)
run("git add .", root_dir)
run('git commit -m "Initial Backend Commit"', root_dir)
run("git remote add origin https://github.com/bkhanzaza551-a11y/assurex-claim-backend.git", root_dir)
# Push
run("git push -u origin main --force", root_dir)

