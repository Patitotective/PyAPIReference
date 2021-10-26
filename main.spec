# -*- mode: python ; coding: utf-8 -*-
import platform

block_cipher = None

with open('requirements.txt') as f:
    hiddenimports = f.read().splitlines()

a = Analysis(['main.py'],
             pathex=['./pyapireference'], 
             binaries=[],
             datas=[('assets/img/icon.ico', 'img'), ('pyapireference/ui/theme.prefs', 'pyapireference/ui')], 
             hiddenimports=hiddenimports,
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='PyAPIReference', # if platform.system() != 'Linux' else 'PyAPIReference.bin',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None, 
          icon='img/icon.ico' # Windows
        )
