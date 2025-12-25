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
import shutil
import time
from colorama import Fore, Style

def get_httpx_path():
    system_paths = ['/usr/bin/httpx', '/usr/local/bin/httpx', '/go/bin/httpx']
    for path in system_paths:
        if os.path.exists(path):
            return path
    
    tool_path = shutil.which('httpx')
    if tool_path:
        try:
            result = subprocess.run(
                [tool_path, '-version'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if 'projectdiscovery' in result.stdout.lower() or 'projectdiscovery' in result.stderr.lower():
                return tool_path
        except:
            pass
    
    return 'httpx'

def run_command(command, step_name, output_file=None, check_output=False, allow_skip=False):
    print(f"\n{Fore.CYAN}▶️  {Style.BRIGHT}{step_name}")
    print(Fore.CYAN + "─" * 70)
    
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        try:
            for line in process.stdout:
                print(Fore.WHITE + line.rstrip())
        except KeyboardInterrupt:
            print("\n\n" + Fore.YELLOW + "⚠️  Process interrupted by user (Ctrl+C)")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            
            if allow_skip:
                print(Fore.YELLOW + "⏭️  Skipping this step and continuing to next...")
            else:
                print(Fore.RED + "⏭️  Critical step interrupted. Attempting to continue to next steps...")
            return True
        
        process.wait()
        
        if check_output and output_file:
            if not os.path.exists(output_file):
                print(Fore.RED + f"❌ FAILED: Output file not created - {os.path.basename(output_file)}")
                print(Fore.RED + "⏭️  Critical step failed. Attempting to continue to next steps...")
                return True
            
            file_size = os.path.getsize(output_file)
            if file_size == 0:
                print(Fore.YELLOW + f"⚠️  WARNING: Output file is empty - {os.path.basename(output_file)}")
                print(Fore.RED + "⏭️  Critical step produced empty output. Attempting to continue to next steps...")
                return True
            
            print(Fore.GREEN + f"✅ SUCCESS: {os.path.basename(output_file)} created ({file_size} bytes)")
            return True
        
        if output_file:
            if os.path.exists(output_file):
                size = os.path.getsize(output_file)
                if size > 0:
                    print(Fore.GREEN + f"✅ Completed - Output: {os.path.basename(output_file)} ({size} bytes)")
                else:
                    print(Fore.YELLOW + f"⚠️  Completed - Output: {os.path.basename(output_file)} (0 bytes - no results found)")
            else:
                print(Fore.YELLOW + f"⚠️  Completed - No output file generated")
        
        return True
            
    except Exception as e:
        print(Fore.RED + f"❌ ERROR: {e}")
        print(Fore.RED + "⏭️  An error occurred. Attempting to continue to next steps...")
        return True

def run_recon(target, output_dir, secretfinder_script, nuclei_templates):
    print("\n" + Fore.GREEN + Style.BRIGHT + "="*70)
    print(Fore.GREEN + Style.BRIGHT + "   🚀 Step 5: Starting Automated Reconnaissance")
    print(Fore.GREEN + Style.BRIGHT + "="*70)
    
    httpx_cmd = get_httpx_path()
    print(Fore.CYAN + f"ℹ️  Using httpx: {httpx_cmd}\n")
    
    subdomain_file = os.path.join(output_dir, "subdomain.txt")
    aktif_sub_file = os.path.join(output_dir, "aktif_sub.txt")
    urls_file = os.path.join(output_dir, "urls.txt")
    filter_urls_file = os.path.join(output_dir, "filter_urls.txt")
    info_file = os.path.join(output_dir, "info.txt")
    js_file = os.path.join(output_dir, "js.txt")
    secret_file = os.path.join(output_dir, "secret.txt")
    
    print(Fore.BLUE + "🚀 Starting Step 1: Subfinder")
    cmd = f"subfinder -d {target} -all -recursive -o {subdomain_file}"
    run_command(cmd, "1/9 Subfinder - Enumerating subdomains", subdomain_file, check_output=True)
    print(Fore.BLUE + "✅ Step 1 completed (or skipped). Checking results...")
    
    print("\n" + Fore.BLUE + "🚀 Starting Step 2: Httpx")
    if os.path.exists(subdomain_file) and os.path.getsize(subdomain_file) > 0:
        cmd = f"cat {subdomain_file} | {httpx_cmd} -fc 403,404 -o {aktif_sub_file}"
        run_command(cmd, "2/9 Httpx - Filtering active subdomains", aktif_sub_file, check_output=True)
        print(Fore.BLUE + "✅ Step 2 completed (or skipped). Checking results...")
    else:
        print(Fore.YELLOW + "⚠️  Skipping Step 2: Httpx - No subdomains found from Step 1.")
    
    print("\n" + Fore.BLUE + "🚀 Starting Step 3: Waybackurls")
    if os.path.exists(aktif_sub_file) and os.path.getsize(aktif_sub_file) > 0:
        cmd = f"cat {aktif_sub_file} | waybackurls | tee {urls_file}"
        run_command(cmd, "3/9 Waybackurls - Fetching archived URLs", urls_file, check_output=True)
        print(Fore.BLUE + "✅ Step 3 completed (or skipped). Checking results...")
    else:
        print(Fore.YELLOW + "⚠️  Skipping Step 3: Waybackurls - No active subdomains found from Step 2.")
    
    print("\n" + Fore.BLUE + "🚀 Starting Step 4: Uro")
    if os.path.exists(urls_file) and os.path.getsize(urls_file) > 0:
        cmd = f"cat {urls_file} | uro | tee {filter_urls_file}"
        run_command(cmd, "4/9 Uro - Cleaning duplicate URLs", filter_urls_file, check_output=True)
        print(Fore.BLUE + "✅ Step 4 completed (or skipped). Checking results...")
    else:
        print(Fore.YELLOW + "⚠️  Skipping Step 4: Uro - No URLs found from Step 3.")
    
    print("\n" + Fore.BLUE + "🚀 Starting Step 5: Grep (Sensitive Files)")
    if os.path.exists(filter_urls_file) and os.path.getsize(filter_urls_file) > 0:
        cmd = f"cat {filter_urls_file} | grep -E \"\\.log|\\.cache|\\.secret|\\.db|\\.backup|\\.yml|\\.gz|\\.rar|\\.zip|\\.config\" | tee {info_file}"
        run_command(cmd, "5/9 Grep - Filtering sensitive files", info_file)
        print(Fore.BLUE + "✅ Step 5 completed (or skipped).")
    else:
        print(Fore.YELLOW + "⚠️  Skipping Step 5: Grep (Sensitive Files) - No URLs found from Step 4.")
    
    print("\n" + Fore.BLUE + "🚀 Starting Step 6: Grep (JavaScript Files)")
    if os.path.exists(filter_urls_file) and os.path.getsize(filter_urls_file) > 0:
        cmd = f"cat {filter_urls_file} | grep \".js$\" | tee {js_file}"
        run_command(cmd, "6/9 Grep - Extracting JavaScript files", js_file)
        print(Fore.BLUE + "✅ Step 6 completed (or skipped).")
    else:
        print(Fore.YELLOW + "⚠️  Skipping Step 6: Grep (JavaScript Files) - No URLs found from Step 4.")
    
    print(f"\n{Fore.MAGENTA}▶️  7/9 SecretFinder - Analyzing JavaScript files")
    print(Fore.MAGENTA + "─" * 70)
    
    if not os.path.exists(js_file) or os.path.getsize(js_file) == 0:
        print(Fore.YELLOW + "⚠️  No JavaScript files found, skipping SecretFinder")
    else:
        try:
            with open(js_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            print(Fore.CYAN + f"📦 Found {len(urls)} JavaScript files to analyze")
            print(Fore.YELLOW + "💡 Press Ctrl+C to skip this step if needed\n")
            
            with open(secret_file, 'w') as secret_out:
                for idx, url in enumerate(urls, 1):
                    try:
                        print(Fore.CYAN + f"   [{idx}/{len(urls)}] {url}")
                        
                        cmd = f"python3 {secretfinder_script} -i \"{url}\" -o cli"
                        result = subprocess.run(
                            cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            check=False,
                            timeout=30
                        )
                        
                        if result.stdout:
                            secret_out.write(f"\n{'='*60}\n")
                            secret_out.write(f"URL: {url}\n")
                            secret_out.write(f"{'='*60}\n")
                            secret_out.write(result.stdout)
                            secret_out.write("\n")
                        
                        time.sleep(0.3)
                        
                    except KeyboardInterrupt:
                        print("\n\n" + Fore.YELLOW + "⚠️  SecretFinder interrupted by user (Ctrl+C)")
                        print(Fore.YELLOW + "⏭️  Skipping remaining JavaScript files and continuing...")
                        break
                    except subprocess.TimeoutExpired:
                        print(Fore.YELLOW + f"   ⏱️  Timeout - skipping this URL")
                        continue
                    except Exception as e:
                        print(Fore.YELLOW + f"   ⚠️  Error: {e}")
                        continue
            
            print(f"\n{Fore.GREEN}✅ Completed - Output: {os.path.basename(secret_file)}")
            
        except KeyboardInterrupt:
            print("\n\n" + Fore.YELLOW + "⚠️  SecretFinder interrupted by user (Ctrl+C)")
            print(Fore.YELLOW + "⏭️  Skipping to next step...")
        except Exception as e:
            print(Fore.YELLOW + f"⚠️  SecretFinder error: {e}")
    
    print(f"\n{Fore.MAGENTA}▶️  8/9 Grep - Filtering secrets by keywords")
    print(Fore.MAGENTA + "─" * 70)
    
    if os.path.exists(secret_file):
        keywords = ['aws', 'twilio', 'google', 'heroku', 'api', 'key', 'token', 'secret']
        for keyword in keywords:
            cmd = f"cat {secret_file} | grep -i {keyword}"
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True, check=False)
            if result.stdout:
                print(Fore.MAGENTA + f"   🔑 Found: {keyword}")
        print(Fore.MAGENTA + "✅ Keyword filtering completed")
    else:
        print(Fore.YELLOW + "⚠️  No secret file to filter")
    
    print(f"\n{Fore.RED}▶️  9/9 Nuclei - Vulnerability scanning")
    print(Fore.RED + "─" * 70)
    
    try:
        confirm = input(Fore.WHITE + "Run Nuclei vulnerability scan? (y/n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n" + Fore.YELLOW + "⏭️  Skipping Nuclei scan")
        confirm = 'n'
    
    if confirm in ['y', 'yes']:
        if os.path.exists(filter_urls_file) and os.path.getsize(filter_urls_file) > 0:
            if nuclei_templates:
                print("\n" + Fore.CYAN + "   Scanning with custom templates directory...")
                nuclei_output = os.path.join(output_dir, "nuclei_custom_scan.txt")
                cmd = f"nuclei -l {filter_urls_file} -t {nuclei_templates} -ept ssl -o {nuclei_output}"
                run_command(cmd, f"Nuclei - Custom Templates Scan", nuclei_output, allow_skip=True)
                print("\n" + Fore.GREEN + "✅ Custom Nuclei scanning completed")
            else:
                severity_levels = ['low', 'medium', 'high', 'critical']
                
                for severity in severity_levels:
                    nuclei_output = os.path.join(output_dir, f"nuclei_{severity}.txt")
                    
                    cmd = f"nuclei -l {filter_urls_file} -s {severity} -ept ssl -o {nuclei_output}"
                    
                    print(f"\n   Scanning: {Fore.RED + Style.BRIGHT}{severity.upper()}{Fore.WHITE} severity")
                    if not run_command(cmd, f"Nuclei - {severity}", nuclei_output, allow_skip=True):
                        print(Fore.YELLOW + f"⏭️  Skipping remaining severity levels...")
                        break
                
                print("\n" + Fore.GREEN + "✅ Default Nuclei scanning (by severity) completed")
        else:
            print(Fore.YELLOW + "⚠️  Skipping Nuclei scan - No URLs found from Step 4.")
    else:
        print(Fore.YELLOW + "⏭️  Skipped Nuclei scanning")
    
    print("\n" + Fore.GREEN + Style.BRIGHT + "="*70)
    print(Fore.GREEN + Style.BRIGHT + "   ✅ RECONNAISSANCE COMPLETED")
    print(Fore.GREEN + Style.BRIGHT + "="*70)
    print(f"\n{Fore.CYAN}📁 Results saved in: {output_dir}")
    print("\n" + Fore.CYAN + "📄 Generated files:")
    
    files = [
        "subdomain.txt",
        "aktif_sub.txt", 
        "urls.txt",
        "filter_urls.txt",
        "info.txt",
        "js.txt",
        "secret.txt"
    ]
    
    for f in files:
        filepath = os.path.join(output_dir, f)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"   {Fore.GREEN}✅ {f} ({size} bytes)")
        else:
            print(f"   {Fore.RED}❌ {f} (File not created)")
    
    if nuclei_templates:
        custom_nuclei_file = os.path.join(output_dir, "nuclei_custom_scan.txt")
        if os.path.exists(custom_nuclei_file):
            size = os.path.getsize(custom_nuclei_file)
            print(f"   {Fore.GREEN}✅ nuclei_custom_scan.txt ({size} bytes)")
        else:
            print(f"   {Fore.RED}❌ nuclei_custom_scan.txt (File not created or scan skipped)")
    else:
        for severity in ['low', 'medium', 'high', 'critical']:
            filepath = os.path.join(output_dir, f"nuclei_{severity}.txt")
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"   {Fore.GREEN}✅ nuclei_{severity}.txt ({size} bytes)")
    
    print("\n" + Fore.GREEN + Style.BRIGHT + "="*70)
    print(Fore.YELLOW + "💡 Review the files above to identify potential vulnerabilities")
    print(Fore.CYAN + "👋 Happy bug hunting!")
    print(Fore.GREEN + Style.BRIGHT + "="*70)
