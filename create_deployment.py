#!/usr/bin/env python3
"""
Create deployment package for cloud hosting.
Packages all necessary files into a zip for easy upload.
"""
import zipfile
import os

# Files needed for deployment
REQUIRED_FILES = [
    'main.py',
    'config.yaml',
    'state.txt',
    'state_btc.txt',
    'price_fetcher.py',
    'decision_engine.py',
    'notifier_telegram.py',
    'utils.py',
    'state_updater.py',
    'trade_logger.py',
    'historical_analyzer.py',
    'pattern_analyzer.py',
    'trailing_stop_manager.py',
    'signal_state_tracker.py',
    'confidence_levels.py',
    'requirements.txt',
]

def create_deployment_package():
    """Create zip file with all required files"""
    
    package_name = 'crypto_notifier_deploy.zip'
    
    print(f"\n📦 Creating deployment package...\n")
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in REQUIRED_FILES:
            if os.path.exists(file):
                zipf.write(file)
                print(f"✅ Added: {file}")
            else:
                print(f"⚠️ Missing: {file}")
    
    file_size = os.path.getsize(package_name) / 1024  # KB
    
    print(f"\n{'='*60}")
    print(f"✅ Package created: {package_name}")
    print(f"📊 Size: {file_size:.2f} KB")
    print(f"{'='*60}\n")
    
    print("📤 Next Steps:")
    print("1. Go to https://www.pythonanywhere.com")
    print("2. Sign up for free account")
    print("3. Go to Files tab")
    print(f"4. Upload {package_name}")
    print("5. Extract in console: unzip crypto_notifier_deploy.zip")
    print("6. Install requirements: pip3.9 install --user -r requirements.txt")
    print("7. Test: python3.9 main.py state.txt")
    print("8. Schedule in Tasks tab\n")

if __name__ == "__main__":
    create_deployment_package()
