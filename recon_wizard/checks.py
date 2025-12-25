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
import subprocess
import shutil
from colorama import Fore, Style

def check_tool(tool_name):
    if tool_name == 'httpx':
        system_paths = ['/usr/bin/httpx', '/usr/local/bin/httpx', '/go/bin/httpx']
        for path in system_paths:
            if os.path.exists(path):
                print(Fore.GREEN + f"✅ {tool_name} (ProjectDiscovery)")
                return True
        tool_path = shutil.which(tool_name)
        if tool_path:
            try:
                result = subprocess.run(
                    [tool_path, '-version'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if 'projectdiscovery' in result.stdout.lower() or 'projectdiscovery' in result.stderr.lower():
                    print(Fore.GREEN + f"✅ {tool_name} (ProjectDiscovery)")
                    return True
                else:
                    print(Fore.YELLOW + f"⚠️  {tool_name} - Found Python version, need ProjectDiscovery Go version")
                    return False
            except:
                pass
        print(Fore.RED + f"❌ {tool_name} - NOT FOUND (need ProjectDiscovery version)")
        return False
    tool_path = shutil.which(tool_name)
    if tool_path:
        print(Fore.GREEN + f"✅ {tool_name}")
        return True
    else:
        print(Fore.RED + f"❌ {tool_name} - NOT FOUND")
        return False

def check_required_tools():
    print(Fore.MAGENTA + Style.BRIGHT + "🔍 Step 1: Checking Required Tools")
    print(Fore.MAGENTA + "-" * 70)
    
    required_tools = ['subfinder', 'httpx', 'waybackurls', 'uro', 'nuclei', 'python3']
    
    all_found = True
    for tool in required_tools:
        if not check_tool(tool):
            all_found = False
    
    if not all_found:
        print("\n" + Fore.RED + Style.BRIGHT + "🛑 Missing tools detected. Please install them first.")
        print(Fore.YELLOW + "💡 Installation guide: https://github.com/projectdiscovery")
        sys.exit(1)
    
    print(Fore.MAGENTA + "-" * 70)
    print(Fore.GREEN + Style.BRIGHT + "✅ All tools are ready!\n")
