import os
import subprocess
import shutil

root_dir = r"C:\Users\Ahmed Bilal Khan\Desktop\AssureX Claim Engine\AssureX-Claim-Engine"
frontend_dir = os.path.join(root_dir, "frontend")

# --- 1. Push Frontend ---
print("Handling Frontend...")
# Remove messed up .git if exists
git_dir_frontend = os.path.join(frontend_dir, ".git")
if os.path.exists(git_dir_frontend):
    shutil.rmtree(git_dir_frontend, ignore_errors=True)

# Create proper .gitignore for frontend
with open(os.path.join(frontend_dir, ".gitignore"), "w") as f:
    f.write("node_modules/\ndist/\n.env\n")

# Run git commands
try:
    subprocess.run(["git", "init"], cwd=frontend_dir, check=True)
    subprocess.run(["git", "add", "."], cwd=frontend_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Initial frontend commit"], cwd=frontend_dir, check=True)
    subprocess.run(["git", "branch", "-M", "main"], cwd=frontend_dir, check=True)
    subprocess.run(["git", "remote", "add", "origin", "https://github.com/bkhanzaza551-a11y/assurex-claim-fronted.git"], cwd=frontend_dir, check=True)
    print("Pushing frontend to GitHub...")
    subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=frontend_dir, check=True)
    print("Frontend pushed successfully!")
except Exception as e:
    print(f"Error pushing frontend: {e}")

# --- 2. Push Backend ---
print("\nHandling Backend...")
# Remove messed up .git if exists
git_dir_root = os.path.join(root_dir, ".git")
if os.path.exists(git_dir_root):
    shutil.rmtree(git_dir_root, ignore_errors=True)

# The root .gitignore already ignores frontend/node_modules, but let's make sure it ignores the whole frontend folder to separate repos properly.
with open(os.path.join(root_dir, ".gitignore"), "a") as f:
    f.write("\nfrontend/\nnode_modules/\n")

try:
    subprocess.run(["git", "init"], cwd=root_dir, check=True)
    subprocess.run(["git", "add", "."], cwd=root_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Initial backend commit"], cwd=root_dir, check=True)
    subprocess.run(["git", "branch", "-M", "main"], cwd=root_dir, check=True)
    subprocess.run(["git", "remote", "add", "origin", "https://github.com/bkhanzaza551-a11y/assurex-claim-backend.git"], cwd=root_dir, check=True)
    print("Pushing backend to GitHub...")
    subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=root_dir, check=True)
    print("Backend pushed successfully!")
except Exception as e:
    print(f"Error pushing backend: {e}")
