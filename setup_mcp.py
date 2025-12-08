"""
Auto-setup script for CAPL MCP Server
Automatically configures .gemini/settings.json or global config with correct paths
Handles merging with existing configurations
"""

import json
import os
import sys
from pathlib import Path
import argparse


def get_project_root():
    """Get the project root directory (where this script is located)"""
    return Path(__file__).parent.resolve()


def get_gemini_config_path(scope='local'):
    """Get the Gemini configuration file path"""
    if scope == 'global':
        # Global: ~/.gemini/settings.json (this is the correct location!)
        home = Path.home()
        return home / '.gemini' / 'settings.json'
    else:
        # Local: project/.gemini/settings.json
        return get_project_root() / '.gemini' / 'settings.json'


def load_existing_config(config_path):
    """Load existing configuration file or return empty structure"""
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Ensure mcpServers key exists
                if 'mcpServers' not in config:
                    config['mcpServers'] = {}
                return config
        except json.JSONDecodeError as e:
            print(f"⚠️  Warning: Could not parse existing config: {e}")
            print(f"   Creating backup and starting fresh...")
            backup_path = config_path.with_suffix('.json.backup')
            if config_path.exists():
                config_path.rename(backup_path)
                print(f"   Backup saved to: {backup_path}")
    
    return {"mcpServers": {}}


def create_mcp_server_config(project_root, server_name='vectorDoc_Server'):
    """Create MCP server configuration entry"""
    server_config = {
        "command": "python",
        "args": ["mcp_app/MCP_Server.py"],
        "cwd": str(project_root),
        "timeout": 30000,
        "trust": True
    }
    return server_config


def install_local():
    """Install MCP server for current project only"""
    project_root = get_project_root()
    config_path = get_gemini_config_path('local')
    
    print(f"\n🏠 Installing LOCAL MCP configuration...")
    
    # Create .gemini directory
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing or create new config
    config = load_existing_config(config_path)
    
    # Check if server already exists
    server_name = 'vectorDoc_Server'
    if server_name in config['mcpServers']:
        print(f"⚠️  Server '{server_name}' already exists in local config")
        print(f"   Old config: {json.dumps(config['mcpServers'][server_name], indent=6)}")
        print(f"\n   Overwriting with new configuration...")
    
    # Add/Update server configuration
    config['mcpServers'][server_name] = create_mcp_server_config(project_root, server_name)
    
    # Write config file
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Local MCP configuration installed!")
    print(f"📍 Config location: {config_path}")
    print(f"📂 Project root: {project_root}")
    print(f"🚀 MCP Server: mcp_app/MCP_Server.py")
    print(f"📋 Total servers in config: {len(config['mcpServers'])}")


def install_global():
    """Install MCP server globally for all projects"""
    project_root = get_project_root()
    config_path = get_gemini_config_path('global')
    
    print(f"\n🌍 Installing GLOBAL MCP configuration...")
    print(f"📍 Target config: {config_path}")
    
    # Create .gemini directory in home if needed
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing config (preserves ALL existing settings)
    config = load_existing_config(config_path)
    
    # Show existing structure
    existing_keys = [k for k in config.keys() if k != 'mcpServers']
    if existing_keys:
        print(f"   Found existing settings: {', '.join(existing_keys)}")
    
    server_name = 'vectorDoc_Server'
    
    # Check if server already exists
    if server_name in config['mcpServers']:
        old_config = config['mcpServers'][server_name]
        print(f"\n⚠️  Server '{server_name}' already exists in global config")
        print(f"   Old CWD: {old_config.get('cwd', 'N/A')}")
        print(f"   New CWD: {project_root}")
        print(f"\n   Overwriting with new configuration...")
    else:
        print(f"✨ Adding new server '{server_name}' to global config")
    
    # Add/Update server configuration
    config['mcpServers'][server_name] = create_mcp_server_config(project_root, server_name)
    
    # Write config file (preserves all other settings)
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Global MCP configuration installed!")
    print(f"📍 Config location: {config_path}")
    print(f"📂 Project root: {project_root}")
    print(f"🌍 Available in all Gemini projects")
    print(f"📋 Total MCP servers: {len(config['mcpServers'])}")
    
    # Show preserved settings
    if existing_keys:
        print(f"✅ Preserved existing settings: {', '.join(existing_keys)}")
    
    # Show all registered servers
    if len(config['mcpServers']) > 1:
        print(f"\n📋 All registered MCP servers:")
        for name in config['mcpServers'].keys():
            cwd = config['mcpServers'][name].get('cwd', 'N/A')
            marker = " ← NEW/UPDATED" if name == server_name else ""
            print(f"   • {name}: {cwd}{marker}")


def uninstall(scope='local'):
    """Remove MCP server configuration"""
    config_path = get_gemini_config_path(scope)
    server_name = 'vectorDoc_Server'
    
    if not config_path.exists():
        print(f"⚠️  No configuration found at {config_path}")
        return
    
    config = load_existing_config(config_path)
    
    if scope == 'local':
        # Remove entire local config
        config_path.unlink(missing_ok=True)
        # Try to remove .gemini directory if empty
        try:
            config_path.parent.rmdir()
        except OSError:
            pass  # Directory not empty
        print(f"✅ Local configuration removed: {config_path}")
    else:
        # Remove only our server from global config (preserve other settings!)
        if server_name in config.get('mcpServers', {}):
            del config['mcpServers'][server_name]
            
            # If mcpServers is now empty, remove the key but keep other settings
            if not config['mcpServers']:
                del config['mcpServers']
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Removed '{server_name}' from global configuration")
            remaining = len(config.get('mcpServers', {}))
            print(f"📋 Remaining MCP servers: {remaining}")
            
            # Show what was preserved
            other_keys = [k for k in config.keys() if k != 'mcpServers']
            if other_keys:
                print(f"✅ Preserved settings: {', '.join(other_keys)}")
        else:
            print(f"⚠️  Server '{server_name}' not found in global configuration")


def show_status():
    """Show current MCP configuration status"""
    print("\n" + "="*70)
    print("📊 CAPL MCP Server Configuration Status")
    print("="*70)
    
    project_root = get_project_root()
    print(f"\n📂 Project Root: {project_root}")
    
    mcp_server_path = project_root / 'mcp_app' / 'MCP_Server.py'
    if mcp_server_path.exists():
        print(f"🐍 MCP Server: ✅ {mcp_server_path.name}")
    else:
        print(f"🐍 MCP Server: ⚠️  NOT FOUND - {mcp_server_path}")
    
    # Check local config
    local_config_path = get_gemini_config_path('local')
    print(f"\n{'─'*70}")
    print(f"🏠 Local Configuration:")
    print(f"   Path: {local_config_path}")
    
    if local_config_path.exists():
        config = load_existing_config(local_config_path)
        print("   Status: ✅ EXISTS")
        
        # Show all settings
        all_keys = list(config.keys())
        print(f"   Settings: {', '.join(all_keys)}")
        
        servers = config.get('mcpServers', {})
        print(f"   MCP Servers: {len(servers)}")
        if servers:
            for name, server_config in servers.items():
                marker = " ✅" if name == 'vectorDoc_Server' else ""
                print(f"      • {name}{marker}")
                print(f"        CWD: {server_config.get('cwd', 'N/A')}")
    else:
        print("   Status: ❌ NOT CONFIGURED")
    
    # Check global config
    global_config_path = get_gemini_config_path('global')
    print(f"\n{'─'*70}")
    print(f"🌍 Global Configuration:")
    print(f"   Path: {global_config_path}")
    
    if global_config_path.exists():
        config = load_existing_config(global_config_path)
        print("   Status: ✅ EXISTS")
        
        # Show all settings
        all_keys = list(config.keys())
        print(f"   Settings: {', '.join(all_keys)}")
        
        servers = config.get('mcpServers', {})
        print(f"   MCP Servers: {len(servers)}")
        
        if 'vectorDoc_Server' in servers:
            print(f"\n   ✅ vectorDoc_Server is configured:")
            server_config = servers['vectorDoc_Server']
            print(f"      CWD: {server_config.get('cwd')}")
            print(f"      Command: {server_config.get('command')} {' '.join(server_config.get('args', []))}")
        else:
            if servers:
                print(f"\n   ⚠️  vectorDoc_Server NOT configured")
            else:
                print(f"\n   ℹ️  No MCP servers configured yet")
        
        # Show other MCP servers
        other_servers = [name for name in servers.keys() if name != 'vectorDoc_Server']
        if other_servers:
            print(f"\n   Other MCP servers:")
            for name in other_servers:
                print(f"      • {name}: {servers[name].get('cwd', 'N/A')}")
        
        # Show other global settings
        other_settings = {k: v for k, v in config.items() if k != 'mcpServers'}
        if other_settings:
            print(f"\n   Other Gemini settings:")
            for key in other_settings.keys():
                print(f"      • {key}")
    else:
        print("   Status: ❌ NOT CONFIGURED")
    
    print("\n" + "="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='CAPL Documentation MCP Server Setup Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup_mcp.py install --local      # Install for this project only
  python setup_mcp.py install --global     # Install globally (merges with existing settings)
  python setup_mcp.py status               # Show detailed configuration status
  python setup_mcp.py uninstall --local    # Remove local configuration
  python setup_mcp.py uninstall --global   # Remove from global (preserves other settings)

Notes:
  - Global config preserves ALL existing Gemini settings (IDE, theme, etc.)
  - Installing overwrites only the 'vectorDoc_Server' entry
  - Uninstalling removes only 'vectorDoc_Server', keeps everything else
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install MCP server')
    install_group = install_parser.add_mutually_exclusive_group(required=True)
    install_group.add_argument('--local', action='store_true', 
                              help='Install for current project only')
    install_group.add_argument('--global', action='store_true',
                              help='Install globally (merges with existing config)')
    
    # Uninstall command
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall MCP server')
    uninstall_group = uninstall_parser.add_mutually_exclusive_group(required=True)
    uninstall_group.add_argument('--local', action='store_true',
                                help='Remove local configuration')
    uninstall_group.add_argument('--global', action='store_true',
                                help='Remove from global (preserves other settings)')
    
    # Status command
    subparsers.add_parser('status', help='Show detailed configuration status')
    
    args = parser.parse_args()
    
    if args.command == 'install':
        if args.local:
            install_local()
        elif getattr(args, 'global'):
            install_global()
    
    elif args.command == 'uninstall':
        if args.local:
            uninstall('local')
        elif getattr(args, 'global'):
            uninstall('global')
    
    elif args.command == 'status':
        show_status()
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
