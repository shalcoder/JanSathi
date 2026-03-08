import os
import shutil
import subprocess
import glob

def create_package():
    print("Starting minimal packaging for AWS Lambda...")
    
    pkg_dir = "lambda_pkg"
    zip_name = "function-minimal"
    
    if os.path.exists(pkg_dir):
        shutil.rmtree(pkg_dir)
    os.makedirs(pkg_dir)
    
    # 1. Install minimal dependencies
    print("Installing requirements-lambda.txt...")
    subprocess.check_call(["pip", "install", "-r", "requirements-lambda.txt", "-t", pkg_dir])
    
    # 2. Copy source code directories
    dirs_to_copy = ["app", "agentcore", "agents", "agentic_engine"]
    for d in dirs_to_copy:
        if os.path.exists(d):
            print(f"Copying directory: {d}")
            shutil.copytree(d, os.path.join(pkg_dir, d), dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))

    # 3. Copy top-level files
    files_to_copy = ["lambda_handler.py", "main.py", ".env"]
    for f in files_to_copy:
        if os.path.exists(f):
            print(f"Copying file: {f}")
            shutil.copy2(f, pkg_dir)

    # 4. Create the ZIP archive
    print("Creating ZIP archive...")
    if os.path.exists(f"{zip_name}.zip"):
        os.remove(f"{zip_name}.zip")
        
    shutil.make_archive(zip_name, 'zip', pkg_dir)
    
    # 5. Clean up
    print("Cleaning up package directory...")
    shutil.rmtree(pkg_dir)
    
    zip_size = os.path.getsize(f"{zip_name}.zip") / (1024 * 1024)
    print(f"Package created successfully: {zip_name}.zip ({zip_size:.2f} MB)")

if __name__ == "__main__":
    create_package()
