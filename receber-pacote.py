#!/usr/bin/env python3
"""Recebe o pacote House TV privado. Apenas decifra; não instala/publica APK."""
from pathlib import Path
import getpass
import hashlib
import hmac
import json
import os
import subprocess
import tempfile
import sys

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'transfer.json').read_text())
password = os.environ.get('HOUSE_TV_TRANSFER_PASSWORD') or getpass.getpass('Senha de transferência fornecida no chat: ')
key = hashlib.pbkdf2_hmac('sha256', b'HouseTV-transfer-MAC\0' + password.encode(), bytes.fromhex(manifest['mac_salt']), 200000)
mac = hmac.new(key, digestmod=hashlib.sha256)
output = root / manifest['output']
if output.exists():
    sys.exit('O pacote já existe; preservado: ' + str(output))
with tempfile.TemporaryDirectory(prefix='.house-tv-transfer-', dir=root) as work:
    encrypted = Path(work) / 'payload.enc'
    with encrypted.open('wb') as target:
        for part in manifest['parts']:
            digest = hashlib.sha256()
            size = 0
            with (root / part['name']).open('rb') as source:
                while True:
                    data = source.read(1024 * 1024)
                    if not data:
                        break
                    target.write(data)
                    digest.update(data)
                    mac.update(data)
                    size += len(data)
            if size != part['bytes'] or digest.hexdigest() != part['sha256']:
                sys.exit('Parte incompleta ou alterada: ' + part['name'])
    if not hmac.compare_digest(mac.hexdigest(), manifest['mac_sha256']):
        sys.exit('Senha incorreta ou pacote alterado. Nenhum conteúdo foi extraído.')
    help_result = subprocess.run(['openssl', 'enc', '-help'], capture_output=True, text=True)
    salt_option = ['-saltlen', '8'] if '-saltlen' in help_result.stdout + help_result.stderr else []
    clear = Path(work) / 'package.tar.gz'
    result = subprocess.run(['openssl', 'enc', '-d', '-aes-256-cbc', '-pbkdf2', '-iter', '200000', '-md', 'sha256',
                             *salt_option, '-in', str(encrypted), '-out', str(clear), '-pass', 'stdin'],
                            input=(password + '\n').encode(), capture_output=True)
    if result.returncode:
        sys.exit('Falha de decodificação OpenSSL; arquivo de saída não foi publicado.')
    digest = hashlib.sha256()
    with clear.open('rb') as source:
        for data in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(data)
    if digest.hexdigest() != manifest['output_sha256']:
        sys.exit('SHA-256 do pacote decifrado incorreto.')
    os.replace(clear, output)
print('Pacote íntegro recuperado: ' + str(output))
print('Nenhum APK foi instalado, assinado ou publicado.')
