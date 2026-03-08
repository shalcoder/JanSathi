import os
import re

def migrate_to_cognito():
    src_dir = 'src'
    replaced_count = 0
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if not file.endswith('.tsx') and not file.endswith('.ts'):
                continue
                
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Replace imports
            content = re.sub(r"import\s+\{\s*useAuth\s*\}\s+from\s+['\"]@clerk/clerk-react['\"];", "import { useAuth } from '@/hooks/useAuth';", content)
            content = re.sub(r"import\s+\{\s*useUser\s*\}\s+from\s+['\"]@clerk/clerk-react['\"];", "import { useAuth } from '@/hooks/useAuth';", content)
            content = re.sub(r"import\s+\{\s*useAuth\s*,\s*useUser\s*\}\s+from\s+['\"]@clerk/clerk-react['\"];", "import { useAuth } from '@/hooks/useAuth';", content)
            content = re.sub(r"import\s+\{\s*useUser\s*,\s*useAuth\s*\}\s+from\s+['\"]@clerk/clerk-react['\"];", "import { useAuth } from '@/hooks/useAuth';", content)
            
            # Replace function calls
            content = re.sub(r"const\s+\{\s*user\s*(?:,\s*isLoaded)?\s*\}\s*=\s*useUser\(\);", "const { user, loading: isLoaded } = useAuth();", content)
            content = re.sub(r"const\s+\{\s*getToken\s*\}\s*=\s*useAuth\(\);", "const { user, loading: isLoaded } = useAuth();\n    const getToken = async () => 'mock-token';", content)
            
            # Additional cleanup of getToken references 
            content = content.replace("const { getToken, isLoaded: isAuthLoaded } = useAuth();", "const { loading: isAuthLoaded } = useAuth();\n    const getToken = async () => 'mock-token';")
            content = content.replace("const { getToken } = useAuth();", "const getToken = async () => 'mock-token';")
            
            if content != original_content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated {path}")
                replaced_count += 1
                
    print(f"Updated {replaced_count} files.")

if __name__ == '__main__':
    migrate_to_cognito()
