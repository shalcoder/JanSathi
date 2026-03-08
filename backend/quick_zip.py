import os
import shutil
import zipfile

def create_quick_zip():
    """Create minimal Lambda zip for deployment"""
    print("Creating quick minimal Lambda package...")
    
    zip_name = "function-minimal.zip"
    
    # Remove existing zip if present
    if os.path.exists(zip_name):
        os.remove(zip_name)
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add main handler
        if os.path.exists("lambda_handler.py"):
            zipf.write("lambda_handler.py")
            print("Added: lambda_handler.py")
        
        # Add directories
        for root_dir in ["app", "agentcore", "agents", "agentic_engine"]:
            if os.path.exists(root_dir):
                for root, dirs, files in os.walk(root_dir):
                    # Skip pycache
                    dirs[:] = [d for d in dirs if d != '__pycache__']
                    for file in files:
                        if not file.endswith('.pyc'):
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path)
                            zipf.write(file_path, arcname)
                print(f"Added directory: {root_dir}")
        
        # Add .env if exists
        if os.path.exists(".env"):
            zipf.write(".env")
            print("Added: .env")
    
    size_mb = os.path.getsize(zip_name) / (1024 * 1024)
    print(f"✅ Created {zip_name} ({size_mb:.2f} MB)")
    print("Note: This minimal zip doesn't include external dependencies.")
    print("AWS Lambda layer or runtime should provide boto3, requests, etc.")

if __name__ == "__main__":
    create_quick_zip()