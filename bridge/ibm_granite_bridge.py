#!/usr/bin/env python3
"""
IBM Granite Bridge - Secure 2FA verification stream for system integrity
This script establishes a secure connection between the local system and IBM Granite LLM
"""

import os
import sys
import json
import time
import socket
import hashlib
import argparse
import requests
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import threading
import ssl
import uuid
import hmac

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "ibm_granite_bridge.log")

logger = logging.getLogger("IBMGraniteBridge")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

class IBMGraniteBridge:
    """Bridge class for IBM Granite LLM integration and 2FA verification"""
    
    def __init__(self, config_path=None):
        """Initialize the IBM Granite Bridge"""
        self.config_path = config_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/bridge_config.json")
        self.config = self._load_config()
        self.session_id = self._generate_session_id()
        self.verification_code = None
        self.is_verified = False
        self.local_server = None
        self.server_thread = None
        self.ollama_url = self.config.get("ollama_url", "http://localhost:11434")
        self.ibm_api_key = self.config.get("ibm_api_key", "")
        self.ibm_api_url = self.config.get("ibm_api_url", "")
        self.local_port = self.config.get("local_port", 5151)
        self.system_fingerprint = self._generate_system_fingerprint()
        
        logger.info(f"IBM Granite Bridge initialized with session {self.session_id}")
    
    def _load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {str(e)}")
                return self._create_default_config()
        else:
            return self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration"""
        config = {
            "ollama_url": "http://localhost:11434",
            "ibm_api_key": "",
            "ibm_api_url": "https://us-south.ml.cloud.ibm.com/ml/v1/",
            "local_port": 5151,
            "verification_timeout": 300,
            "ping_interval": 60,
            "log_level": "INFO",
            "trusted_devices": []
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Created default config at {self.config_path}")
        except Exception as e:
            logger.error(f"Error creating default config: {str(e)}")
        
        return config
    
    def _generate_session_id(self):
        """Generate a unique session ID"""
        timestamp = str(time.time())
        hostname = socket.gethostname()
        unique_str = f"{timestamp}-{hostname}-{os.getpid()}"
        return hashlib.sha256(unique_str.encode()).hexdigest()[:12]
    
    def _generate_system_fingerprint(self):
        """Generate a unique fingerprint for this system"""
        try:
            # Collect system information
            hostname = socket.gethostname()
            mac_address = self._get_mac_address()
            cpu_info = self._get_cpu_info()
            disk_id = self._get_disk_id()
            
            # Combine and hash the information
            fingerprint_data = f"{hostname}|{mac_address}|{cpu_info}|{disk_id}"
            fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()
            
            logger.info(f"Generated system fingerprint: {fingerprint[:8]}...")
            return fingerprint
        except Exception as e:
            logger.error(f"Error generating system fingerprint: {str(e)}")
            return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    
    def _get_mac_address(self):
        """Get the MAC address of the primary network interface"""
        try:
            if sys.platform == "darwin":  # macOS
                mac = subprocess.check_output("ifconfig en0 | awk '/ether/{print $2}'", 
                                             shell=True).decode().strip()
            elif sys.platform == "linux":
                mac = subprocess.check_output("ip link show | grep link/ether | head -1 | awk '{print $2}'", 
                                             shell=True).decode().strip()
            else:
                mac = "00:00:00:00:00:00"
            return mac
        except:
            return "00:00:00:00:00:00"
    
    def _get_cpu_info(self):
        """Get CPU information"""
        try:
            if sys.platform == "darwin":  # macOS
                cpu_info = subprocess.check_output("sysctl -n machdep.cpu.brand_string", 
                                                 shell=True).decode().strip()
            elif sys.platform == "linux":
                cpu_info = subprocess.check_output("cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d: -f2", 
                                                 shell=True).decode().strip()
            else:
                cpu_info = "Unknown CPU"
            return cpu_info
        except:
            return "Unknown CPU"
    
    def _get_disk_id(self):
        """Get disk identifier"""
        try:
            if sys.platform == "darwin":  # macOS
                disk_id = subprocess.check_output("diskutil info / | grep 'Volume UUID' | awk '{print $3}'", 
                                                shell=True).decode().strip()
            elif sys.platform == "linux":
                disk_id = subprocess.check_output("blkid -o value -s UUID $(df / | grep /dev | cut -d' ' -f1)", 
                                                shell=True).decode().strip()
            else:
                disk_id = "Unknown Disk"
            return disk_id
        except:
            return "Unknown Disk"
    
    def _generate_verification_code(self):
        """Generate a 6-digit verification code"""
        import random
        self.verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        return self.verification_code
    
    def get_system_info(self):
        """Collect system information for verification"""
        info = {
            "hostname": socket.gethostname(),
            "mac_address": self._get_mac_address(),
            "session_id": self.session_id,
            "timestamp": time.time(),
            "system_fingerprint": self.system_fingerprint,
            "os_type": sys.platform,
            "python_version": sys.version
        }
        return info
    
    def start_local_server(self):
        """Start a local HTTP server for 2FA verification"""
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import threading
        
        class VerificationHandler(BaseHTTPRequestHandler):
            bridge_instance = self
            
            def do_GET(self):
                if self.path == '/status':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    status = {
                        "status": "active",
                        "verified": self.bridge_instance.is_verified,
                        "session_id": self.bridge_instance.session_id,
                        "system_fingerprint": self.bridge_instance.system_fingerprint[:8] + "..."
                    }
                    self.wfile.write(json.dumps(status).encode())
                elif self.path == '/verify':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    code = self.bridge_instance._generate_verification_code()
                    html = f"""
                    <html><body>
                    <h2>IBM Granite 2FA Verification</h2>
                    <p>Enter this code on your verification device: <strong>{code}</strong></p>
                    <form action="/confirm" method="post">
                    <input type="text" name="code" placeholder="Enter code from verification device">
                    <input type="submit" value="Verify">
                    </form>
                    </body></html>
                    """
                    self.wfile.write(html.encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_POST(self):
                if self.path == '/confirm':
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length).decode()
                    # Simple parsing of form data
                    code = post_data.split('code=')[1].split('&')[0] if 'code=' in post_data else ""
                    
                    if code == self.bridge_instance.verification_code:
                        self.bridge_instance.is_verified = True
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        html = """
                        <html><body>
                        <h2>Verification Successful</h2>
                        <p>The system has been verified and can proceed.</p>
                        </body></html>
                        """
                        self.wfile.write(html.encode())
                    else:
                        self.send_response(401)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        html = """
                        <html><body>
                        <h2>Verification Failed</h2>
                        <p>The code entered does not match. Please try again.</p>
                        </body></html>
                        """
                        self.wfile.write(html.encode())
                else:
                    self.send_response(404)
                    self.end_headers()
        
        def run_server():
            server_address = ('', self.local_port)
            self.local_server = HTTPServer(server_address, VerificationHandler)
            
            # Attempt to use SSL if certificates exist
            cert_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/cert.pem")
            key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/key.pem")
            
            if os.path.exists(cert_path) and os.path.exists(key_path):
                self.local_server.socket = ssl.wrap_socket(
                    self.local_server.socket,
                    keyfile=key_path,
                    certfile=cert_path,
                    server_side=True
                )
                logger.info(f"HTTPS server started on port {self.local_port}")
            else:
                logger.info(f"HTTP server started on port {self.local_port} (SSL certificates not found)")
                
            self.local_server.serve_forever()
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        logger.info(f"Local server thread started on port {self.local_port}")
        return True
    
    def query_ollama(self, prompt, model="granite:latest"):
        """Query the local Ollama instance with IBM Granite model"""
        try:
            url = f"{self.ollama_url}/api/generate"
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                logger.error(f"Error querying Ollama: {response.status_code}")
                return f"Error: {response.status_code}"
        except Exception as e:
            logger.error(f"Exception querying Ollama: {str(e)}")
            return f"Error: {str(e)}"
    
    def verify_system_integrity(self):
        """Use IBM Granite to verify system integrity"""
        if not self.is_verified:
            logger.warning("System not verified via 2FA")
            return False
        
        # Collect system information
        system_info = self.get_system_info()
        
        # Generate a prompt for the LLM to analyze
        prompt = f"""
        You are a system integrity verification agent. Analyze the following system information and determine if it appears normal or if there are any suspicious indicators:
        
        Hostname: {system_info['hostname']}
        MAC Address: {system_info['mac_address']}
        System Fingerprint: {system_info['system_fingerprint']}
        OS Type: {system_info['os_type']}
        Python Version: {system_info['python_version']}
        Timestamp: {datetime.fromtimestamp(system_info['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}
        
        Respond with VERIFIED if everything appears normal, or SUSPICIOUS followed by your reasoning if you detect any anomalies.
        """
        
        # Query the LLM
        response = self.query_ollama(prompt)
        
        # Parse the response
        if "VERIFIED" in response:
            logger.info("System integrity verified by IBM Granite")
            return True
        elif "SUSPICIOUS" in response:
            logger.warning(f"System integrity check failed: {response}")
            return False
        else:
            logger.error(f"Ambiguous response from IBM Granite: {response}")
            return False
    
    def start_beacon_mode(self):
        """Start beacon mode to periodically ping and verify system integrity"""
        def beacon_loop():
            ping_interval = self.config.get("ping_interval", 60)
            logger.info(f"Starting beacon mode with {ping_interval}s interval")
            
            while True:
                try:
                    # Generate system fingerprint
                    current_fingerprint = self._generate_system_fingerprint()
                    
                    # Check if fingerprint has changed
                    if current_fingerprint != self.system_fingerprint:
                        logger.warning(f"System fingerprint changed: {self.system_fingerprint[:8]}... -> {current_fingerprint[:8]}...")
                        self.system_fingerprint = current_fingerprint
                        self.is_verified = False
                    
                    # Verify system integrity if verified
                    if self.is_verified:
                        self.verify_system_integrity()
                    
                    # Sleep for the configured interval
                    time.sleep(ping_interval)
                except Exception as e:
                    logger.error(f"Error in beacon loop: {str(e)}")
                    time.sleep(ping_interval)
        
        beacon_thread = threading.Thread(target=beacon_loop, daemon=True)
        beacon_thread.start()
        logger.info("Beacon mode activated")
        return beacon_thread
    
    def shutdown(self):
        """Clean shutdown of the bridge"""
        logger.info("Shutting down IBM Granite Bridge")
        if self.local_server:
            self.local_server.shutdown()
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=5)
        logger.info("IBM Granite Bridge shutdown complete")

def main():
    """Main function to run the bridge as a standalone script"""
    parser = argparse.ArgumentParser(description="IBM Granite Bridge - 2FA System Verification")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--port", help="Local server port", type=int, default=5151)
    parser.add_argument("--beacon", help="Start in beacon mode", action="store_true")
    args = parser.parse_args()
    
    bridge = IBMGraniteBridge(config_path=args.config)
    
    if args.port:
        bridge.local_port = args.port
    
    try:
        # Start local server
        bridge.start_local_server()
        
        # Start beacon mode if requested
        if args.beacon:
            beacon_thread = bridge.start_beacon_mode()
        
        # Print verification URL
        print(f"IBM Granite Bridge running with session ID: {bridge.session_id}")
        print(f"Visit http://localhost:{bridge.local_port}/verify to complete 2FA verification")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...")
    finally:
        bridge.shutdown()

if __name__ == "__main__":
    main()
