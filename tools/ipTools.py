# Import modules
import sys
import socket
import ipaddress
import requests
from urllib.parse import urlparse
from tools.EMAIL.emailTools import ReadSenderEmail
from time import sleep
from colorama import Fore

def is_cloudflare_protected(link):
    parsed_uri = urlparse(link)
    domain = "{uri.netloc}".format(uri=parsed_uri)
    try:
        origin = socket.gethostbyname(domain)
        iprange = requests.get("https://www.cloudflare.com/ips-v4").text
        ipv4 = [row.rstrip() for row in iprange.splitlines()]
        for i in range(len(ipv4)):
            if ipaddress.ip_address(origin) in ipaddress.ip_network(ipv4[i]):
                print(
                    f"{Fore.RED}[!] {Fore.YELLOW}The site is protected by CloudFlare, attacks may not produce results.{Fore.RESET}"
                )
                sleep(1)
    except socket.gaierror:
        return False

def get_address_info(target):
    try:
        ip = target.split(":")[0]
        port = int(target.split(":")[1])
    except IndexError:
        print(f"{Fore.RED}[!] {Fore.MAGENTA}You must enter an IP and port{Fore.RESET}")
        sys.exit(1)
    else:
        return ip, port

def get_url_info(target):
    if not target.startswith("http"):
        target = f"http://{target}"
    return target

def get_email_message():
    server, username = ReadSenderEmail()
    subject = input(f"{Fore.BLUE}[?] {Fore.MAGENTA}Enter the Subject (leave blank for random value): ")
    body = input(f"{Fore.BLUE}[?] {Fore.MAGENTA}Enter Your Message (leave blank for random value): ")
    return [server, username, subject, body]

def get_target_address(target, method):
    if method == "SMS":
        if target.startswith("+"):
            target = target[1:]
        return target
    elif method == "EMAIL":
        email = get_email_message()
        email.append(target)
        return email
    elif method in (
        "SYN",
        "UDP",
        "NTP",
        "POD",
        "MEMCACHED",
        "ICMP",
        "SLOWLORIS",
    ) and target.startswith("http"):
        parsed_uri = urlparse(target)
        domain = "{uri.netloc}".format(uri=parsed_uri)
        origin = socket.gethostbyname(domain)
        is_cloudflare_protected(domain)
        return origin, 80
    elif method in ("SYN", "UDP", "NTP", "POD", "MEMCACHED", "ICMP", "SLOWLORIS"):
        return get_address_info(target)
    elif method == "HTTP":
        url = get_url_info(target)
        is_cloudflare_protected(url)
        return url
    else:
        return target

def internet_connection_check():
    try:
        requests.get("https://google.com", timeout=4)
    except:
        print(
            f"{Fore.RED}[!] {Fore.MAGENTA}Your device is not connected to the Internet{Fore.RESET}"
        )
        sys.exit(1)
