#!/usr/bin/env python3
"""
Transformers models API documentation generator

This script generates:
1. Core modules of the transformers models package (always generated)
2. Model packages and each model's submodules (choose between all/some modes)

Usage:
    python3 generate_model_docs.py --some    # Generate only priority models defined in YAML
    python3 generate_model_docs.py --all     # Generate documentation for all models
"""

import argparse
import subprocess
import sys
import yaml
import webbrowser
import threading
import time
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Project settings
PROJECT_ROOT = Path(__file__).parent.absolute()
MODELS_DIR = PROJECT_ROOT / "src" / "transformers" / "models"
DEFAULT_API_DOCS_DIR = PROJECT_ROOT / "api_docs"
PYTHON_EXECUTABLE = PROJECT_ROOT / "venv" / "bin" / "python"
CONFIG_FILE = PROJECT_ROOT / "generate_model_docs.yaml"

# Global variable
API_DOCS_DIR = DEFAULT_API_DOCS_DIR

def load_config():
    """Load YAML configuration file."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {CONFIG_FILE}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ YAML parsing error: {e}")
        sys.exit(1)

def generate_docs_for_module(module_path, output_subdir="", timeout=180):
    """Generate API docs for a specific module."""
    try:
        output_dir = API_DOCS_DIR / output_subdir if output_subdir else API_DOCS_DIR
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            str(PYTHON_EXECUTABLE),
            "-m", "pdoc",
            module_path,
            "-o", str(output_dir)
        ]
        
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            print(f"✅ Successfully generated docs for {module_path}")
            return True
        else:
            print(f"❌ Failed to generate docs for {module_path}")
            if result.stderr:
                error_msg = result.stderr[:300]
                print(f"   Error: {error_msg}...")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout generating docs for {module_path}")
        return False
    except Exception as e:
        print(f"❌ Exception generating docs for {module_path}: {e}")
        return False

def discover_core_modules():
    """Auto-discover core modules inside src/transformers directory."""
    transformers_dir = PROJECT_ROOT / "src" / "transformers"
    skip_items = {
        'models', '__pycache__', 'tests', 'test_*', 'deprecated',
        '__init__.py', '*.pyc', '*.pyo', '.git'
    }
    
    core_modules = []
    
    if not transformers_dir.exists():
        print(f"❌ Transformers directory not found: {transformers_dir}")
        return []
    
    for item in transformers_dir.iterdir():
        if item.name.startswith('.') or item.name.startswith('__'):
            continue
            
        # check skip items
        if any(item.name == skip or item.name.startswith(skip.rstrip('*'))
               for skip in skip_items):
            continue
            
        # check if it's a Python module file
        if item.is_file() and item.suffix == '.py':
            module_name = item.stem
            if module_name != '__init__':
                core_modules.append(module_name)
    
    return sorted(core_modules)


def discover_model_submodules(model_name):
    """Auto-discover submodules inside a given model directory."""
    model_dir = MODELS_DIR / model_name
    skip_items = {'__pycache__', 'tests', 'test_*', '__init__.py'}
    
    if not model_dir.exists() or not model_dir.is_dir():
        return []
    
    submodules = []
    
    for item in model_dir.iterdir():
        if item.name.startswith('.') or item.name.startswith('__'):
            continue
            
        # check skip items
        if any(item.name == skip or item.name.startswith(skip.rstrip('*'))
               for skip in skip_items):
            continue
            
        # check if it's a Python module file
        if item.is_file() and item.suffix == '.py':
            module_name = item.stem
            if module_name != '__init__':
                submodules.append(module_name)
    
    return sorted(submodules)


def generate_core_modules():
    """Generate documentation for core transformers modules."""
    print("\n🔧 Generating Core Transformers Modules...")
    print("=" * 50)
    
    core_modules = discover_core_modules()
    success_count = 0
    
    print(f"📋 Discovered {len(core_modules)} core modules")
    
    for module in core_modules:
        module_path = f"src.transformers.{module}"
        print(f"  Processing: {module}")
        if generate_docs_for_module(module_path, "core_modules"):
            success_count += 1
    
    print(f"\n📊 Core Modules: {success_count}/{len(core_modules)} successful")
    return success_count, len(core_modules)

def get_all_model_directories():
    """Return a sorted list of all model package directories."""
    if not MODELS_DIR.exists():
        print(f"❌ Models directory not found: {MODELS_DIR}")
        return []
    
    model_dirs = []
    skip_modules = set(['deprecated', '__pycache__', 'test_modules'])
    
    for item in MODELS_DIR.iterdir():
        if item.is_dir() and item.name not in skip_modules:
            # check if it's a Python package
            if (item / "__init__.py").exists():
                model_dirs.append(item.name)
    
    return sorted(model_dirs)

def generate_model_packages(models_list):
    """Generate documentation for model packages."""
    print(f"\n📦 Generating Model Packages ({len(models_list)} models)...")
    print("=" * 50)
    
    success_count = 0
    
    for model_name in models_list:
        module_path = f"src.transformers.models.{model_name}"
        if generate_docs_for_module(module_path, "model_packages"):
            success_count += 1
    
    print(f"\n📊 Model Packages: {success_count}/{len(models_list)} successful")
    return success_count, len(models_list)

def generate_model_submodules(config, mode):
    """Generate documentation for model submodules."""
    print(f"\n🔍 Generating Model Submodules ({mode} mode)...")
    print("=" * 50)
    
    if mode == "some":
        models_list = config.get('priority_models', [])
    else:  # mode == "all"
        models_list = get_all_model_directories()
    
    total_submodules = 0
    success_count = 0
    
    for model_name in models_list:
        # auto-discover submodules for each model
        submodules = discover_model_submodules(model_name)
        
        if not submodules:
            print(f"\n📝 Processing {model_name}: No submodules found")
            continue
            
        print(f"\n📝 Processing {model_name} ({len(submodules)} submodules)...")
        print(f"    Submodules: {', '.join(submodules)}")
        
        for submodule in submodules:
            total_submodules += 1
            module_path = f"src.transformers.models.{model_name}.{submodule}"
            output_subdir = f"model_submodules/{model_name}"
            
            if generate_docs_for_module(module_path, output_subdir):
                success_count += 1
    
    print(f"\n📊 Model Submodules: {success_count}/{total_submodules} successful")
    return success_count, total_submodules

def create_comprehensive_index(stats):
    """Create a comprehensive HTML index page for generated docs."""
    print("\n📄 Creating comprehensive index page...")
    
    # scan generated documentation files
    generated_files = {
        'core_modules': [],
        'model_packages': [],
        'model_submodules': {}
    }
    
    # scan core modules
    core_dir = API_DOCS_DIR / "core_modules" / "src" / "transformers"
    if core_dir.exists():
        for file in core_dir.glob("*.html"):
            generated_files['core_modules'].append(file.stem)
    
    # scan model packages
    packages_dir = API_DOCS_DIR / "model_packages" / "src" / "transformers" / "models"
    if packages_dir.exists():
        for file in packages_dir.glob("*.html"):
            generated_files['model_packages'].append(file.stem)
    
    # scan model submodules
    submodules_dir = API_DOCS_DIR / "model_submodules"
    if submodules_dir.exists():
        for model_dir in submodules_dir.iterdir():
            if model_dir.is_dir():
                model_name = model_dir.name
                submodule_files = []
                model_docs_dir = model_dir / "src" / "transformers" / "models" / model_name
                if model_docs_dir.exists():
                    for file in model_docs_dir.glob("*.html"):
                        submodule_files.append(file.stem)
                if submodule_files:
                    generated_files['model_submodules'][model_name] = submodule_files
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>🤗 Transformers API Documentation</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{ 
            background: linear-gradient(45deg, #ff6b6b, #ffa726);
            color: white; 
            padding: 30px; 
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .stats {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px; 
            padding: 30px; 
            background: #f8f9fa;
        }}
        .stat-card {{ 
            background: white; 
            padding: 20px; 
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .content {{ padding: 30px; }}
        .section {{ margin-bottom: 40px; }}
        .section h2 {{ 
            color: #333; 
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
        }}
        .card {{ 
            background: #f8f9fa; 
            padding: 15px; 
            border-radius: 8px;
            border-left: 4px solid #667eea;
            transition: transform 0.2s;
        }}
        .card:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}
        .card a {{ 
            color: #333; 
            text-decoration: none; 
            font-weight: 500;
        }}
        .card a:hover {{ color: #667eea; }}
        .search-box {{ 
            width: 100%; 
            padding: 15px; 
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 16px;
            margin-bottom: 20px;
        }}
        .submodule-list {{ 
            margin-top: 10px; 
            padding-left: 20px; 
        }}
        .submodule-list li {{ 
            margin: 5px 0; 
            font-size: 0.9em;
            color: #666;
        }}
        .tag {{ 
            background: #667eea; 
            color: white; 
            padding: 2px 8px; 
            border-radius: 12px; 
            font-size: 0.8em;
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤗 Transformers API Documentation</h1>
            <p>Complete API Reference for Hugging Face Transformers Library</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{stats['core'][0]}</div>
                <div>Core Modules</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['packages'][0]}</div>
                <div>Model Packages</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['submodules'][0]}</div>
                <div>Submodules</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{sum(s[0] for s in stats.values())}</div>
                <div>Total Docs</div>
            </div>
        </div>
        
        <div class="content">
            <input type="text" class="search-box" placeholder="🔍 Search modules..." id="searchBox">
            
            <div class="section">
                <h2>🔧 Core Transformers Modules</h2>
                <div class="grid" id="coreModules">"""
    
    for module in sorted(generated_files['core_modules']):
        html_content += f"""
                    <div class="card">
                        <a href="core_modules/src/transformers/{module}.html">{module}</a>
                        <span class="tag">Core</span>
                    </div>"""
    
    html_content += f"""
                </div>
            </div>
            
            <div class="section">
                <h2>📦 Model Packages</h2>
                <div class="grid" id="modelPackages">"""
    
    for model in sorted(generated_files['model_packages']):
        html_content += f"""
                    <div class="card">
                        <a href="model_packages/src/transformers/models/{model}.html">{model}</a>
                        <span class="tag">Package</span>
                    </div>"""
    
    html_content += f"""
                </div>
            </div>
            
            <div class="section">
                <h2>🔍 Model Submodules</h2>
                <div class="grid" id="modelSubmodules">"""
    
    for model_name, submodules in sorted(generated_files['model_submodules'].items()):
        html_content += f"""
                    <div class="card">
                        <strong>{model_name}</strong>
                        <ul class="submodule-list">"""
        for submodule in sorted(submodules):
            html_content += f"""
                            <li><a href="model_submodules/{model_name}/src/transformers/models/{model_name}/{submodule}.html">{submodule}</a></li>"""
        html_content += f"""
                        </ul>
                    </div>"""
    
    html_content += f"""
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Search functionality
        document.getElementById('searchBox').addEventListener('input', function(e) {{
            const query = e.target.value.toLowerCase();
            const cards = document.querySelectorAll('.card');
            
            cards.forEach(card => {{
                const text = card.textContent.toLowerCase();
                card.style.display = text.includes(query) ? 'block' : 'none';
            }});
        }});
    </script>
</body>
</html>"""
    
    index_file = API_DOCS_DIR / "index.html"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Index page created: {index_file}")

def check_directory_overwrite(directory):
    """Confirm overwrite if the directory exists and is not empty."""
    if directory.exists() and any(directory.iterdir()):
        print(f"⚠️  Directory {directory} already exists and contains files.")
        response = input("Do you want to overwrite? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Operation cancelled.")
            sys.exit(0)
        print("✅ Proceeding with overwrite...")
    return True


def start_http_server(directory, port=8080):
    """Start an HTTP server serving `directory` and return the URL."""
    try:
        import os
        
        class QuietHTTPRequestHandler(SimpleHTTPRequestHandler):
            def log_message(self, format, *args):
                pass  # suppress log output
        
        server = HTTPServer(('localhost', port), QuietHTTPRequestHandler)
        
        def run_server():
            # change working directory in the server thread
            original_dir = os.getcwd()
            try:
                os.chdir(directory)
                server.serve_forever()
            finally:
                os.chdir(original_dir)
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # short wait to allow server to start
        time.sleep(0.5)
        
        return f"http://localhost:{port}/"
        
    except Exception as e:
        print(f"❌ Error starting HTTP server: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Unified Transformers API documentation generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 generate_model_docs.py --some              # Generate only priority models
  python3 generate_model_docs.py --all               # Generate all models
  python3 generate_model_docs.py --some --run        # Generate and start HTTP server
  python3 generate_model_docs.py --run               # Start HTTP server only
  python3 generate_model_docs.py --some --open       # Generate and open in browser
  python3 generate_model_docs.py --dir /path/to/docs --some  # Use custom output directory
        """
    )

    # generation mode
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--some', '-s',
        action='store_true',
        help='Generate only priority models (defined in YAML)'
    )
    mode_group.add_argument(
        '--all', '-a',
        action='store_true',
        help='Generate documentation for all models'
    )
    
    # runtime / execution options
    parser.add_argument(
        '--run', '-r',
        action='store_true',
        help='Start HTTP server and print URL'
    )
    parser.add_argument(
        '--open', '-o',
        action='store_true',
        help='Open generated docs in the system web browser'
    )
    parser.add_argument(
        '--dir', '-d',
        type=Path,
        default=DEFAULT_API_DOCS_DIR,
        help=f'API docs output / server directory (default: {DEFAULT_API_DOCS_DIR})'
    )
    
    args = parser.parse_args()
    
    # set global API_DOCS_DIR
    global API_DOCS_DIR
    API_DOCS_DIR = args.dir
    
    # If only --run is provided, start the HTTP server without generating docs
    if not args.some and not args.all and args.run:
        print("🌐 Starting HTTP server without documentation generation...")
        url = start_http_server(API_DOCS_DIR)
        if url:
            print(f"📡 Documentation server running at: {url}")
            if args.open:
                print("🔗 Opening in browser...")
                webbrowser.open(url)
            try:
                print("Press Ctrl+C to stop the server...")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Server stopped.")
        return
    
    # If no generation mode provided and --run is not used
    if not args.some and not args.all:
        parser.error("Must specify either --some/-s or --all/-a")
    
    # determine generation mode
    mode = "some" if args.some else "all"
    
    print(f" API Documentation Generation ({mode} mode)")
    print("=" * 70)
    print(f"📁 Target directory: {API_DOCS_DIR}")
    
    # Confirm overwrite if target directory exists
    check_directory_overwrite(API_DOCS_DIR)
    
    # load configuration
    config = load_config()
    
    # Create API docs directory
    API_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    
    # collect statistics
    stats = {}
    
    # 1. Generate core modules (always)
    stats['core'] = generate_core_modules()
    
    # 2. Generate model packages
    if mode == "some":
        models_list = config.get('priority_models', [])
    else:  # mode == "all"
        models_list = get_all_model_directories()
    
    stats['packages'] = generate_model_packages(models_list)
    
    # 3. Generate model submodules
    stats['submodules'] = generate_model_submodules(config, mode)
    
    # 4. Create comprehensive index
    create_comprehensive_index(stats)
    
    # Final summary
    print("\n" + "=" * 70)
    print("🎉 Documentation Generation Complete!")
    print("=" * 70)
    print("📊 Final Statistics:")
    print(f"   Core Modules: {stats['core'][0]}/{stats['core'][1]}")
    print(f"   Model Packages: {stats['packages'][0]}/{stats['packages'][1]}")
    submodule_stats = stats['submodules']
    print(f"   Model Submodules: {submodule_stats[0]}/{submodule_stats[1]}")
    print(f"   Total Success: {sum(s[0] for s in stats.values())}")
    
    # Start HTTP server or open browser
    if args.run or args.open:
        url = start_http_server(API_DOCS_DIR)
        if url:
            print(f"\n🌐 Documentation server running at: {url}")
            if args.open:
                print("🔗 Opening in browser...")
                webbrowser.open(url)
            if args.run:
                try:
                    print("Press Ctrl+C to stop the server...")
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n👋 Server stopped.")
            else:
                print("💡 Server started in background.")
    else:
        print("\n🌐 View documentation:")
        print(f"   cd {API_DOCS_DIR} && python3 -m http.server 8080")
        print("   Browser: http://localhost:8080/")


if __name__ == "__main__":
    main()
