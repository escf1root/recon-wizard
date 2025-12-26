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
import argparse
import logging
from colorama import init, Fore, Style


init(autoreset=True)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        
        logging.StreamHandler(sys.stdout)  
    ]
)

from recon_wizard.utils import clear_screen, print_3d_banner, print_author_banner, is_valid_domain
from recon_wizard.checks import check_required_tools
from recon_wizard.recon import run_recon

def print_colored_help():
    print(Fore.CYAN + Style.BRIGHT + "Automated Reconnaissance Tool")
    print("\n" + Fore.YELLOW + "Usage:")
    print(Fore.WHITE + "  python3 main.py -t <domain> [OPTIONS]\n")

    print(Fore.YELLOW + "Options:")
    print(Fore.GREEN + "  -t, --target TARGET" + Fore.WHITE + "\t\tTarget domain to scan (e.g., example.com)")
    print(Fore.GREEN + "  -o, --output-dir OUTPUT_DIR" + Fore.WHITE + "\tDirectory to save results (default: ./results)")
    print(Fore.GREEN + "  -sf, --secretfinder-path PATH" + Fore.WHITE + "\tPath to SecretFinder.py script (default: ./SecretFinder.py)")
    print(Fore.GREEN + "  -nt, --nuclei-templates PATH" + Fore.WHITE + "\tPath to custom Nuclei templates directory.")
    print(Fore.WHITE + "\t\t\t\tIf not provided, default Nuclei templates are used.")
    print(Fore.GREEN + "  -h, --help" + Fore.WHITE + "\t\t\tShow this help message and exit\n")

    print(Fore.MAGENTA + "Example:")
    print(Fore.CYAN + "  python3 main.py -t example.com -o ./results -nt /path/to/templates\n")

def main():
    
    if "-h" in sys.argv or "--help" in sys.argv:
        print_colored_help()
        sys.exit(0)

    parser = argparse.ArgumentParser(add_help=False)  
    parser.add_argument('-t', '--target', required=True, help=argparse.SUPPRESS)
    parser.add_argument('-o', '--output-dir', default='./results', help=argparse.SUPPRESS)
    parser.add_argument('-sf', '--secretfinder-path', default='./SecretFinder.py', help=argparse.SUPPRESS)
    parser.add_argument('-nt', '--nuclei-templates', help=argparse.SUPPRESS)

    args = parser.parse_args()

    
    if not is_valid_domain(args.target):
        error_msg = f"❌ Invalid domain format: {args.target}"
        print(Fore.RED + error_msg)
        logging.error(error_msg)
        sys.exit(1)
    logging.info(f"Target domain validated: {args.target}")

    clear_screen()
    print_3d_banner()
    print("\n")
    print_author_banner()
    print()

    try:
        
        logging.info("Checking required tools...")
        check_required_tools()
        logging.info("All required tools are available.")

        
        output_dir = args.output_dir
        logging.info(f"Setting up output directory: {output_dir}")

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                logging.info(f"Created output directory: {output_dir}")
                print(Fore.GREEN + f"✅ Created directory: {output_dir}")
            except PermissionError:
                error_msg = f"❌ Permission denied: Cannot create directory '{output_dir}'. Check path and permissions (e.g., use './{output_dir}' instead of '/{output_dir}' if not using sudo)."
                print(Fore.RED + error_msg)
                logging.critical(error_msg)
                sys.exit(1)
            except Exception as e:
                error_msg = f"❌ Failed to create directory '{output_dir}': {e}"
                print(Fore.RED + error_msg)
                logging.critical(error_msg)
                sys.exit(1)
        else:
            logging.info(f"Using existing output directory: {output_dir}")
            print(Fore.GREEN + f"✅ Using existing directory: {output_dir}")

        
        secretfinder_path_arg = args.secretfinder_path
        logging.info(f"Validating SecretFinder script path: {secretfinder_path_arg}")

        
        if os.path.isfile(secretfinder_path_arg):
            
            secretfinder_script = secretfinder_path_arg
            logging.info(f"SecretFinder script provided directly: {secretfinder_script}")
        elif os.path.isdir(secretfinder_path_arg):
            
            possible_script_paths = [
                os.path.join(secretfinder_path_arg, 'SecretFinder.py'),
                os.path.join(secretfinder_path_arg, 'secretfinder.py'),
                os.path.join(secretfinder_path_arg, 'SecretFinder', 'SecretFinder.py'), 
                os.path.join(secretfinder_path_arg, 'secretfinder', 'secretfinder.py'),
            ]
            found_script = False
            for path in possible_script_paths:
                if os.path.isfile(path):
                    secretfinder_script = path
                    logging.info(f"Found SecretFinder script in directory: {secretfinder_script}")
                    found_script = True
                    break

            if not found_script:
                error_msg = f"❌ SecretFinder.py not found in directory: {secretfinder_path_arg}. Looked for common names like SecretFinder.py, secretfinder.py, etc."
                print(Fore.RED + error_msg)
                logging.critical(error_msg)
                sys.exit(1)
        else:
            error_msg = f"❌ Path does not exist or is not a file/directory: {secretfinder_path_arg}"
            print(Fore.RED + error_msg)
            logging.critical(error_msg)
            sys.exit(1)

        logging.info(f"SecretFinder script validated: {secretfinder_script}")
        print(Fore.GREEN + f"✅ SecretFinder script: {secretfinder_script}")

        
        nuclei_templates = args.nuclei_templates
        if nuclei_templates:
            logging.info(f"Validating Nuclei templates path: {nuclei_templates}")
            if not os.path.exists(nuclei_templates):
                error_msg = f"❌ Nuclei templates directory not found: {nuclei_templates}"
                print(Fore.RED + error_msg)
                logging.critical(error_msg)
                sys.exit(1)
            if not os.path.isdir(nuclei_templates):
                error_msg = f"❌ Nuclei templates path is not a directory: {nuclei_templates}"
                print(Fore.RED + error_msg)
                logging.critical(error_msg)
                sys.exit(1)
            logging.info(f"Nuclei templates validated: {nuclei_templates}")
            print(Fore.GREEN + f"✅ Nuclei templates: {nuclei_templates}")
        else:
            logging.info("No custom Nuclei templates specified. Using default templates.")
            print(Fore.YELLOW + "ℹ️  Using default Nuclei templates")

        print(Fore.GREEN + f"✅ Target set: {args.target}")
        print("\n")

        
        logging.info("Starting reconnaissance process...")
        run_recon(args.target, output_dir, secretfinder_script, nuclei_templates)
        logging.info("Reconnaissance process completed.")

    except KeyboardInterrupt:
        print("\n\n" + Fore.YELLOW + "⚠️  Process interrupted by user (Ctrl+C)")
        logging.warning("Process interrupted by user.")
        sys.exit(0)
    except Exception as e:
        error_msg = f"\n{Fore.RED}❌ Unexpected error occurred: {e}"
        print(error_msg)
        logging.critical(f"Unexpected error: {e}", exc_info=True) 
        sys.exit(1)

if __name__ == "__main__":
    main()
