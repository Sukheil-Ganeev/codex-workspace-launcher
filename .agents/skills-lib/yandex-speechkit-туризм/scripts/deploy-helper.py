#!/usr/bin/env python3
import argparse, sys, json, subprocess
from pathlib import Path

try:
    from rich.console import Console
    from rich.prompt import Confirm
except ImportError:
    print('ERROR: pip install rich')
    sys.exit(1)

console = Console()

class DeploymentHelper:
    PLATFORMS = ['vercel', 'netlify', 'railway']
    
    def __init__(self, platform: str):
        self.platform = platform
    
    def check_cli(self) -> bool:
        try:
            subprocess.run([self.platform, '--version'], capture_output=True, check=True)
            console.print(f'[green]{self.platform} CLI found[/green]')
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            console.print(f'[red]{self.platform} CLI not found. Install: npm install -g {self.platform}[/red]')
            return False
    
    def deploy(self) -> bool:
        console.print(f'[cyan]Deploying to {self.platform}...[/cyan]')
        
        if self.platform == 'vercel':
            cmd = ['vercel', '--prod']
        elif self.platform == 'netlify':
            cmd = ['netlify', 'deploy', '--prod']
        elif self.platform == 'railway':
            cmd = ['railway', 'up']
        else:
            return False
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                console.print('[green]Deployment successful![/green]')
                return True
            else:
                console.print('[red]Deployment failed![/red]')
                console.print(result.stderr)
                return False
        except Exception as e:
            console.print(f'[red]Error: {e}[/red]')
            return False
    
    def health_check(self, url: str) -> bool:
        try:
            import requests
            response = requests.get(f'{url}/health', timeout=10)
            
            if response.status_code == 200:
                console.print('[green]Health check passed![/green]')
                return True
            else:
                console.print(f'[yellow]Health check returned {response.status_code}[/yellow]')
                return False
        except Exception as e:
            console.print(f'[red]Health check failed: {e}[/red]')
            return False

def main():
    parser = argparse.ArgumentParser(description='Deploy Yandex SpeechKit webhook')
    parser.add_argument('--platform', '-p', choices=['vercel', 'netlify', 'railway'], required=True)
    parser.add_argument('--url', '-u', type=str, help='Deployment URL for health check')
    parser.add_argument('--health-check', action='store_true', help='Run health check only')
    args = parser.parse_args()
    
    helper = DeploymentHelper(args.platform)
    
    if args.health_check:
        if not args.url:
            console.print('[red]Error: --url required for health check[/red]')
            sys.exit(1)
        helper.health_check(args.url)
        return
    
    if not helper.check_cli():
        sys.exit(1)
    
    if Confirm.ask('Ready to deploy?'):
        success = helper.deploy()
        
        if success and args.url:
            helper.health_check(args.url)
        
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
