"""
ReconWizard - Automated reconnaissance toolkit
Copyright (C) 2025 Escape

This program is free software: you can redistribute it and/or modify
it under the terms of the MIT License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
MIT License for more details.

You should have received a copy of the MIT License
along with this program. If not, see <https://opensource.org/licenses/MIT >.
"""
import os
import sys
import subprocess
from colorama import init, Fore, Style

init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_3d_banner():
    banner = r"""
██╗    ██╗██╗███████╗ █████╗ ██████╗ ██████╗     ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
██║    ██║██║╚══███╔╝██╔══██╗██╔══██╗██╔══██╗    ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
██║ █╗ ██║██║  ███╔╝ ███████║██████╔╝██║  ██║    ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
██║███╗██║██║ ███╔╝  ██╔══██║██╔══██╗██║  ██║    ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
╚███╔███╔╝██║███████╗██║  ██║██║  ██║██████╔╝    ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
 ╚══╝╚══╝ ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝     ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
                                                                                            
"""
    lines = banner.splitlines()
    colors = [
        Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA, Fore.WHITE,
        Fore.LIGHTRED_EX, Fore.LIGHTYELLOW_EX, Fore.LIGHTGREEN_EX, Fore.LIGHTCYAN_EX,
        Fore.LIGHTBLUE_EX, Fore.LIGHTMAGENTA_EX,
    ]
    for i, line in enumerate(lines):
        color = colors[i % len(colors)]
        print(color + line)

def decrypt_author():
    key = 0x23
    encrypted = [70, 80, 64, 69, 18, 81, 76, 76, 87]
    decrypted = ''.join(chr(b ^ key) for b in encrypted)
    return decrypted

def print_author_banner():
    author = decrypt_author()
    github = f"https://github.com/{author}"
    repo = "https://github.com/escf1root/recon-wizard"
    top_border = "╔════════════════════════════════════════════════════════╗"
    line1 = f"║ ⚡ Author : {author:<32}           ║"
    line2 = f"║ 🌐 GitHub : {github:<31}            ║"
    line3 = f"║ 📦 Repo   : {repo:<31}  ║"
    bot_border = "╚════════════════════════════════════════════════════════╝"

    print(Fore.BLUE + top_border)
    print(Fore.MAGENTA + line1)
    print(Fore.MAGENTA + line2)
    print(Fore.MAGENTA + line3)
    print(Fore.BLUE + bot_border)

def is_valid_domain(domain):
    import re
    pattern = r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, domain) is not None
