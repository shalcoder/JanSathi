import os

hooks_file = r'src\hooks\useAuth.ts'
with open(hooks_file, 'r', encoding='utf-8') as f:
    hooks_content = f.read()

if 'fetchAuthSession' not in hooks_content:
    hooks_content = hooks_content.replace(
        "import { getCurrentUser, signOut as amplifySignOut } from 'aws-amplify/auth';",
        "import { fetchAuthSession, getCurrentUser, signOut as amplifySignOut } from 'aws-amplify/auth';"
    )
if 'export const getToken' not in hooks_content:
    hooks_content += '''
export const getToken = async () => {
    try {
        const session = await fetchAuthSession();
        return session.tokens?.idToken?.toString() || session.tokens?.accessToken?.toString() || null;
    } catch {
        return null;
    }
};
'''
with open(hooks_file, 'w', encoding='utf-8') as f:
    f.write(hooks_content)

for root, _, files in os.walk('src'):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            if file == 'useAuth.ts':
                continue
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            modified = False
            if "const getToken = async () => 'mock-token';" in content:
                content = content.replace("const getToken = async () => 'mock-token';", "")
                modified = True
            elif 'const getToken = async () => "mock-token";' in content:
                content = content.replace('const getToken = async () => "mock-token";', "")
                modified = True
            elif "const getToken = async () => 'mock-token'; // or get valid Amplify token here if needed" in content:
                content = content.replace("const getToken = async () => 'mock-token'; // or get valid Amplify token here if needed", "")
                modified = True

            if modified:
                if "import { useAuth } from '@/hooks/useAuth';" in content:
                    content = content.replace("import { useAuth } from '@/hooks/useAuth';", "import { useAuth, getToken } from '@/hooks/useAuth';")
                elif "import { getToken } from" not in content:
                    content = "import { getToken } from '@/hooks/useAuth';\n" + content
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated {path}")
