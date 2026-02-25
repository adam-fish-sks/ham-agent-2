"""
Restart Development Environment Script

This script handles restarting the entire development environment:
- Stops running containers
- Starts PostgreSQL database container
- Runs Prisma migrations
- Starts development servers (Next.js + Express)

Usage:
    python restart_dev.py
"""

import os
import sys
import subprocess
import time


def run_command(command, description, cwd=None, check=True):
    """Run a shell command and print status."""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Running: {command}\n")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            check=check,
            capture_output=False,
            text=True
        )
        print(f"✅ {description} completed")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        if check:
            raise
        return False


def stop_containers():
    """Stop all running Podman containers and Node processes for this project."""
    print("\n" + "="*60)
    print("🛑 Stopping existing containers and Node processes...")
    print("="*60)
    
    # Kill Node processes on ports 3000 and 3001
    try:
        subprocess.run(
            "netstat -ano | findstr :3000 | findstr LISTENING",
            shell=True,
            capture_output=True,
            text=True
        )
        subprocess.run("FOR /F \"tokens=5\" %P IN ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') DO taskkill /F /PID %P", shell=True, capture_output=True)
    except:
        pass
    
    try:
        subprocess.run(
            "netstat -ano | findstr :3001 | findstr LISTENING",
            shell=True,
            capture_output=True,
            text=True
        )
        subprocess.run("FOR /F \"tokens=5\" %P IN ('netstat -ano ^| findstr :3001 ^| findstr LISTENING') DO taskkill /F /PID %P", shell=True, capture_output=True)
    except:
        pass
    
    # Try to stop the PostgreSQL container
    subprocess.run(
        "podman stop ham-agent-2-postgres",
        shell=True,
        capture_output=True
    )
    
    # Give containers time to stop
    time.sleep(2)
    print("✅ Containers stopped")


def start_database():
    """Start the PostgreSQL database container."""
    print("\n" + "="*60)
    print("🚀 Starting PostgreSQL container...")
    print("="*60)
    
    # Check if container exists
    result = subprocess.run(
        "podman ps -a --filter name=ham-agent-2-postgres --format {{.Names}}",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if "ham-agent-2-postgres" in result.stdout:
        # Container exists, just start it
        run_command(
            "podman start ham-agent-2-postgres",
            "Starting existing container"
        )
    else:
        # Create new container
        run_command(
            "podman run -d --name ham-agent-2-postgres "
            "-e POSTGRES_USER=ham_agent_2 "
            "-e POSTGRES_PASSWORD=ham_agent_2_password "
            "-e POSTGRES_DB=ham_agent_2_db "
            "-p 5432:5432 "
            "-v ham-agent-2-postgres-data:/var/lib/postgresql/data "
            "postgres:16-alpine",
            "Creating and starting new PostgreSQL container"
        )
    
    # Wait for database to be ready
    print("\n⏳ Waiting for database to be ready...")
    time.sleep(5)
    print("✅ Database should be ready")


def check_environment():
    """Check and setup environment variables."""
    env_file = os.path.join(os.getcwd(), ".env")
    env_example = os.path.join(os.getcwd(), ".env.example")
    
    if not os.path.exists(env_file):
        print("\n⚠️  .env file not found!")
        
        if os.path.exists(env_example):
            print("📋 Creating .env from .env.example...")
            
            # Copy .env.example to .env
            with open(env_example, 'r') as src:
                content = src.read()
            
            with open(env_file, 'w') as dst:
                dst.write(content)
            
            print("✅ Created .env file")
            print("\n⚠️  IMPORTANT: Update .env with your actual API keys:")
            print("  - WORKWIZE_KEY")
            print("  - AZURE_OPENAI_ENDPOINT")
            print("  - AZURE_OPENAI_API_KEY")
            print("\nThe DATABASE_URL is already configured for local development.")
        else:
            print(f"❌ .env.example not found at {env_example}")
            print("Cannot create .env file")
            return False
    else:
        print("✅ .env file exists")
    
    return True


def run_migrations():
    """Run Prisma migrations."""
    packages_db = os.path.join(os.getcwd(), "packages", "database")
    
    # Load environment variables from .env file
    env_file = os.path.join(os.getcwd(), ".env")
    env_vars = os.environ.copy()
    
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"').strip("'")
                    env_vars[key.strip()] = value
    
    # Run migration with environment variables
    print(f"\n🔍 Using DATABASE_URL: {env_vars.get('DATABASE_URL', 'NOT FOUND')}")
    
    result = subprocess.run(
        "npx prisma migrate deploy",
        shell=True,
        cwd=packages_db,
        env=env_vars,
        capture_output=False
    )
    
    if result.returncode != 0:
        print(f"❌ Running Prisma migrations failed with exit code {result.returncode}")
        raise subprocess.CalledProcessError(result.returncode, "npx prisma migrate deploy")
    
    print("✅ Running Prisma migrations completed")


def start_dev_servers():
    """Start development servers."""
    print("\n" + "="*60)
    print("🚀 Starting development servers...")
    print("="*60)
    print("\n📝 Starting all services with Turbo...")
    print("Press Ctrl+C to stop all servers\n")
    
    # Give user a moment to read
    time.sleep(2)
    
    # Ensure DATABASE_URL is set in environment
    env = os.environ.copy()
    if 'DATABASE_URL' not in env:
        env['DATABASE_URL'] = 'postgresql://ham_agent_2:ham_agent_2_password@localhost:5432/ham_agent_2_db'
    
    # Start dev servers (this will block)
    print(f"\n{'='*60}")
    print(f"🔧 Starting development servers (this will run in foreground)")
    print(f"{'='*60}")
    print(f"Running: npm run dev\n")
    
    try:
        subprocess.run(
            "npm run dev",
            shell=True,
            check=False,
            env=env
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Servers stopped by user")
    except Exception as e:
        print(f"❌ Failed to start servers: {e}")


def main():
    """Main execution function."""
    print("\n" + "="*60)
    print("🔄 HAM Agent 2 - Development Environment Restart")
    print("="*60)
    
    try:
        # Step 1: Check environment setup
        if not check_environment():
            print("\n❌ Environment setup failed")
            sys.exit(1)
        
        # Step 2: Stop containers
        stop_containers()
        
        # Step 3: Start database
        start_database()
        
        # Step 4: Run migrations
        print("\n" + "="*60)
        print("🔧 Running Prisma migrations")
        print("="*60)
        run_migrations()
        
        print("\n" + "="*60)
        print("✅ Development environment setup complete!")
        print("="*60)
        print("\n📊 Database Status:")
        print("  Container: ham-agent-2-postgres")
        print("  Host: localhost:5432")
        print("  Database: ham_agent_2_db")
        print("  User: ham_agent_2")
        
        # Step 5: Start dev servers
        start_dev_servers()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("Development servers stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during restart: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
