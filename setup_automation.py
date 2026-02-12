import os
import sys
import subprocess

def create_task(task_name, script_name, time_str):
    """
    Registers a scheduled task using schtasks.
    """
    python_exe = sys.executable
    # Use pythonw.exe to run without a window if usually preferred, but for now python.exe is safer for debugging visibility
    # Or keep sys.executable (usually python.exe)
    
    script_path = os.path.abspath(script_name)
    cwd = os.path.dirname(script_path)
    
    # Command to run: cd to dir && python script.py
    # We use cmd /c to ensure CWD is correct
    command = f'cmd /c "cd /d {cwd} && {python_exe} {script_path}"'
    
    print(f"Creating task '{task_name}'...")
    print(f"  Script: {script_name}")
    print(f"  Time:   {time_str}")
    
    # schtasks command
    # /SC DAILY : Run every day
    # /TN : Task Name
    # /TR : Task Run (Transformation/Command)
    # /ST : Start Time (HH:mm)
    # /F  : Force overwrite if exists
    
    sch_cmd = [
        "schtasks", "/Create",
        "/SC", "DAILY",
        "/TN", task_name,
        "/TR", command,
        "/ST", time_str,
        "/F"
    ]
    
    try:
        result = subprocess.run(sch_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Success: {task_name} created.")
        else:
            print(f"Failed: {result.stderr.strip()}")
            if "Access is denied" in result.stderr:
                print("   TIP: Try running this script as Administrator.")
    except Exception as e:
        print(f"Error executing schtasks: {e}")

if __name__ == "__main__":
    print("A.R.E.S. Automation Setup")
    print("===========================")
    
    # Task 1: Morning Briefing (09:00 AM)
    create_task("ARES_Morning_Briefing", "daily_briefing.py", "09:00")
    
    # Task 2: Market Scanner (16:30 PM - Market Close)
    create_task("ARES_Market_Scanner", "scan_markets.py", "16:30")
    
    print("\nDone. Verify in Task Scheduler or run 'schtasks /query /TN ARES_Morning_Briefing'.")
