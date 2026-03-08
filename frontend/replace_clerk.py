import os

def replace_clerk_imports():
    src_dir = 'src'
    replaced_count = 0
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.tsx') or file.endswith('.ts'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if '@clerk/clerk-react' in content:
                    content = content.replace('@clerk/clerk-react', '@/lib/clerk-mock')
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated {path}")
                    replaced_count += 1
    
    print(f"Total files updated: {replaced_count}")

if __name__ == '__main__':
    replace_clerk_imports()
