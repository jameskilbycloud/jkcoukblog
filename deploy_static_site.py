#!/usr/bin/env python3
"""
Automated WordPress to Static Site Deployment
Complete solution with multiple deployment targets
"""

import os
import sys
import json
import subprocess
import time
import shutil
from pathlib import Path
from wp_to_static_generator import WordPressStaticGenerator

class StaticSiteDeployer:
    def __init__(self, output_dir, target_domain):
        self.output_dir = Path(output_dir)
        self.target_domain = target_domain
        
    def deploy_to_cloudflare_pages(self, project_name):
        """Deploy to Cloudflare Pages using Wrangler CLI"""
        print("☁️ Deploying to Cloudflare Pages...")
        
        try:
            cmd = [
                'wrangler', 'pages', 'publish', str(self.output_dir),
                '--project-name', project_name,
                '--compatibility-date', '2023-09-01'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Cloudflare Pages deployment successful!")
                print(f"📄 Output: {result.stdout}")
                return True
            else:
                print(f"❌ Cloudflare deployment failed:")
                print(f"📄 Error: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("❌ Wrangler CLI not found. Install with: npm install -g wrangler")
            return False
        except Exception as e:
            print(f"❌ Deployment error: {e}")
            return False
    
    def deploy_to_netlify(self, site_id=None):
        """Deploy to Netlify using Netlify CLI"""
        print("🌐 Deploying to Netlify...")
        
        try:
            if site_id:
                cmd = ['netlify', 'deploy', '--prod', '--dir', str(self.output_dir), '--site', site_id]
            else:
                cmd = ['netlify', 'deploy', '--prod', '--dir', str(self.output_dir)]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Netlify deployment successful!")
                print(f"📄 Output: {result.stdout}")
                return True
            else:
                print(f"❌ Netlify deployment failed:")
                print(f"📄 Error: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("❌ Netlify CLI not found. Install with: npm install -g netlify-cli")
            return False
        except Exception as e:
            print(f"❌ Deployment error: {e}")
            return False
    
    def deploy_to_aws_s3(self, bucket_name, aws_profile=None):
        """Deploy to AWS S3 using AWS CLI"""
        print("📦 Deploying to AWS S3...")
        
        try:
            cmd = ['aws', 's3', 'sync', str(self.output_dir), f's3://{bucket_name}/', '--delete']
            
            if aws_profile:
                cmd.extend(['--profile', aws_profile])
            
            # Add cache control headers
            cmd.extend(['--cache-control', 'max-age=86400'])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ AWS S3 deployment successful!")
                print(f"📄 Output: {result.stdout}")
                return True
            else:
                print(f"❌ AWS S3 deployment failed:")
                print(f"📄 Error: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("❌ AWS CLI not found. Install with: pip install awscli")
            return False
        except Exception as e:
            print(f"❌ Deployment error: {e}")
            return False
    
    def deploy_via_rsync(self, remote_host, remote_path, ssh_key=None):
        """Deploy via rsync/SSH"""
        print(f"🔄 Deploying via rsync to {remote_host}...")
        
        try:
            cmd = [
                'rsync', '-avz', '--delete',
                f'{self.output_dir}/',
                f'{remote_host}:{remote_path}'
            ]
            
            if ssh_key:
                cmd.insert(1, f'-e ssh -i {ssh_key}')
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Rsync deployment successful!")
                print(f"📄 Output: {result.stdout}")
                return True
            else:
                print(f"❌ Rsync deployment failed:")
                print(f"📄 Error: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("❌ Rsync not found.")
            return False
        except Exception as e:
            print(f"❌ Deployment error: {e}")
            return False
    
    def deploy_to_git_repo(self, target_dir='public'):
        """Commit static site to git repository"""
        print(f"📝 Committing static site to git repository...")
        
        try:
            import subprocess
            from datetime import datetime
            
            # Remove existing target directory
            target_path = Path(target_dir)
            if target_path.exists():
                shutil.rmtree(target_path)
            
            # Copy static files to target directory
            shutil.copytree(self.output_dir, target_path)
            
            # Git operations
            subprocess.run(['git', 'add', target_dir], check=True)
            
            # Check if there are changes to commit
            result = subprocess.run(['git', 'diff', '--cached', '--exit-code'], 
                                  capture_output=True)
            
            if result.returncode != 0:  # There are changes
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                commit_msg = f"🚀 Auto-update static site - {timestamp}"
                
                subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
                print(f"✅ Changes committed: {commit_msg}")
                
                # Push if on a branch with upstream
                try:
                    subprocess.run(['git', 'push'], check=True)
                    print("✅ Changes pushed to remote repository")
                except subprocess.CalledProcessError:
                    print("⚠️  Could not push - you may need to push manually")
                
                return True
            else:
                print("ℹ️  No changes to commit")
                return True
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Git operation failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Deployment error: {e}")
            return False
    
    def start_local_server(self, port=8000):
        """Start a local HTTP server for testing"""
        print(f"🌐 Starting local server on port {port}...")
        print(f"📍 URL: http://localhost:{port}")
        print("Press Ctrl+C to stop")
        
        try:
            os.chdir(self.output_dir)
            subprocess.run([
                sys.executable, '-m', 'http.server', str(port)
            ])
        except KeyboardInterrupt:
            print("\\n🛑 Server stopped")

def create_github_action_workflow():
    """Create a GitHub Actions workflow file"""
    workflow_content = '''name: WordPress to Static Site Deploy

on:
  schedule:
    - cron: '0 6,18 * * *'  # Twice daily at 6 AM and 6 PM UTC
  workflow_dispatch:        # Manual trigger
  repository_dispatch:      # Webhook trigger
    types: [wordpress-update]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        pip install requests beautifulsoup4
        
    - name: Generate static site
      env:
        WP_AUTH_TOKEN: ${{ secrets.WP_AUTH_TOKEN }}
      run: |
        python wp_to_static_generator.py ./static-output
        
    - name: Deploy to Cloudflare Pages
      env:
        CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
      run: |
        npm install -g wrangler
        wrangler pages publish ./static-output \\
          --project-name=jameskilby-co-uk \\
          --compatibility-date=2023-09-01
          
    - name: Notify on success
      if: success()
      run: |
        echo "✅ Static site deployed successfully!"
        
    - name: Notify on failure
      if: failure()
      run: |
        echo "❌ Static site deployment failed!"
'''

    workflow_dir = Path('.github/workflows')
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_file = workflow_dir / 'deploy-static-site.yml'
    workflow_file.write_text(workflow_content)
    
    print(f"✅ Created GitHub Actions workflow: {workflow_file}")
    print("📝 Don't forget to add these secrets to your GitHub repository:")
    print("   - WP_AUTH_TOKEN: Your WordPress Basic Auth token")
    print("   - CLOUDFLARE_API_TOKEN: Your Cloudflare API token")

def create_cron_script():
    """Create a cron script for automated deployment"""
    script_content = f'''#!/bin/bash
# Automated WordPress to Static Site Deployment
# Add to cron with: 0 6,18 * * * /path/to/this/script

set -e

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/static-output"
LOG_FILE="$SCRIPT_DIR/deploy.log"

echo "🚀 Starting automated deployment at $(date)" >> "$LOG_FILE"

cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d "wordpress_spellcheck_env" ]; then
    source wordpress_spellcheck_env/bin/activate
fi

# Generate static site
python wp_to_static_generator.py "$OUTPUT_DIR" >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Static site generation successful at $(date)" >> "$LOG_FILE"
    
    # Deploy (customize this section for your deployment target)
    python deploy_static_site.py "$OUTPUT_DIR" --cloudflare jameskilby-co-uk >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Deployment successful at $(date)" >> "$LOG_FILE"
    else
        echo "❌ Deployment failed at $(date)" >> "$LOG_FILE"
    fi
else
    echo "❌ Static site generation failed at $(date)" >> "$LOG_FILE"
fi

echo "📝 Log file: $LOG_FILE"
'''

    script_file = Path('automated_deploy.sh')
    script_file.write_text(script_content)
    script_file.chmod(0o755)  # Make executable
    
    print(f"✅ Created cron deployment script: {script_file}")
    print("📝 To schedule, add to cron with:")
    print(f"   0 6,18 * * * {script_file.absolute()}")

def main():
    if len(sys.argv) < 2:
        print("WordPress to Static Site Deployment Tool")
        print("=" * 50)
        print("Usage: python deploy_static_site.py <command> [options]")
        print()
        print("Commands:")
        print("  generate <output_dir>              - Generate static site only")
        print("  deploy <output_dir> <target>       - Deploy existing static site")
        print("  full <output_dir> <target>         - Generate and deploy")
        print("  server <output_dir> [port]         - Start local test server")
        print("  setup-github                       - Create GitHub Actions workflow")
        print("  setup-cron                         - Create cron deployment script")
        print()
        print("Deployment targets:")
        print("  --cloudflare <project-name>        - Deploy to Cloudflare Pages")
        print("  --netlify [site-id]                - Deploy to Netlify")
        print("  --s3 <bucket-name> [profile]       - Deploy to AWS S3")
        print("  --rsync <host:path> [ssh-key]      - Deploy via rsync")
        print("  --git [directory]                  - Commit to git repository")
        print()
        print("Examples:")
        print("  python deploy_static_site.py generate ./static")
        print("  python deploy_static_site.py full ./static --cloudflare jameskilby-co-uk")
        print("  python deploy_static_site.py server ./static 8080")
        print("  python deploy_static_site.py setup-github")
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Configuration
    WP_URL = 'https://wordpress.jameskilby.cloud'
    AUTH_TOKEN = os.getenv('WP_AUTH_TOKEN')  # Use environment variable
    
    if not AUTH_TOKEN:
        print('❌ Error: WP_AUTH_TOKEN environment variable is required')
        print('   Set it with: export WP_AUTH_TOKEN="your_token_here"')
        sys.exit(1)
    TARGET_DOMAIN = 'https://jameskilby.co.uk'
    
    if command == 'generate':
        if len(sys.argv) < 3:
            print("Usage: python deploy_static_site.py generate <output_dir>")
            sys.exit(1)
        
        output_dir = sys.argv[2]
        
        generator = WordPressStaticGenerator(
            wp_url=WP_URL,
            auth_token=AUTH_TOKEN,
            output_dir=output_dir,
            target_domain=TARGET_DOMAIN
        )
        
        success = generator.generate_static_site()
        if not success:
            sys.exit(1)
    
    elif command == 'deploy':
        if len(sys.argv) < 4:
            print("Usage: python deploy_static_site.py deploy <output_dir> <target>")
            sys.exit(1)
        
        output_dir = sys.argv[2]
        deployer = StaticSiteDeployer(output_dir, TARGET_DOMAIN)
        
        target = sys.argv[3]
        
        if target == '--cloudflare':
            project_name = sys.argv[4] if len(sys.argv) > 4 else 'jameskilby-co-uk'
            success = deployer.deploy_to_cloudflare_pages(project_name)
        elif target == '--netlify':
            site_id = sys.argv[4] if len(sys.argv) > 4 else None
            success = deployer.deploy_to_netlify(site_id)
        elif target == '--s3':
            bucket_name = sys.argv[4]
            aws_profile = sys.argv[5] if len(sys.argv) > 5 else None
            success = deployer.deploy_to_aws_s3(bucket_name, aws_profile)
        elif target == '--rsync':
            remote = sys.argv[4]
            ssh_key = sys.argv[5] if len(sys.argv) > 5 else None
            success = deployer.deploy_via_rsync(remote.split(':')[0], remote.split(':')[1], ssh_key)
        elif target == '--git':
            target_dir = sys.argv[4] if len(sys.argv) > 4 else 'public'
            success = deployer.deploy_to_git_repo(target_dir)
        else:
            print(f"❌ Unknown deployment target: {target}")
            sys.exit(1)
        
        if not success:
            sys.exit(1)
    
    elif command == 'full':
        if len(sys.argv) < 4:
            print("Usage: python deploy_static_site.py full <output_dir> <target>")
            sys.exit(1)
        
        output_dir = sys.argv[2]
        
        # Generate
        generator = WordPressStaticGenerator(
            wp_url=WP_URL,
            auth_token=AUTH_TOKEN,
            output_dir=output_dir,
            target_domain=TARGET_DOMAIN
        )
        
        success = generator.generate_static_site()
        if not success:
            sys.exit(1)
        
        # Deploy
        deployer = StaticSiteDeployer(output_dir, TARGET_DOMAIN)
        target = sys.argv[3]
        
        if target == '--cloudflare':
            project_name = sys.argv[4] if len(sys.argv) > 4 else 'jameskilby-co-uk'
            success = deployer.deploy_to_cloudflare_pages(project_name)
        # ... (other deployment targets same as above)
        
        if not success:
            sys.exit(1)
    
    elif command == 'server':
        if len(sys.argv) < 3:
            print("Usage: python deploy_static_site.py server <output_dir> [port]")
            sys.exit(1)
        
        output_dir = sys.argv[2]
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
        
        deployer = StaticSiteDeployer(output_dir, TARGET_DOMAIN)
        deployer.start_local_server(port)
    
    elif command == 'setup-github':
        create_github_action_workflow()
    
    elif command == 'setup-cron':
        create_cron_script()
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()