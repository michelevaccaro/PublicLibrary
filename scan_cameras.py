#!/usr/bin/env python3
"""
IP Camera Scanner
Scans the local network to detect IP cameras using:
  - ONVIF WS-Discovery (multicast UDP)
  - SSDP/UPnP discovery (multicast UDP)
  - Port scanning on common camera ports
  - HTTP/RTSP probing to fingerprint devices

IMPORTANT: Use only on networks you own or have explicit authorization to scan.
Unauthorized network scanning may be illegal in your jurisdiction.
"""

import socket
import struct
import threading
import ipaddress
import json
import time
import sys
import re
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Ports commonly used by IP cameras
CAMERA_PORTS = [80, 443, 554, 8080, 8081, 8082, 8083, 8443, 8554, 8888, 37777, 34567]

# HTTP paths that cameras typically expose
CAMERA_HTTP_PATHS = ["/", "/index.html", "/index.htm", "/login.html", "/admin/",
                     "/cgi-bin/viewer/video.jpg", "/video.mjpg", "/snapshot.jpg"]

# Keywords in HTTP responses that suggest a camera
CAMERA_KEYWORDS = [
    "camera", "cam", "ipcam", "ip cam", "webcam", "netcam", "nvr", "dvr",
    "hikvision", "dahua", "axis", "bosch", "hanwha", "foscam", "amcrest",
    "reolink", "uniview", "vivotek", "avigilon", "milestone", "genetec",
    "rtsp", "onvif", "video surveillance", "cctv", "ptz", "panoramic",
    "h264", "h.264", "h265", "h.265", "mpeg4",
]

# ONVIF WS-Discovery multicast probe
WS_DISCOVERY_ADDR = ("239.255.255.250", 3702)
WS_DISCOVERY_MSG = b"""<?xml version="1.0" encoding="UTF-8"?>
<e:Envelope xmlns:e="http://www.w3.org/2003/05/soap-envelope"
    xmlns:w="http://schemas.xmlsoap.org/ws/2004/08/addressing"
    xmlns:d="http://schemas.xmlsoap.org/ws/2005/04/discovery"
    xmlns:dn="http://www.onvif.org/ver10/network/wsdl">
  <e:Header>
    <w:MessageID>uuid:84ede3de-7dec-11d0-c360-F01234567890</w:MessageID>
    <w:To e:mustUnderstand="true">urn:schemas-xmlsoap-org:ws:2005:04:discovery</w:To>
    <w:Action e:mustUnderstand="true">
      http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe
    </w:Action>
  </e:Header>
  <e:Body>
    <d:Probe>
      <d:Types>dn:NetworkVideoTransmitter</d:Types>
    </d:Probe>
  </e:Body>
</e:Envelope>"""

# SSDP discovery message
SSDP_ADDR = ("239.255.255.250", 1900)
SSDP_MSG = (
    "M-SEARCH * HTTP/1.1\r\n"
    "HOST: 239.255.255.250:1900\r\n"
    'MAN: "ssdp:discover"\r\n'
    "MX: 3\r\n"
    "ST: ssdp:all\r\n"
    "\r\n"
).encode()


def get_local_subnet():
    """Detect the local network subnet by connecting to an external address."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
        return local_ip, str(network)
    except OSError as e:
        print(f"[!] Cannot detect local network: {e}", file=sys.stderr)
        return None, None


def onvif_discovery(timeout=5):
    """Send ONVIF WS-Discovery probe and collect responses."""
    found = {}
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 4)
        sock.settimeout(timeout)
        sock.sendto(WS_DISCOVERY_MSG, WS_DISCOVERY_ADDR)
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                data, addr = sock.recvfrom(65535)
                ip = addr[0]
                if ip not in found:
                    xaddrs = re.findall(r"<[^>]*XAddrs[^>]*>([^<]+)</", data.decode(errors="ignore"))
                    found[ip] = {
                        "ip": ip,
                        "method": "ONVIF WS-Discovery",
                        "details": xaddrs[0].strip() if xaddrs else "ONVIF device",
                    }
            except socket.timeout:
                break
    except OSError as e:
        print(f"[!] ONVIF discovery error: {e}", file=sys.stderr)
    finally:
        sock.close()
    return found


def ssdp_discovery(timeout=5):
    """Send SSDP M-SEARCH and collect UPnP responses, filtering camera-like devices."""
    found = {}
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 4)
        sock.settimeout(timeout)
        sock.sendto(SSDP_MSG, SSDP_ADDR)
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                data, addr = sock.recvfrom(65535)
                ip = addr[0]
                text = data.decode(errors="ignore").lower()
                if any(k in text for k in CAMERA_KEYWORDS):
                    server = re.search(r"server:\s*(.+)", text)
                    location = re.search(r"location:\s*(\S+)", text)
                    if ip not in found:
                        found[ip] = {
                            "ip": ip,
                            "method": "SSDP/UPnP",
                            "details": server.group(1).strip() if server else "UPnP camera device",
                            "location": location.group(1).strip() if location else None,
                        }
            except socket.timeout:
                break
    except OSError as e:
        print(f"[!] SSDP discovery error: {e}", file=sys.stderr)
    finally:
        sock.close()
    return found


def check_port(ip, port, timeout=1.5):
    """Return True if the TCP port is open."""
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except (OSError, ConnectionRefusedError):
        return False


def probe_http(ip, port, timeout=3):
    """
    Probe an HTTP(S) port and return (is_camera, banner) where is_camera is
    True if the response looks like a camera web interface.
    """
    schemes = ["https", "http"] if port == 443 or port == 8443 else ["http", "https"]
    for scheme in schemes:
        url = f"{scheme}://{ip}:{port}/"
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            ctx = None
            if scheme == "https":
                import ssl
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            resp = urlopen(req, timeout=timeout, context=ctx) if ctx else urlopen(req, timeout=timeout)
            body = resp.read(4096).decode(errors="ignore").lower()
            headers = str(resp.headers).lower()
            combined = body + headers
            server = resp.headers.get("Server", "")
            if any(k in combined for k in CAMERA_KEYWORDS):
                return True, server or "HTTP camera interface detected"
        except HTTPError as e:
            headers = str(e.headers).lower()
            server = e.headers.get("Server", "")
            if any(k in headers for k in CAMERA_KEYWORDS):
                return True, server or "HTTP camera interface (auth required)"
        except (URLError, OSError):
            continue
    return False, None


def probe_rtsp(ip, port=554, timeout=3):
    """Send an RTSP OPTIONS request and check for a valid RTSP response."""
    try:
        with socket.create_connection((ip, port), timeout=timeout) as s:
            s.sendall(
                f"OPTIONS rtsp://{ip}:{port}/ RTSP/1.0\r\n"
                f"CSeq: 1\r\n"
                f"User-Agent: IPCamScanner/1.0\r\n\r\n".encode()
            )
            data = s.recv(512).decode(errors="ignore")
            if "RTSP/1.0" in data or "RTSP/1.1" in data:
                server = re.search(r"Server:\s*(.+)", data, re.IGNORECASE)
                return True, server.group(1).strip() if server else "RTSP stream detected"
    except OSError:
        pass
    return False, None


def scan_host(ip):
    """
    Full probe of a single IP address.
    Returns a dict with findings, or None if no camera indicators found.
    """
    result = {"ip": ip, "open_ports": [], "indicators": [], "banner": None}

    # Check ports in parallel
    with ThreadPoolExecutor(max_workers=len(CAMERA_PORTS)) as ex:
        port_futures = {ex.submit(check_port, ip, p): p for p in CAMERA_PORTS}
        for fut in as_completed(port_futures):
            if fut.result():
                result["open_ports"].append(port_futures[fut])

    if not result["open_ports"]:
        return None

    # Probe RTSP
    if 554 in result["open_ports"] or 8554 in result["open_ports"]:
        for p in [554, 8554]:
            if p in result["open_ports"]:
                ok, banner = probe_rtsp(ip, p)
                if ok:
                    result["indicators"].append(f"RTSP on port {p}")
                    result["banner"] = banner

    # Probe HTTP(S)
    http_ports = [p for p in result["open_ports"] if p not in (554, 8554)]
    for port in http_ports:
        ok, banner = probe_http(ip, port)
        if ok:
            result["indicators"].append(f"Camera web UI on port {port}")
            if not result["banner"]:
                result["banner"] = banner

    if result["indicators"] or result["open_ports"]:
        return result
    return None


def scan_subnet(subnet, max_workers=64):
    """Scan all hosts in a subnet for camera indicators."""
    hosts = list(ipaddress.IPv4Network(subnet).hosts())
    results = []
    print(f"[*] Scanning {len(hosts)} hosts in {subnet} ...")
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(scan_host, str(h)): str(h) for h in hosts}
        done = 0
        for fut in as_completed(futures):
            done += 1
            if done % 20 == 0 or done == len(hosts):
                print(f"    Progress: {done}/{len(hosts)}", end="\r")
            r = fut.result()
            if r:
                results.append(r)
    print()
    return results


def print_report(passive_results, active_results, output_json=False):
    """Print a formatted report of all discovered cameras."""
    all_ips = {}

    for ip, info in passive_results.items():
        all_ips[ip] = info

    for r in active_results:
        ip = r["ip"]
        if ip in all_ips:
            all_ips[ip].update(r)
        else:
            all_ips[ip] = r

    if not all_ips:
        print("\n[*] No IP cameras found on the network.")
        return

    if output_json:
        print(json.dumps(list(all_ips.values()), indent=2))
        return

    print(f"\n{'='*60}")
    print(f"  IP CAMERAS FOUND: {len(all_ips)}")
    print(f"{'='*60}")
    for ip, info in sorted(all_ips.items()):
        print(f"\n  IP Address : {ip}")
        if "method" in info:
            print(f"  Discovered : {info['method']}")
        if "details" in info:
            print(f"  Details    : {info['details']}")
        if "open_ports" in info and info["open_ports"]:
            print(f"  Open ports : {', '.join(str(p) for p in sorted(info['open_ports']))}")
        if "indicators" in info and info["indicators"]:
            print(f"  Indicators : {'; '.join(info['indicators'])}")
        if "banner" in info and info["banner"]:
            print(f"  Banner     : {info['banner']}")
        if "location" in info and info.get("location"):
            print(f"  Location   : {info['location']}")
    print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Scan the local network for IP cameras.",
        epilog="IMPORTANT: Use only on networks you own or are authorized to scan."
    )
    parser.add_argument("--subnet", help="Target subnet in CIDR notation (e.g. 192.168.1.0/24). "
                                         "Auto-detected if omitted.")
    parser.add_argument("--passive-only", action="store_true",
                        help="Only use passive discovery (ONVIF, SSDP). Skip port scan.")
    parser.add_argument("--timeout", type=float, default=5.0,
                        help="Discovery timeout in seconds (default: 5)")
    parser.add_argument("--workers", type=int, default=64,
                        help="Max parallel workers for port scanning (default: 64)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    if not args.json:
        print("=" * 60)
        print("  IP Camera Scanner")
        print("  Use only on networks you own or have permission to scan.")
        print("=" * 60)

    # Determine subnet
    local_ip, auto_subnet = get_local_subnet()
    subnet = args.subnet or auto_subnet
    if not subnet:
        print("[!] Cannot determine subnet. Use --subnet to specify it.", file=sys.stderr)
        sys.exit(1)

    if not args.json:
        print(f"\n[*] Local IP  : {local_ip}")
        print(f"[*] Target    : {subnet}")

    # Phase 1: Passive discovery
    if not args.json:
        print("\n[*] Phase 1: Passive discovery (ONVIF + SSDP) ...")
    passive = {}
    t_onvif = threading.Thread(target=lambda: passive.update(onvif_discovery(args.timeout)))
    t_ssdp  = threading.Thread(target=lambda: passive.update(ssdp_discovery(args.timeout)))
    t_onvif.start()
    t_ssdp.start()
    t_onvif.join()
    t_ssdp.join()

    if not args.json:
        print(f"    Passive discovery found {len(passive)} device(s).")

    # Phase 2: Active port scan
    active = []
    if not args.passive_only:
        if not args.json:
            print("\n[*] Phase 2: Active port scan ...")
        active = scan_subnet(subnet, max_workers=args.workers)
        if not args.json:
            print(f"    Active scan found {len(active)} host(s) with camera-related ports.")

    # Report
    print_report(passive, active, output_json=args.json)


if __name__ == "__main__":
    main()
