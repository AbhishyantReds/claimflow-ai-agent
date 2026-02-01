"""
Verify Docker setup is ready
"""
import os
from pathlib import Path


def check_file_exists(filepath: str, description: str) -> bool:
    """Check if file exists"""
    exists = Path(filepath).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists


def check_directory_exists(dirpath: str, description: str) -> bool:
    """Check if directory exists"""
    exists = Path(dirpath).exists() and Path(dirpath).is_dir()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {dirpath}")
    return exists


def main():
    print("="*60)
    print("DOCKER SETUP VERIFICATION")
    print("="*60)
    
    all_good = True
    
    print("\n📦 Docker Configuration Files:")
    all_good &= check_file_exists("Dockerfile", "Dockerfile")
    all_good &= check_file_exists("docker-compose.yml", "Docker Compose")
    all_good &= check_file_exists("docker-entrypoint.sh", "Entrypoint Script")
    all_good &= check_file_exists(".dockerignore", "Docker Ignore")
    all_good &= check_file_exists("Makefile", "Makefile")
    
    print("\n📋 Configuration Files:")
    all_good &= check_file_exists("requirements.txt", "Requirements")
    all_good &= check_file_exists(".env.example", "Environment Example")
    
    has_env = check_file_exists(".env", "Environment (actual)")
    if not has_env:
        print("   ⚠️  Copy .env.example to .env and add your OPENAI_API_KEY")
    
    print("\n📂 Required Directories:")
    all_good &= check_directory_exists("data", "Data Directory")
    all_good &= check_directory_exists("data/policies", "Policy Documents")
    all_good &= check_directory_exists("agent", "Agent Code")
    all_good &= check_directory_exists("database", "Database Module")
    all_good &= check_directory_exists("ui", "UI Module")
    all_good &= check_directory_exists("scripts", "Scripts")
    
    print("\n📄 Documentation:")
    check_file_exists("docs/DOCKER.md", "Docker Guide")
    check_file_exists("docs/RAG_DOCUMENTATION.md", "RAG Documentation")
    
    print("\n📊 Data Files:")
    db_exists = check_file_exists("data/claimflow.db", "SQLite Database")
    chroma_exists = check_directory_exists("data/chroma_db", "ChromaDB")
    
    if not db_exists:
        print("   ℹ️  Run: python scripts/init_database.py --reset --seed")
    
    if not chroma_exists:
        print("   ℹ️  Run: python scripts/ingest_policies.py")
    
    print("\n" + "="*60)
    
    if all_good and has_env:
        print("✅ DOCKER SETUP COMPLETE!")
        print("\nQuick Start:")
        print("  1. Ensure Docker is running")
        print("  2. Set OPENAI_API_KEY in .env file")
        print("  3. Run: docker-compose up -d")
        print("  4. Access: http://localhost:7860")
        print("\nOr use Make commands:")
        print("  make up      - Start application")
        print("  make logs    - View logs")
        print("  make shell   - Open shell")
    else:
        print("❌ SETUP INCOMPLETE")
        print("\nMissing components detected. Please fix the issues above.")
    
    print("="*60)


if __name__ == "__main__":
    main()
