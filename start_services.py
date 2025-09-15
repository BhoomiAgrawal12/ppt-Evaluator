#!/usr/bin/env python3
"""
Startup script for SIH Presentation Evaluator
Runs both the main application and the AI detector service
"""

import os
import sys
import time
import subprocess
import threading
import signal
from pathlib import Path

def run_detector_service():
    """Run the AI detector service"""
    print("Starting AI Detector Service on port 5001...")
    try:
        process = subprocess.Popen([
            sys.executable, "detector.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait a moment for the service to start
        time.sleep(3)

        # Check if the process is still running
        if process.poll() is None:
            print("SUCCESS: AI Detector Service started successfully!")
        else:
            stdout, stderr = process.communicate()
            print(f"ERROR: AI Detector Service failed to start:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")

        return process
    except Exception as e:
        print(f"ERROR: Failed to start AI Detector Service: {str(e)}")
        return None

def run_main_app():
    """Run the main Flask application"""
    print("Starting Main Application on port 5000...")
    try:
        process = subprocess.Popen([
            sys.executable, "app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait a moment for the service to start
        time.sleep(3)

        # Check if the process is still running
        if process.poll() is None:
            print("SUCCESS: Main Application started successfully!")
            print("Frontend available at: http://localhost:5000")
            print("API available at: http://localhost:5000/api/")
        else:
            stdout, stderr = process.communicate()
            print(f"ERROR: Main Application failed to start:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")

        return process
    except Exception as e:
        print(f"ERROR: Failed to start Main Application: {str(e)}")
        return None

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")

    required_packages = [
        'flask', 'transformers', 'torch', 'google-generativeai',
        'requests', 'llama_cloud_services'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            if package == 'google-generativeai':
                import google.generativeai
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"ERROR: Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False

    print("SUCCESS: All dependencies are installed!")
    return True

def main():
    """Main startup function"""
    print("=" * 60)
    print("SIH Presentation Evaluator - System Startup")
    print("=" * 60)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Check if upload directory exists
    upload_dir = Path("uploads")
    if not upload_dir.exists():
        upload_dir.mkdir()
        print("Created uploads directory")

    # Check if templates directory exists
    templates_dir = Path("templates")
    if not templates_dir.exists():
        print("ERROR: Templates directory not found!")
        sys.exit(1)

    processes = []

    try:
        # Start AI Detector Service
        detector_process = run_detector_service()
        if detector_process:
            processes.append(('Detector Service', detector_process))

        # Start Main Application
        main_process = run_main_app()
        if main_process:
            processes.append(('Main Application', main_process))

        if not processes:
            print("ERROR: No services started successfully!")
            sys.exit(1)

        print("\n" + "=" * 60)
        print("SUCCESS: System Started Successfully!")
        print("=" * 60)
        print("Services running:")
        for name, process in processes:
            print(f"   * {name}: PID {process.pid}")

        print("\nQuick Links:")
        print("   * Frontend: http://localhost:5000")
        print("   * API Status: http://localhost:5000/api/status")
        print("   * Detector API: http://localhost:5001/detect")

        print("\nUsage:")
        print("   1. Set GEMINI_API_KEY in your .env file")
        print("   2. Open http://localhost:5000 in your browser")
        print("   3. Upload a PPT, PPTX or PDF file")
        print("   4. Enter team name and problem statement")
        print("   5. Get intelligent LLM-based evaluation results")

        print("\nPress Ctrl+C to stop all services")
        print("=" * 60)

        # Wait for keyboard interrupt
        try:
            while True:
                # Check if processes are still running
                for name, process in processes[:]:
                    if process.poll() is not None:
                        print(f"WARNING: {name} has stopped unexpectedly!")
                        processes.remove((name, process))

                if not processes:
                    print("ERROR: All services have stopped!")
                    break

                time.sleep(5)
        except KeyboardInterrupt:
            print("\nShutdown signal received...")

    except Exception as e:
        print(f"ERROR: Error during startup: {str(e)}")

    finally:
        # Cleanup
        print("Cleaning up...")
        for name, process in processes:
            try:
                process.terminate()
                print(f"   * Stopped {name}")
            except:
                pass

        print("Cleanup completed!")
        print("Goodbye!")

if __name__ == "__main__":
    main()