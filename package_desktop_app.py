#!/usr/bin/env python3
"""
Desktop App Packaging Script
Creates distributable packages for Windows, macOS, and Linux
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
import zipfile
import tarfile
import json

class DesktopAppPackager:
    """Package the desktop app for distribution"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.desktop_app_dir = self.project_root / "desktop_app"
        
        # App metadata
        self.app_name = "AI-IDS"
        self.app_version = "1.0.0"
        self.app_description = "AI-powered Intrusion Detection System"
        self.app_author = "AI-IDS Team"
        
    def clean_build(self):
        """Clean previous build artifacts"""
        print("🧹 Cleaning previous builds...")
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
    
    def install_packaging_dependencies(self):
        """Install required packaging dependencies"""
        print("📦 Installing packaging dependencies...")
        
        # Install PyInstaller for executable creation
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        
        # Install additional packaging tools based on platform
        if platform.system() == "Windows":
            subprocess.run([sys.executable, "-m", "pip", "install", "pywin32"], check=True)
        elif platform.system() == "Darwin":
            subprocess.run([sys.executable, "-m", "pip", "install", "py2app"], check=True)
        
        print("✅ Packaging dependencies installed")
    
    def create_pyinstaller_spec(self):
        """Create PyInstaller spec file"""
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{self.desktop_app_dir / "ids_desktop_app.py"}'],
    pathex=['{self.project_root}'],
    binaries=[],
    datas=[
        ('{self.project_root / "src"}', 'src'),
        ('{self.project_root / "models"}', 'models'),
        ('{self.project_root / "data"}', 'data'),
        ('{self.project_root / "requirements.txt"}', '.'),
    ],
    hiddenimports=[
        'sklearn',
        'pandas',
        'numpy',
        'joblib',
        'scapy',
        'flask',
        'threading',
        'tkinter',
        'pystray',
        'PIL',
        'winreg',  # For Windows registry access
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{self.app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{self.create_app_icon()}',
)
'''
        
        spec_file = self.build_dir / "ai_ids.spec"
        spec_file.write_text(spec_content)
        return spec_file
    
    def create_app_icon(self):
        """Create application icon"""
        # Create a simple icon using PIL
        try:
            from PIL import Image, ImageDraw
            
            # Create 256x256 icon
            icon = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
            draw = ImageDraw.Draw(icon)
            
            # Draw shield shape
            shield_color = (52, 152, 219)  # Blue
            points = [
                (128, 20),   # Top
                (220, 60),   # Top right
                (220, 160),  # Bottom right
                (128, 240),  # Bottom center
                (36, 160),   # Bottom left
                (36, 60),    # Top left
            ]
            draw.polygon(points, fill=shield_color)
            
            # Draw "AI" text
            try:
                from PIL import ImageFont
                # Try to use a nice font
                font = ImageFont.truetype("arial.ttf", 80)
            except:
                font = ImageFont.load_default()
            
            # Draw AI text
            text = "AI"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (256 - text_width) // 2
            y = (256 - text_height) // 2 - 10
            
            draw.text((x, y), text, fill='white', font=font)
            
            # Save icon
            icon_path = self.build_dir / "app_icon.png"
            icon.save(icon_path)
            
            # Convert to ICO for Windows
            if platform.system() == "Windows":
                ico_path = self.build_dir / "app_icon.ico"
                icon.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
                return str(ico_path)
            
            return str(icon_path)
            
        except ImportError:
            print("⚠️ PIL not available, creating simple icon")
            # Create empty icon file
            icon_path = self.build_dir / "app_icon.png"
            icon_path.touch()
            return str(icon_path)
    
    def build_executable(self):
        """Build executable using PyInstaller"""
        print("🔨 Building executable...")
        
        spec_file = self.create_pyinstaller_spec()
        
        # Run PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--workpath", str(self.build_dir / "work"),
            "--distpath", str(self.build_dir / "dist"),
            str(spec_file)
        ]
        
        subprocess.run(cmd, check=True, cwd=self.project_root)
        print("✅ Executable built successfully")
    
    def create_windows_installer(self):
        """Create Windows installer"""
        if platform.system() != "Windows":
            print("⚠️ Windows installer can only be created on Windows")
            return
        
        print("🪟 Creating Windows installer...")
        
        # Create NSIS installer script
        nsis_script = f'''
!define APPNAME "{self.app_name}"
!define COMPANYNAME "{self.app_author}"
!define DESCRIPTION "{self.app_description}"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0

RequestExecutionLevel admin

InstallDir "$PROGRAMFILES\\${{APPNAME}}"

Name "${{APPNAME}}"
Icon "app_icon.ico"
outFile "..\\..\\dist\\${{APPNAME}}-Setup.exe"

page directory
page instfiles

section "install"
    setOutPath $INSTDIR
    file /r "dist\\${{APPNAME}}\\*"
    
    # Create uninstaller
    writeUninstaller "$INSTDIR\\uninstall.exe"
    
    # Create start menu shortcuts
    createDirectory "$SMPROGRAMS\\${{APPNAME}}"
    createShortCut "$SMPROGRAMS\\${{APPNAME}}\\${{APPNAME}}.lnk" "$INSTDIR\\${{APPNAME}}.exe"
    createShortCut "$SMPROGRAMS\\${{APPNAME}}\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
    
    # Create desktop shortcut
    createShortCut "$DESKTOP\\${{APPNAME}}.lnk" "$INSTDIR\\${{APPNAME}}.exe"
    
    # Registry entries for Add/Remove Programs
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayName" "${{APPNAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "UninstallString" "$INSTDIR\\uninstall.exe"
sectionEnd

section "uninstall"
    delete "$INSTDIR\\*.*"
    rmDir /r "$INSTDIR"
    
    delete "$SMPROGRAMS\\${{APPNAME}}\\*.*"
    rmDir "$SMPROGRAMS\\${{APPNAME}}"
    delete "$DESKTOP\\${{APPNAME}}.lnk"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}"
sectionEnd
'''
        
        nsis_file = self.build_dir / "installer.nsi"
        nsis_file.write_text(nsis_script)
        
        # Try to compile with NSIS (if available)
        try:
            subprocess.run(["makensis", str(nsis_file)], check=True, cwd=self.build_dir)
            print("✅ Windows installer created")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ NSIS not found. Creating ZIP package instead...")
            self.create_zip_package("windows")
    
    def create_macos_app(self):
        """Create macOS .app bundle"""
        if platform.system() != "Darwin":
            print("⚠️ macOS app can only be created on macOS")
            return
        
        print("🍎 Creating macOS app bundle...")
        
        app_name = f"{self.app_name}.app"
        app_dir = self.dist_dir / app_name
        
        # Create app bundle structure
        contents_dir = app_dir / "Contents"
        macos_dir = contents_dir / "MacOS"
        resources_dir = contents_dir / "Resources"
        
        contents_dir.mkdir(parents=True, exist_ok=True)
        macos_dir.mkdir(exist_ok=True)
        resources_dir.mkdir(exist_ok=True)
        
        # Copy executable
        executable_src = self.build_dir / "dist" / self.app_name / self.app_name
        executable_dst = macos_dir / self.app_name
        shutil.copy2(executable_src, executable_dst)
        executable_dst.chmod(0o755)
        
        # Create Info.plist
        info_plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{self.app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.ai-ids.desktop</string>
    <key>CFBundleName</key>
    <string>{self.app_name}</string>
    <key>CFBundleVersion</key>
    <string>{self.app_version}</string>
    <key>CFBundleShortVersionString</key>
    <string>{self.app_version}</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.12</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>'''
        
        (contents_dir / "Info.plist").write_text(info_plist)
        
        # Create DMG
        dmg_path = self.dist_dir / f"{self.app_name}-{self.app_version}.dmg"
        subprocess.run([
            "hdiutil", "create", "-volname", self.app_name,
            "-srcfolder", str(app_dir),
            "-ov", "-format", "UDZO",
            str(dmg_path)
        ], check=True)
        
        print("✅ macOS DMG created")
    
    def create_linux_package(self):
        """Create Linux package"""
        if platform.system() != "Linux":
            print("⚠️ Linux package optimized for Linux systems")
        
        print("🐧 Creating Linux package...")
        
        # Create AppImage structure
        appdir = self.build_dir / f"{self.app_name}.AppDir"
        appdir.mkdir(exist_ok=True)
        
        # Copy executable and resources
        executable_src = self.build_dir / "dist" / self.app_name
        shutil.copytree(executable_src, appdir / "usr" / "bin", dirs_exist_ok=True)
        
        # Create desktop file
        desktop_content = f'''[Desktop Entry]
Type=Application
Name={self.app_name}
Exec={self.app_name}
Icon={self.app_name.lower()}
Comment={self.app_description}
Categories=Security;Network;
'''
        
        (appdir / f"{self.app_name}.desktop").write_text(desktop_content)
        
        # Copy icon
        icon_src = self.build_dir / "app_icon.png"
        if icon_src.exists():
            shutil.copy2(icon_src, appdir / f"{self.app_name.lower()}.png")
        
        # Create tar.gz package
        tar_path = self.dist_dir / f"{self.app_name}-{self.app_version}-linux.tar.gz"
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(appdir, arcname=f"{self.app_name}-{self.app_version}")
        
        print("✅ Linux package created")
    
    def create_zip_package(self, platform_name):
        """Create simple ZIP package"""
        print(f"📦 Creating ZIP package for {platform_name}...")
        
        zip_path = self.dist_dir / f"{self.app_name}-{self.app_version}-{platform_name}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add executable
            exe_dir = self.build_dir / "dist" / self.app_name
            for file_path in exe_dir.rglob("*"):
                if file_path.is_file():
                    arcname = f"{self.app_name}-{self.app_version}" / file_path.relative_to(exe_dir)
                    zipf.write(file_path, arcname)
            
            # Add README
            readme_content = f"""# {self.app_name} v{self.app_version}

## Installation Instructions

### Windows
1. Extract the ZIP file
2. Run {self.app_name}.exe
3. Grant administrator permissions when prompted
4. The app will start minimized in the system tray

### macOS
1. Extract the ZIP file
2. Run {self.app_name}
3. Allow the app in Security & Privacy settings if prompted
4. The app will start minimized in the menu bar

### Linux
1. Extract the ZIP file
2. Make the executable: chmod +x {self.app_name}
3. Run: ./{self.app_name}
4. The app will start minimized in the system tray

## Features
- Real-time network monitoring
- AI-powered threat detection
- Web dashboard interface
- System tray integration
- Auto-start with system
- Cross-platform compatibility

## Usage
- Right-click the system tray icon to access controls
- Open the dashboard to view real-time statistics
- Configure settings through the GUI
- Enable auto-start to run at system startup

## Support
For support and documentation, visit: http://localhost:8000
"""
            
            zipf.writestr(f"{self.app_name}-{self.app_version}/README.txt", readme_content)
        
        print(f"✅ ZIP package created: {zip_path}")
    
    def create_installer_script(self):
        """Create cross-platform installer script"""
        installer_content = '''#!/usr/bin/env python3
"""
AI-IDS Desktop App Installer
Cross-platform installer for the AI Intrusion Detection System
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def install_dependencies():
    """Install required Python dependencies"""
    print("📦 Installing dependencies...")
    
    requirements = [
        "scikit-learn>=1.0.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "joblib>=1.1.0",
        "scapy>=2.4.0",
        "flask>=2.0.0",
        "pystray>=0.17.0",
        "Pillow>=8.0.0",
    ]
    
    # Add platform-specific requirements
    if platform.system() == "Windows":
        requirements.append("pywin32>=227")
    
    for req in requirements:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", req], 
                         check=True, capture_output=True)
            print(f"✅ Installed {req}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {req}: {e}")
            return False
    
    return True

def setup_application():
    """Setup application files and configuration"""
    print("🔧 Setting up application...")
    
    # Create application directory
    if platform.system() == "Windows":
        app_dir = Path.home() / "AppData/Local/AI-IDS"
    elif platform.system() == "Darwin":
        app_dir = Path.home() / "Library/Application Support/AI-IDS"
    else:
        app_dir = Path.home() / ".local/share/ai-ids"
    
    app_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy application files
    src_dir = Path(__file__).parent
    for item in src_dir.iterdir():
        if item.name not in ["installer.py", "__pycache__"]:
            if item.is_dir():
                shutil.copytree(item, app_dir / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, app_dir)
    
    print(f"✅ Application installed to: {app_dir}")
    return app_dir

def create_shortcuts(app_dir):
    """Create desktop and start menu shortcuts"""
    print("🔗 Creating shortcuts...")
    
    if platform.system() == "Windows":
        # Create Windows shortcuts using PowerShell
        desktop_shortcut = Path.home() / "Desktop/AI-IDS.lnk"
        ps_command = f'''
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut("{desktop_shortcut}")
$Shortcut.TargetPath = "{sys.executable}"
$Shortcut.Arguments = "\\"{app_dir / 'ids_desktop_app.py'}\\""
$Shortcut.WorkingDirectory = "{app_dir}"
$Shortcut.IconLocation = "{app_dir / 'app_icon.ico'}"
$Shortcut.Save()
'''
        subprocess.run(["powershell", "-Command", ps_command], capture_output=True)
        
    elif platform.system() == "Darwin":
        # Create macOS application alias
        app_script = f'''#!/bin/bash
cd "{app_dir}"
"{sys.executable}" ids_desktop_app.py
'''
        app_file = Path.home() / "Desktop/AI-IDS"
        app_file.write_text(app_script)
        app_file.chmod(0o755)
        
    else:
        # Create Linux desktop file
        desktop_content = f'''[Desktop Entry]
Type=Application
Name=AI Intrusion Detection System
Exec={sys.executable} {app_dir}/ids_desktop_app.py
Icon={app_dir}/app_icon.png
Comment=AI-powered network intrusion detection
Categories=Security;Network;
StartupNotify=true
'''
        desktop_file = Path.home() / "Desktop/AI-IDS.desktop"
        desktop_file.write_text(desktop_content)
        desktop_file.chmod(0o755)
    
    print("✅ Shortcuts created")

def main():
    """Main installer function"""
    print("🛡️ AI-IDS Desktop App Installer")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        sys.exit(1)
    
    try:
        # Install dependencies
        if not install_dependencies():
            print("❌ Failed to install dependencies")
            sys.exit(1)
        
        # Setup application
        app_dir = setup_application()
        
        # Create shortcuts
        create_shortcuts(app_dir)
        
        print("\\n🎉 Installation completed successfully!")
        print(f"Application installed to: {app_dir}")
        print("\\nTo start the application:")
        print("- Use the desktop shortcut")
        print("- Or run: python ids_desktop_app.py")
        print("\\nThe app will run in the system tray.")
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
        
        installer_path = self.dist_dir / "install.py"
        installer_path.write_text(installer_content)
        installer_path.chmod(0o755)
        
        print("✅ Installer script created")
    
    def package_all_platforms(self):
        """Package for all platforms"""
        print("🚀 Starting cross-platform packaging...")
        
        # Clean and prepare
        self.clean_build()
        
        # Install dependencies
        self.install_packaging_dependencies()
        
        # Build executable
        self.build_executable()
        
        # Create platform-specific packages
        current_platform = platform.system()
        
        if current_platform == "Windows":
            self.create_windows_installer()
        elif current_platform == "Darwin":
            self.create_macos_app()
        elif current_platform == "Linux":
            self.create_linux_package()
        
        # Always create ZIP package as fallback
        self.create_zip_package(current_platform.lower())
        
        # Create installer script
        self.create_installer_script()
        
        print("\\n🎉 Packaging completed!")
        print(f"Packages created in: {self.dist_dir}")
        print("\\nAvailable packages:")
        for package in self.dist_dir.iterdir():
            print(f"  📦 {package.name}")

def main():
    """Main entry point"""
    packager = DesktopAppPackager()
    packager.package_all_platforms()

if __name__ == "__main__":
    main()
