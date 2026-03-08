"""
Quick verification script for Knowledge Base implementation.
Run this to check if everything is set up correctly.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_imports():
    """Verify all required imports work."""
    print("🔍 Checking imports...")
    
    try:
        from app.services.knowledge_base_service import KnowledgeBaseService
        print("  ✅ KnowledgeBaseService imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import KnowledgeBaseService: {e}")
        return False
    
    try:
        from app.api.knowledge_base_routes import kb_bp
        print("  ✅ knowledge_base_routes imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import knowledge_base_routes: {e}")
        return False
    
    try:
        from app.models.models import BedrockQueryCache
        print("  ✅ BedrockQueryCache model imported successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import BedrockQueryCache: {e}")
        return False
    
    return True


def check_env_vars():
    """Check if required environment variables are set."""
    print("\n🔍 Checking environment variables...")
    
    required_vars = [
        'AWS_REGION',
        'BEDROCK_KB_ID',
        'BEDROCK_KB_S3_BUCKET'
    ]
    
    optional_vars = [
        'KB_CACHE_TTL',
        'KB_ENABLE_CACHE'
    ]
    
    all_set = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            display_value = value if var not in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY'] else '***'
            print(f"  ✅ {var} = {display_value}")
        else:
            print(f"  ⚠️  {var} not set (required)")
            all_set = False
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var} = {value}")
        else:
            print(f"  ℹ️  {var} not set (optional, will use default)")
    
    return all_set


def check_database():
    """Check if database table exists."""
    print("\n🔍 Checking database...")
    
    try:
        from app.models.models import db, BedrockQueryCache
        from flask import Flask
        
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/jansathi.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # Check if table exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'bedrock_query_cache' in tables:
                print("  ✅ BedrockQueryCache table exists")
                
                # Check table structure
                columns = [col['name'] for col in inspector.get_columns('bedrock_query_cache')]
                expected_columns = ['id', 'query', 'context_hash', 'response_json', 'language', 'created_at']
                
                missing = set(expected_columns) - set(columns)
                if missing:
                    print(f"  ⚠️  Missing columns: {missing}")
                else:
                    print(f"  ✅ All required columns present: {len(columns)} columns")
                
                return True
            else:
                print("  ⚠️  BedrockQueryCache table not found")
                print("     Run: python main.py (will auto-create tables)")
                return False
                
    except Exception as e:
        print(f"  ⚠️  Database check failed: {e}")
        print("     This is normal if you haven't run the app yet")
        return False


def check_files():
    """Check if all required files exist."""
    print("\n🔍 Checking files...")
    
    files = [
        'app/services/knowledge_base_service.py',
        'app/api/knowledge_base_routes.py',
        'docs/knowledge_base_caching.md',
        'docs/kb_quick_start.md',
        'test_knowledge_base.py',
        'KNOWLEDGE_BASE_IMPLEMENTATION.md'
    ]
    
    all_exist = True
    for file in files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"  ✅ {file} ({size:,} bytes)")
        else:
            print(f"  ❌ {file} not found")
            all_exist = False
    
    return all_exist


def check_blueprint_registration():
    """Check if blueprint is registered in main.py."""
    print("\n🔍 Checking blueprint registration...")
    
    try:
        with open('main.py', 'r') as f:
            content = f.read()
            
        if 'knowledge_base_routes' in content and 'kb_bp' in content:
            print("  ✅ Knowledge Base blueprint registered in main.py")
            return True
        else:
            print("  ❌ Knowledge Base blueprint not registered in main.py")
            return False
    except Exception as e:
        print(f"  ❌ Failed to check main.py: {e}")
        return False


def print_summary(results):
    """Print summary of checks."""
    print("\n" + "="*60)
    print("  VERIFICATION SUMMARY")
    print("="*60)
    
    total = len(results)
    passed = sum(results.values())
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check}")
    
    print(f"\nScore: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Your Knowledge Base implementation is ready.")
        print("\nNext steps:")
        print("1. Set up Bedrock Knowledge Base in AWS Console")
        print("2. Update .env with BEDROCK_KB_ID and BEDROCK_KB_S3_BUCKET")
        print("3. Run: python main.py")
        print("4. Test: python test_knowledge_base.py")
    else:
        print("\n⚠️  Some checks failed. Please review the issues above.")
        print("\nCommon fixes:")
        print("- Run 'python main.py' to create database tables")
        print("- Copy .env.example to .env and configure")
        print("- Install missing dependencies: pip install -r requirements.txt")


def main():
    """Run all verification checks."""
    print("="*60)
    print("  Knowledge Base Implementation Verification")
    print("="*60)
    
    results = {
        'Imports': check_imports(),
        'Files': check_files(),
        'Blueprint Registration': check_blueprint_registration(),
        'Environment Variables': check_env_vars(),
        'Database': check_database()
    }
    
    print_summary(results)


if __name__ == '__main__':
    main()
