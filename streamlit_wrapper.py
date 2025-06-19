#!/usr/bin/env python3
"""
Wrapper script for running Streamlit app from PyInstaller executable
"""
import sys
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
import threading
import time
import webbrowser

def extract_app_files():
    """Extract app files from PyInstaller bundle"""
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        bundle_dir = Path(sys._MEIPASS)
        
        # Create temp directory for app files
        temp_dir = Path(tempfile.mkdtemp(prefix='streamlit_app_'))
        
        # Copy necessary files
        files_to_copy = ['app.py', 'Frontend', 'Backend', 'Arquivos']
        
        for item in files_to_copy:
            src = bundle_dir / item
            dst = temp_dir / item
            
            if src.exists():
                if src.is_file():
                    shutil.copy2(src, dst)
                else:
                    shutil.copytree(src, dst)
                print(f"Extracted: {item}")
            else:
                print(f"Warning: {item} not found in bundle")
        
        return temp_dir
    else:
        # Running from source
        return Path(__file__).parent

def run_streamlit_app(app_dir):
    """Run the Streamlit app"""
    app_file = app_dir / 'app.py'
    
    if not app_file.exists():
        print(f"Error: app.py not found in {app_dir}")
        return False
    
    # Change to app directory
    original_cwd = os.getcwd()
    os.chdir(app_dir)
    
    try:
        # Create Streamlit config to disable development mode
        config_dir = app_dir / '.streamlit'
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / 'config.toml'
        config_content = """
[global]
developmentMode = false

[server]
port = 8501
address = "127.0.0.1"
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
"""
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        print(f"Created config file: {config_file}")
        
        # Set environment variables for Streamlit
        os.environ['STREAMLIT_SERVER_PORT'] = '8501'
        os.environ['STREAMLIT_SERVER_ADDRESS'] = '127.0.0.1'
        os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
        os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
        os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
        os.environ['STREAMLIT_GLOBAL_DEVELOPMENT_MODE'] = 'false'
        
        # Import and run Streamlit
        import streamlit.web.cli as stcli
        
        # Prepare arguments - simpler approach
        args = [
            'streamlit', 'run', str(app_file),
            '--global.developmentMode', 'false'
        ]
        
        sys.argv = args
        
        # Start Streamlit
        print("Starting Streamlit app...")
        print("App will be available at: http://localhost:8501")
        
        # Open browser after a delay
        def open_browser():
            time.sleep(3)
            webbrowser.open('http://localhost:8501')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Run Streamlit
        stcli.main()
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error running Streamlit: {e}")
        return False
    finally:
        os.chdir(original_cwd)
    
    return True

def main():
    print("Initializing Streamlit application...")
    
    try:
        # Extract app files
        app_dir = extract_app_files()
        print(f"App directory: {app_dir}")
        
        # Run the app
        success = run_streamlit_app(app_dir)
        
        if not success:
            print("Failed to start Streamlit app")
            input("Press Enter to exit...")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()