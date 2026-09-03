import urllib.request
import json
import os
import struct
import zlib

# Step 1: Login
login_data = json.dumps({"correo": "admin@sistema-sst.com", "password": "SuperAdmin2026*"}).encode('utf-8')
req = urllib.request.Request(
    'http://localhost:8000/auth/login-json',
    data=login_data,
    headers={'Content-Type': 'application/json'}
)
try:
    r = urllib.request.urlopen(req)
    auth = json.loads(r.read())
    token = auth.get('access_token', '')
    print(f'Login OK')
except Exception as e:
    print(f'Login error: {e}')
    exit(1)

headers = {'Authorization': f'Bearer {token}'}

# Step 2: Try to find any evidence endpoint that works
endpoints_to_try = [
    ('CAPA', '/capa/?page=1&page_size=1', 'items'),
    ('INSPECCIONES', '/inspecciones/?page=1&page_size=1', 'items'),
    ('INCIDENTES', '/incidentes/?page=1&page_size=1', 'items'),
    ('EPP', '/epp/entregas/?page=1&page_size=1', 'items'),
]

found_module = None
found_id = None

for module, endpoint, key in endpoints_to_try:
    try:
        req2 = urllib.request.Request(f'http://localhost:8000{endpoint}', headers=headers)
        r2 = urllib.request.urlopen(req2)
        data = json.loads(r2.read())
        items = data.get(key, data) if isinstance(data, dict) else data
        if items and len(items) > 0:
            found_module = module
            found_id = items[0]['id']
            print(f'Found {module} ID: {found_id}')
            break
    except Exception as e:
        print(f'{module}: {e}')

if not found_module:
    print('No modules with data found')
    exit(1)

# Step 3: Create a test image
def create_test_png():
    header = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
    ihdr_crc = b'\x00' * 4
    ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + ihdr_crc
    raw_data = b'\x00\xff\x00\x00'
    compressed = zlib.compress(raw_data)
    idat_crc = b'\x00' * 4
    idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + idat_crc
    iend_crc = b'\x00' * 4
    iend = struct.pack('>I', 0) + b'IEND' + iend_crc
    return header + ihdr + idat + iend

test_png = create_test_png()

# Step 4: Upload based on module
upload_endpoints = {
    'CAPA': f'/capa/{found_id}/evidencias',
    'INSPECCIONES': f'/inspecciones/{found_id}/evidencias',
    'INCIDENTES': f'/incidentes/{found_id}/evidencias',
    'EPP': f'/epp/entregas/{found_id}/evidencias',
}

upload_url = upload_endpoints[found_module]
print(f'Uploading to: {upload_url}')

boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="tipo_evidencia"\r\n\r\n'
    f'EVIDENCIA_TEST\r\n'
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="descripcion"\r\n\r\n'
    f'Test upload\r\n'
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="archivo"; filename="test.png"\r\n'
    f'Content-Type: image/png\r\n\r\n'
).encode('utf-8') + test_png + f'\r\n--{boundary}--\r\n'.encode('utf-8')

req3 = urllib.request.Request(
    f'http://localhost:8000{upload_url}',
    data=body,
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': f'multipart/form-data; boundary={boundary}'
    },
    method='POST'
)
try:
    r3 = urllib.request.urlopen(req3)
    result = json.loads(r3.read())
    print(f'\nUpload result:')
    print(json.dumps(result, indent=2))
    
    # Step 5: Try to access the uploaded file URL
    if 'url' in result:
        file_url = result['url']
        print(f'\nFile URL from response: {file_url}')
        
        # Convert to protected URL
        if file_url.startswith('/uploads/'):
            relative = file_url[9:]  # Remove '/uploads/'
            protected_url = f'http://localhost:8000/archivos-protegidos/{relative}'
        else:
            protected_url = f'http://localhost:8000{file_url}'
        print(f'Protected URL: {protected_url}')
        
        req4 = urllib.request.Request(protected_url, headers=headers)
        try:
            r4 = urllib.request.urlopen(req4)
            content = r4.read()
            print(f'File access: {r4.status} OK, size: {len(content)} bytes')
        except urllib.error.HTTPError as e:
            body_err = e.read().decode('utf-8', errors='replace')
            print(f'File access ERROR: {e.code} - {body_err}')
        
        # Also check the file on disk
        from pathlib import Path
        disk_path = Path('C:/Proyectos/sistema_gestion_sst/backend/app/uploads') / relative
        print(f'\nDisk path: {disk_path}')
        print(f'Exists on disk: {disk_path.exists()}')
        if disk_path.exists():
            print(f'Size on disk: {disk_path.stat().st_size} bytes')
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='replace')
    print(f'Upload HTTP error: {e.code} - {body}')
except Exception as e:
    print(f'Upload error: {e}')
