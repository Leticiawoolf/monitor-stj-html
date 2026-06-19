import requests
import socket

print("=== Teste de DNS ===")
try:
    ip = socket.gethostbyname("api-publica.datajud.cnj.jus.br")
    print(f"IP resolvido: {ip}")
except Exception as e:
    print(f"Erro de DNS: {e}")

print("\n=== Teste de conexão simples (GET) ===")
try:
    resp = requests.get("https://api-publica.datajud.cnj.jus.br", timeout=15)
    print(f"Status: {resp.status_code}")
except Exception as e:
    print(f"Erro: {type(e).__name__}: {e}")

print("\n=== Teste de IP público do runner ===")
try:
    resp = requests.get("https://api.ipify.org?format=json", timeout=10)
    print(f"IP do runner: {resp.json()}")
except Exception as e:
    print(f"Erro: {e}")
