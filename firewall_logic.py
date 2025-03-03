import tkinter as tk
from tkinter import ttk, messagebox
from mitmproxy import http
import threading
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
        self.traffic_history = deque(maxlen=30)
        self.master = None
        self.running = False
        self.traffic_rules = []
        self.sandbox_mode = False
        self.sandbox_queue = deque()
        self.rules = {} 
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

        if self._is_blocked_request(url, flow.request.content.decode('utf-8', errors='ignore')):
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

        if self._is_blocked_response(url, flow.response.content.decode('utf-8', errors='ignore')):
            flow.response = http.Response.make(403, b"Blocked by Firewall Rule")
            logging.warning(f"Blocked URL: {url}")
            self.queue.put(("ALERT", f"Blocked Response: {url} (Rule Matched)"))
            return

        if self.traffic_rules:
            self._apply_traffic_rules(flow, url, "Response")

    def _is_blocked_request(self, url, content):
        domain = url.split("/")[2] if "/" in url else url
        if domain in self.blocked_domains:
            return True

        for pattern in self.blocked_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True

        if not content:
            return False

        if self._check_content_type(content, url, "Request"):
            return True

        # check obfuscation
        # entropy = self._calculate_entropy(content)
        # if entropy > 6.0:
        #     logging.warning(f"High entropy detected in {url}: {entropy}")
        #     return True

        for signature in self.malware_signatures + self.ad_signatures + self.tracking_signatures:
            if re.search(signature, content, re.IGNORECASE):
                logging.warning(f"Signature match in {url}: {signature}")
                return True

        return False

    def _is_blocked_response(self, url, content):
        domain = url.split("/")[2] if "/" in url else url
        if domain in self.blocked_domains:
            return True

        for pattern in self.blocked_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True

        if not content:
            return False

        if self._check_content_type(content, url, "Response"):
            return True

        # Heuristic: High entropy (possible obfuscation)
        # entropy = self._calculate_entropy(content)
        # if entropy > 6.0:
        #     logging.warning(f"High entropy detected in {url}: {entropy}")
        #     return True

        # Check for specific signatures
        # for signature in self.malware_signatures + self.ad_signatures + self.tracking_signatures:
        #     if re.search(signature, content, re.IGNORECASE):
        #         logging.warning(f"Signature match in {url}: {signature}")
        #         return True

        return False

    def _check_content_type(self, content, url, scope):
        domain = url.split("/")[2] if "/" in url else url

        if re.search(r"\.js($|\?)", url, re.IGNORECASE) and self._is_rule_enabled("Block JS Files"):
            return True
        if re.search(r"\.(png|jpg|jpeg|gif)($|\?)", url, re.IGNORECASE) and self._is_rule_enabled("Block Image Files"):
            return True
        if re.search(r"\.css($|\?)", url, re.IGNORECASE) and self._is_rule_enabled("Block CSS Files"):
            return True

        if self._is_rule_enabled("Block Specific URL"):
            for pattern in self.rules.get("Block Specific URL", {}).get("list", []):
                if re.search(re.escape(pattern), url, re.IGNORECASE):
                    return True

        if self._is_rule_enabled("Block Malware Domains"):
            for domain_pattern in self.rules.get("Block Malware Domains", {}).get("list", []):
                if re.search(re.escape(domain_pattern), domain, re.IGNORECASE):
                    return True

        if self._is_rule_enabled("Block Specific Text"):
            for text_pattern in self.rules.get("Block Specific Text", {}).get("list", []):
                if re.search(re.escape(text_pattern), content, re.IGNORECASE):
                    return True

        if self._is_rule_enabled("Block Ads"):
            for ad_pattern in self.rules.get("Block Ads", {}).get("list", []):
                if re.search(re.escape(ad_pattern), content, re.IGNORECASE) or re.search(re.escape(ad_pattern), url, re.IGNORECASE):
                    return True
                if scope == "Response" and any(re.search(re.escape(sig), content, re.IGNORECASE) for sig in self.tracking_signatures):
                    return True

        return False

    def _is_rule_enabled(self, rule_name):
        return rule_name in self.rules and self.rules[rule_name]["enabled"].get()

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
        if enabled and pattern not in self.blocked_patterns:
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
        logging.info(f"Alert added: {alert}")

    def update_rule_list(self, rule_name, rule_list):
        if rule_name in self.rules:
            self.rules[rule_name]["list"] = rule_list
            self.queue.put(("ALERT", f"Updated list for rule {rule_name}: {rule_list}"))
            logging.info(f"Updated list for rule {rule_name}: {rule_list}")

    def remove_block_rule(self, pattern):
        if pattern in self.blocked_patterns:
            self.blocked_patterns.remove(pattern)
            self.queue.put(("ALERT", f"Removed block rule: {pattern}"))
            logging.info(f"Blocking rule removed: {pattern}")
        if pattern in self.blocked_domains:
            self.blocked_domains.remove(pattern)
            self.queue.put(("ALERT", f"Removed block domain: {pattern}"))
            logging.info(f"Blocking domain removed: {pattern}")

async def start_proxy(firewall):
    opts = options.Options(listen_host='0.0.0.0', listen_port=8080)
    firewall.master = DumpMaster(opts, with_termlog=False, with_dumper=False)
    firewall.master.addons.add(firewall)
    await firewall.master.run()

def run_proxy(firewall):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_proxy(firewall))