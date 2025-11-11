
#!/usr/bin/env python3
"""
Hurtrock Music Store - Windows Service
Service untuk menjalankan aplikasi sebagai Windows Service dengan auto-restart
"""

import sys
import os
import time
import subprocess
import threading
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    WINDOWS_SERVICE_AVAILABLE = True
except ImportError:
    WINDOWS_SERVICE_AVAILABLE = False
    
class HurtrockMusicStoreService(win32serviceutil.ServiceFramework):
    _svc_name_ = "HurtrockMusicStore"
    _svc_display_name_ = "Hurtrock Music Store"
    _svc_description_ = "Hurtrock Music Store Flask Web Application"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True
        self.process = None
        
        # Setup logging
        self.setup_logging()
        
        # Get application directory
        self.app_dir = Path(__file__).parent.absolute()
        self.python_exe = sys.executable
        self.main_script = self.app_dir / "main.py"
        
    def setup_logging(self):
        """Setup logging untuk service"""
        log_dir = Path(__file__).parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "service.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("HurtrockService")
        
    def SvcStop(self):
        """Stop service"""
        self.logger.info("Service stop requested")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False
        
        # Stop Flask process
        if self.process and self.process.poll() is None:
            self.logger.info("Terminating Flask process")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.logger.warning("Force killing Flask process")
                self.process.kill()
                
    def SvcDoRun(self):
        """Main service loop"""
        self.logger.info("Starting Hurtrock Music Store Service")
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_app)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Wait for stop signal
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        
        self.logger.info("Service stopped")
        
    def monitor_app(self):
        """Monitor dan restart aplikasi jika crash"""
        restart_count = 0
        max_restarts = 5
        restart_window = 300  # 5 menit
        last_restart_time = 0
        
        while self.is_running:
            try:
                current_time = time.time()
                
                # Reset restart count jika sudah lewat restart window
                if current_time - last_restart_time > restart_window:
                    restart_count = 0
                    
                # Check if we've exceeded max restarts
                if restart_count >= max_restarts:
                    self.logger.error(f"Maximum restart attempts ({max_restarts}) reached. Stopping service.")
                    self.SvcStop()
                    break
                    
                # Start Flask application
                self.logger.info(f"Starting Flask application (attempt {restart_count + 1})")
                
                # Change to app directory
                os.chdir(self.app_dir)
                
                # Set environment variables
                env = os.environ.copy()
                env['FLASK_ENV'] = 'production'
                env['PYTHONPATH'] = str(self.app_dir)
                
                # Start process
                self.process = subprocess.Popen(
                    [self.python_exe, str(self.main_script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=env,
                    cwd=self.app_dir
                )
                
                self.logger.info(f"Flask application started with PID {self.process.pid}")
                
                # Monitor process
                while self.is_running and self.process.poll() is None:
                    time.sleep(5)
                    
                # Process ended
                if self.process.poll() is not None and self.is_running:
                    exit_code = self.process.returncode
                    self.logger.warning(f"Flask application exited with code {exit_code}")
                    
                    restart_count += 1
                    last_restart_time = current_time
                    
                    if self.is_running:
                        self.logger.info(f"Restarting in 5 seconds... (restart {restart_count}/{max_restarts})")
                        time.sleep(5)
                        
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")
                if self.is_running:
                    time.sleep(10)
                    
def install_service():
    """Install Windows Service"""
    if not WINDOWS_SERVICE_AVAILABLE:
        print("Error: pywin32 tidak tersedia. Install dengan: pip install pywin32")
        return False
        
    try:
        # Install service
        win32serviceutil.InstallService(
            HurtrockMusicStoreService._svc_reg_class_,
            HurtrockMusicStoreService._svc_name_,
            HurtrockMusicStoreService._svc_display_name_,
            description=HurtrockMusicStoreService._svc_description_
        )
        
        print("✓ Service berhasil diinstall")
        
        # Set service to auto-start
        import win32service
        hscm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
        hs = win32service.OpenService(hscm, HurtrockMusicStoreService._svc_name_, win32service.SERVICE_ALL_ACCESS)
        
        win32service.ChangeServiceConfig(
            hs,
            win32service.SERVICE_NO_CHANGE,
            win32service.SERVICE_AUTO_START,  # Auto-start
            win32service.SERVICE_NO_CHANGE,
            None, None, None, None, None, None, None
        )
        
        win32service.CloseServiceHandle(hs)
        win32service.CloseServiceHandle(hscm)
        
        print("✓ Service dikonfigurasi untuk auto-start")
        
        return True
        
    except Exception as e:
        print(f"✗ Error installing service: {e}")
        return False
        
def uninstall_service():
    """Uninstall Windows Service"""
    if not WINDOWS_SERVICE_AVAILABLE:
        print("Error: pywin32 tidak tersedia")
        return False
        
    try:
        win32serviceutil.RemoveService(HurtrockMusicStoreService._svc_name_)
        print("✓ Service berhasil dihapus")
        return True
    except Exception as e:
        print(f"✗ Error uninstalling service: {e}")
        return False
        
def start_service():
    """Start Windows Service"""
    try:
        win32serviceutil.StartService(HurtrockMusicStoreService._svc_name_)
        print("✓ Service berhasil distart")
        return True
    except Exception as e:
        print(f"✗ Error starting service: {e}")
        return False
        
def stop_service():
    """Stop Windows Service"""
    try:
        win32serviceutil.StopService(HurtrockMusicStoreService._svc_name_)
        print("✓ Service berhasil dihentikan")
        return True
    except Exception as e:
        print(f"✗ Error stopping service: {e}")
        return False
        
def service_status():
    """Check service status"""
    if not WINDOWS_SERVICE_AVAILABLE:
        print("Error: pywin32 tidak tersedia")
        return
        
    try:
        import win32service
        hscm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_CONNECT)
        hs = win32service.OpenService(hscm, HurtrockMusicStoreService._svc_name_, win32service.SERVICE_QUERY_STATUS)
        
        status = win32service.QueryServiceStatus(hs)
        state = status[1]
        
        status_map = {
            win32service.SERVICE_STOPPED: "STOPPED",
            win32service.SERVICE_START_PENDING: "START_PENDING", 
            win32service.SERVICE_STOP_PENDING: "STOP_PENDING",
            win32service.SERVICE_RUNNING: "RUNNING",
            win32service.SERVICE_CONTINUE_PENDING: "CONTINUE_PENDING",
            win32service.SERVICE_PAUSE_PENDING: "PAUSE_PENDING",
            win32service.SERVICE_PAUSED: "PAUSED"
        }
        
        print(f"Service Status: {status_map.get(state, 'UNKNOWN')}")
        
        win32service.CloseServiceHandle(hs)
        win32service.CloseServiceHandle(hscm)
        
    except Exception as e:
        print(f"Error checking service status: {e}")

def show_help():
    """Show help information"""
    print("""
🎸 Hurtrock Music Store - Windows Service Manager
===============================================

Usage: python hurtrock-service.py [COMMAND]

Commands:
  install       Install Windows Service
  uninstall     Remove Windows Service  
  start         Start service
  stop          Stop service
  status        Show service status
  debug         Run in debug mode (not as service)
  help          Show this help

Examples:
  python hurtrock-service.py install    # Install service
  python hurtrock-service.py start      # Start service
  python hurtrock-service.py status     # Check status

Service Features:
  ✅ Auto-start saat Windows boot
  ✅ Auto-restart jika aplikasi crash
  ✅ Berjalan di background
  ✅ Windows Event Log integration
  ✅ Restart protection (max 5 restart dalam 5 menit)

Requirements:
  pip install pywin32

Note: Run as Administrator untuk install/uninstall service
""")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        # No arguments - try to run as service
        if WINDOWS_SERVICE_AVAILABLE:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(HurtrockMusicStoreService)
            servicemanager.StartServiceCtrlDispatcher()
        else:
            print("pywin32 tidak tersedia. Jalankan: pip install pywin32")
            
    else:
        command = sys.argv[1].lower()
        
        if command == 'install':
            if install_service():
                print("\n🎉 Service berhasil diinstall!")
                print("Jalankan: python hurtrock-service.py start")
                
        elif command == 'uninstall':
            if uninstall_service():
                print("\n✓ Service berhasil dihapus!")
                
        elif command == 'start':
            start_service()
            
        elif command == 'stop':
            stop_service()
            
        elif command == 'status':
            service_status()
            
        elif command == 'debug':
            # Run directly for debugging
            service = HurtrockMusicStoreService([])
            service.monitor_app()
            
        elif command in ['help', '--help', '-h']:
            show_help()
            
        else:
            print(f"Unknown command: {command}")
            show_help()
