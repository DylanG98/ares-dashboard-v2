import os
import shutil
import glob

def clean_workspace():
    root_dir = os.getcwd()
    archive_dir = os.path.join(root_dir, "archive")
    legacy_reports_dir = os.path.join(archive_dir, "legacy_reports")
    legacy_images_dir = os.path.join(archive_dir, "legacy_images")
    
    os.makedirs(legacy_reports_dir, exist_ok=True)
    os.makedirs(legacy_images_dir, exist_ok=True)
    
    print(f"Cleaning workspace: {root_dir}")
    print(f"Archive target: {archive_dir}")
    
    # 1. Move Report Files (MD and HTML)
    report_patterns = ["REPORTE_*.md", "REPORTE_*.html"]
    for pattern in report_patterns:
        for file in glob.glob(pattern):
            try:
                shutil.move(file, os.path.join(legacy_reports_dir, file))
                print(f"Moved: {file}")
            except Exception as e:
                print(f"Error moving {file}: {e}")

    # 2. Move Output Images from root/output to archive
    output_dir = "output"
    if os.path.exists(output_dir):
        for file in glob.glob(os.path.join(output_dir, "*.png")):
            try:
                filename = os.path.basename(file)
                shutil.move(file, os.path.join(legacy_images_dir, filename))
                print(f"Archived image: {filename}")
            except Exception as e:
                print(f"Error archiving image {file}: {e}")
        
        # Try to remove output dir if empty
        try:
            os.rmdir(output_dir)
            print("Removed empty 'output' directory.")
        except:
            print("'output' directory not empty, left in place.")

    print("\nCleanup Complete! 🧹")
    print("Files moved to 'archive/' folder.")

if __name__ == "__main__":
    clean_workspace()
