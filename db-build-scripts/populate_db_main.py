"""
Main script to populate the database with data from Workwize API.
Runs all population scripts in the correct order to respect foreign key dependencies.
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Define scripts in dependency order
SCRIPTS = [
    {
        "name": "Warehouses",
        "script": "populate_warehouses.py",
        "description": "Populate warehouses (no dependencies)"
    },
    {
        "name": "Offices",
        "script": "populate_offices.py",
        "description": "Populate offices (no dependencies)"
    },
    {
        "name": "Employees",
        "script": "populate_employees.py",
        "description": "Populate employees (no dependencies)"
    },
    {
        "name": "Addresses",
        "script": "populate_addresses.py",
        "description": "Populate addresses (requires employees)"
    },
    {
        "name": "Assets",
        "script": "populate_assets.py",
        "description": "Populate assets (requires employees and warehouses)"
    },
    {
        "name": "Orders",
        "script": "populate_orders.py",
        "description": "Populate orders (requires employees)"
    }
]


def print_header():
    """Print script header."""
    print("=" * 80)
    print("Workwize Database Population - Main Script")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total scripts to run: {len(SCRIPTS)}")
    print("=" * 80)
    print()


def print_section(step, total, name, description):
    """Print section header for each script."""
    print()
    print("-" * 80)
    print(f"[{step}/{total}] {name}")
    print(f"Description: {description}")
    print("-" * 80)


def run_script(script_name):
    """Run a population script and return success status."""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    script_path = script_dir / script_name
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',  # Handle encoding issues gracefully
            cwd=str(script_dir)  # Run from the script directory
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.returncode != 0:
            print(f"\nERROR: {script_name} failed with exit code {result.returncode}")
            if result.stderr:
                print("Error output:")
                print(result.stderr)
            return False
        
        return True
        
    except Exception as e:
        print(f"\nEXCEPTION: Failed to run {script_name}")
        print(f"Error: {str(e)}")
        return False


def main():
    """Main execution function."""
    print_header()
    
    results = []
    start_time = datetime.now()
    
    for idx, script_info in enumerate(SCRIPTS, 1):
        name = script_info["name"]
        script = script_info["script"]
        description = script_info["description"]
        
        print_section(idx, len(SCRIPTS), name, description)
        
        script_start = datetime.now()
        success = run_script(script)
        script_duration = (datetime.now() - script_start).total_seconds()
        
        results.append({
            "name": name,
            "script": script,
            "success": success,
            "duration": script_duration
        })
        
        if not success:
            print(f"\n!!! {name} failed. Stopping execution. !!!")
            print("Fix the error and run this script again to resume.")
            break
    
    # Print summary
    total_duration = (datetime.now() - start_time).total_seconds()
    print()
    print("=" * 80)
    print("Execution Summary")
    print("=" * 80)
    
    for result in results:
        status = "SUCCESS" if result["success"] else "FAILED"
        duration_str = f"{result['duration']:.1f}s"
        print(f"[{status:7}] {result['name']:15} ({duration_str:>8})")
    
    print("-" * 80)
    successful = sum(1 for r in results if r["success"])
    print(f"Completed: {successful}/{len(SCRIPTS)} scripts")
    print(f"Total time: {total_duration:.1f}s")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Exit with appropriate code
    if all(r["success"] for r in results):
        print("\nAll population scripts completed successfully!")
        sys.exit(0)
    else:
        print("\nSome scripts failed. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
