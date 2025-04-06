import tkinter as tk
from tkinter import ttk, messagebox
from mitmproxy import http
import threading
import platform
import winreg
import subprocess
import asyncio
from mitmproxy.tools.dump import DumpMaster
from mitmproxy import options
import queue
import re
import time
from collections import deque
import logging
import math

# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class FirewallLogic:
    def __init__(self, app, queue):
        self.app = app
        self.queue = queue
        self.blocked_patterns = []
        self.blocked_domains = set()
        self.traffic_history = deque(maxlen=5000)
        self.master = None
        self.running = False
        self.traffic_rules = []
        self.sandbox_mode = False
        self.sandbox_queue = deque()
        self.rules = {
            "Block JS Files": {"enabled": False, "list": []},
            "Block Image Files": {"enabled": False, "list": []},
            "Block CSS Files": {"enabled": False, "list": []},
            "Block Domains": {"enabled": False, "list": []},
            "Block URL": {"enabled": False, "list": []},
            "Block Text": {"enabled": False, "list": []},
        }
        self.malware_signatures = [
            r"malware\.[a-z]+", r"virus\.[a-z]+", r"exploit\.[a-z]+", r"trojan\.[a-z]+", r"phish\.[a-z]+",
            r"cmd\.exe", r"powershell\.exe", r"wget\s+http", r"eval\(", r'document\.write\(',
            r'unescape\(', r'base64_decode\(', r'exec\('
        ]
        self.ad_signatures = [r"ads\.[a-z]+", r"adserver\.[a-z]+", r"doubleclick\.net", r"googlesyndication\.com"]
        self.tracking_signatures = [r"tracking\.[a-z]+", r"analytics\.[a-z]+", r"pixel\.[a-z]+"]

    def request(self, flow: http.HTTPFlow):
        url = flow.request.pretty_url
        client_ip = flow.client_conn.address[0]
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        domain = flow.request.host

        logging.info(f"Traffic detected: {url} from {client_ip}")
        self.traffic_history.append((domain, timestamp))
        self.queue.put(("TRAFFIC", list(self.traffic_history)))
    
        try:
            content = flow.request.content.decode('utf-8', errors='ignore')
        except Exception as e:
            content = ""
            logging.warning(f"Failed to decode request content for {url}: {e}")

        if self._is_blocked_request(domain,url, content):
            flow.response = http.Response.make(403, b"Blocked by Firewall Rule")
            logging.warning(f"Blocked URL: {url}")
            self.queue.put(("ALERT", f"Blocked Request: {url} (Rule Matched)"))
            return

        if url.startswith("http://"):
            self.add_alert_to_timeline(f"HTTP Warning: {url} at {timestamp}")

        if self.sandbox_mode:
            logging.info(f"Sandbox mode active. Intercepting request: {url}")
            flow.intercept()
            self.sandbox_queue.append(flow)
            self.queue.put(("SANDBOX", f"Intercepted: {url}"))
            return

        if self.traffic_rules:
            self._apply_traffic_rules(flow, url, "Request")

    def response(self, flow: http.HTTPFlow):
        url = flow.request.pretty_url
        logging.info(f"Response received for: {url}")

        try:
            content = flow.response.content.decode('utf-8', errors='ignore')
        except Exception as e:
            content = ""
            logging.warning(f"Failed to decode response content for {url}: {e}")

        if self._is_blocked_response(url, content):
            flow.response = http.Response.make(403, b"Blocked by Firewall Rule")
            logging.warning(f"Blocked URL: {url}")
            self.queue.put(("ALERT", f"Blocked Response: {url} (Rule Matched)"))
            return

        if self.traffic_rules:
            self._apply_traffic_rules(flow, url, "Response")

    def _is_blocked_request(self, domain,url, content):
        if self.rules["Block Domains"]["enabled"]:
            for d in self.rules["Block Domains"]["list"]:
                if domain in d:
                    return True

        if self.rules["Block URL"]["enabled"]:
            for u in self.rules["Block URL"]["list"]:
                if re.search(re.escape(u), url, re.IGNORECASE):
                    return True

        if self.rules["Block Text"]["enabled"] and content:
            for text in self.rules["Block Text"]["list"]:
                if text in content:
                    return True

        if self._check_content_type(url, content, "Request"):
            return True

        # for signature in self.malware_signatures + self.ad_signatures + self.tracking_signatures:
        #     if re.search(signature, url + content, re.IGNORECASE):
        #         logging.warning(f"Signature match in {url}: {signature}")
        #         return True
                
        return False

    def _is_blocked_response(self, url, content):
        domain = url.split("/")[2] if "/" in url else url

        if self.rules["Block Domains"]["enabled"] and domain in self.rules["Block Domains"]["list"]:
            return True

        if self.rules["Block URL"]["enabled"]:
            for pattern in self.rules["Block URL"]["list"]:
                if re.search(re.escape(pattern), url, re.IGNORECASE):
                    return True

        if self.rules["Block Text"]["enabled"] and content:
            for text in self.rules["Block Text"]["list"]:
                if text in content:
                    return True

        if self._check_content_type(url, content, "Response"):
            return True

        return False

    def _check_content_type(self, url, content, scope):
        if self.rules["Block JS Files"]["enabled"] and url:
            for js in self.rules["Block JS Files"]["list"]:
                if js in url and (str(js).split(".")[-1] in ["js","JS"]):
                    return True
                
        if self.rules["Block CSS Files"]["enabled"] and url:
            for css in self.rules["Block CSS Files"]["list"]:
                if css in url and (str(css).split(".")[-1] in ["css", "CSS"]):
                    return True
                
        if self.rules["Block Image Files"]["enabled"] and url:
            for img in self.rules["Block Image Files"]["list"]:
                if img in url and (str(img).split(".")[-1] in ["jpg", "jpeg", "png", "gif", "webp", "svg", "bmp", "ico"]):
                    return True
        return False

    def _apply_traffic_rules(self, flow, url, scope):
        for find, replace, rule_scope in self.traffic_rules:
            if scope == "Request" and find in url:
                flow.request.url = flow.request.url.replace(find, replace)
                logging.info(f"Applied traffic rule: {find} -> {replace} in {url}")
            elif scope == "Response" and flow.response.content:
                try:
                    content = flow.response.content.decode('utf-8', errors='ignore')
                    new_content = str(content).replace(str(find), replace)
                    # new_content = new_content.replace(str(find).capitalize(), replace)
                    flow.response.content = new_content.encode('utf-8')
                    logging.info(f"Applied traffic rule: {find} -> {replace} in response for {url}")
                except Exception as e:
                    logging.warning(f"Failed to apply traffic rule to response {url}: {e}")

    def _calculate_entropy(self, data):
        if not data:
            return 0
        entropy = 0
        for x in range(256):
            p_x = data.count(chr(x)) / len(data)
            if p_x > 0:
                entropy -= p_x * math.log2(p_x)
        return entropy

    def add_block_rule(self, pattern, enabled=True):
        if pattern in self.rules:
            self.rules[pattern]["enabled"] = enabled
            self.queue.put(("ALERT", f"Rule {pattern} {'enabled' if enabled else 'disabled'}"))
            logging.info(f"Rule {pattern} {'enabled' if enabled else 'disabled'}")
        else:
            if "." in pattern:
                self.blocked_domains.add(pattern)
            else:
                self.blocked_patterns.append(pattern)
            self.queue.put(("ALERT", f"Added block rule: {pattern}"))
            logging.info(f"Blocking rule added: {pattern}")

    def add_traffic_rule(self, find, replace, scope):
        if (find, replace, scope) not in self.traffic_rules:
            self.traffic_rules.append((find, replace, scope))
            self.queue.put(("ALERT", f"Added traffic rule: '{find}' -> '{replace}' in {scope}"))
            logging.info(f"Traffic rule added: {find} -> {replace} in {scope}")

    def set_sandbox_mode(self, enabled):
        self.sandbox_mode = enabled
        self.queue.put(("ALERT", f"Sandbox mode {'enabled' if enabled else 'disabled'}"))
        logging.info(f"Sandbox mode {'enabled' if enabled else 'disabled'}")

    def allow_sandbox_request(self):
        if self.sandbox_queue:
            flow = self.sandbox_queue.popleft()
            if hasattr(flow, "resume"):
                flow.resume()
                logging.info(f"Sandboxed request resumed: {flow.request.pretty_url}")

    def add_alert_to_timeline(self, alert):
        self.queue.put(("ALERT", alert))
        logging.info(f"Alert added: {alert}")

    def update_rule_list(self, rule_name, rule_list):
        if rule_name in self.rules:
            self.rules[rule_name]["list"] = rule_list
            self.queue.put(("ALERT", f"Updated list for rule {rule_name}: {rule_list}"))
            logging.info(f"Updated list for rule {rule_name}: {rule_list}")

    def remove_block_rule(self, pattern):
        if pattern in self.rules:
            self.rules[pattern]["enabled"] = False
            self.queue.put(("ALERT", f"Disabled block rule: {pattern}"))
            logging.info(f"Disabled block rule: {pattern}")
        elif pattern in self.blocked_patterns:
            self.blocked_patterns.remove(pattern)
            self.queue.put(("ALERT", f"Removed block rule: {pattern}"))
            logging.info(f"Blocking rule removed: {pattern}")
        elif pattern in self.blocked_domains:
            self.blocked_domains.remove(pattern)
            self.queue.put(("ALERT", f"Removed block domain: {pattern}"))
            logging.info(f"Blocking domain removed: {pattern}")

def setup_system_proxy(host="127.0.0.1", port=8080):
    os_name = platform.system().lower()
    proxy_address = f"{host}:{port}"

    try:
        if "windows" in os_name:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxy_address)

            logging.info(f"Windows system proxy set to {proxy_address}")

        elif "linux" in os_name:
            try:
                subprocess.run(["gsettings", "set", "org.gnome.system.proxy.http", "host", host], check=True)
                subprocess.run(["gsettings", "set", "org.gnome.system.proxy.http", "port", str(port)], check=True)
                subprocess.run(["gsettings", "set", "org.gnome.system.proxy", "mode", "manual"], check=True)
                
                subprocess.run(["gsettings", "set", "org.gnome.system.proxy.https", "host", host], check=True)
                subprocess.run(["gsettings", "set", "org.gnome.system.proxy.https", "port", str(port)], check=True)
                
                logging.info(f"Linux system proxy (GNOME) set to {proxy_address}")
                messagebox.showinfo("Proxy Setup", f"System proxy set to {proxy_address} on Linux. Restart your browser if needed.")
            except subprocess.CalledProcessError as e:
                pass
        else:
            logging.error(f"Unsupported OS: {os_name}")
            messagebox.showerror("Error", f"Proxy setup not supported on {os_name}")
            return

    except Exception as e:
        logging.error(f"Failed to set system proxy: {e}")
        messagebox.showerror("Error", f"Failed to set system proxy: {str(e)}")

def remove_system_proxy():
    os_name = platform.system().lower()

    try:
        if "windows" in os_name:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS) as key:
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, "")
                winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, "")

            subprocess.run(["netsh", "winhttp", "reset", "proxy"], check=True)
            logging.info("Windows system proxy removed")

        elif "linux" in os_name:
            try:
                subprocess.run(["gsettings", "set", "org.gnome.system.proxy", "mode", "none"], check=True)
                subprocess.run(["gsettings", "reset", "org.gnome.system.proxy.http", "host"], check=True)
                subprocess.run(["gsettings", "reset", "org.gnome.system.proxy.http", "port"], check=True)
                subprocess.run(["gsettings", "reset", "org.gnome.system.proxy.https", "host"], check=True)
                subprocess.run(["gsettings", "reset", "org.gnome.system.proxy.https", "port"], check=True)
                subprocess.run(["gsettings", "reset", "org.gnome.system.proxy", "ignore-hosts"], check=True)
                logging.info("Linux system proxy (GNOME) removed")
                messagebox.showinfo("Proxy Removal", "System proxy removed on Linux. Restart your browser if needed.")
            except subprocess.CalledProcessError as e:
                pass

        else:
            logging.error(f"Unsupported OS: {os_name}")
            return
    except Exception as e:
        logging.error(f"Failed to remove system proxy: {e}")

async def start_proxy(firewall,fhost="127.0.0.1",fport=8080):
    opts = options.Options(listen_host=fhost, listen_port=fport)
    firewall.master = DumpMaster(opts, with_termlog=False, with_dumper=False)
    firewall.master.addons.add(firewall)
    await firewall.master.run()

def run_proxy(firewall,fhost,fport):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_proxy(firewall,fhost,fport))