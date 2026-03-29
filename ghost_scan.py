#!/usr/bin/env python3
"""
ghost_scan.py — OSINT Username Scanner
Autor: Gabo | github.com/coer848
Descripción: Busca un username en múltiples plataformas y reporta su presencia.
"""

import requests
import json
import sys
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─── Paleta de colores ANSI ───────────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"
    MAGENTA = "\033[95m"

# ─── Plataformas a escanear ───────────────────────────────────────────────────
# Estructura: "NombrePlataforma": {"url": "URL con {}", "not_found": código HTTP o texto}
PLATFORMS = {
    "GitHub":       {"url": "https://github.com/{}",               "not_found_code": 404},
    "Twitter/X":    {"url": "https://x.com/{}",                    "not_found_code": 404},
    "Instagram":    {"url": "https://www.instagram.com/{}/",        "not_found_code": 404},
    "TikTok":       {"url": "https://www.tiktok.com/@{}",           "not_found_code": 404},
    "Reddit":       {"url": "https://www.reddit.com/user/{}",       "not_found_code": 404},
    "Pinterest":    {"url": "https://www.pinterest.com/{}/",        "not_found_code": 404},
    "Twitch":       {"url": "https://www.twitch.tv/{}",             "not_found_code": 404},
    "Steam":        {"url": "https://steamcommunity.com/id/{}",     "not_found_code": 404},
    "Spotify":      {"url": "https://open.spotify.com/user/{}",     "not_found_code": 404},
    "DeviantArt":   {"url": "https://www.deviantart.com/{}",        "not_found_code": 404},
    "Keybase":      {"url": "https://keybase.io/{}",                "not_found_code": 404},
    "HackerNews":   {"url": "https://news.ycombinator.com/user?id={}","not_found_code": 404},
    "GitLab":       {"url": "https://gitlab.com/{}",                "not_found_code": 404},
    "Replit":       {"url": "https://replit.com/@{}",               "not_found_code": 404},
    "Pastebin":     {"url": "https://pastebin.com/u/{}",            "not_found_code": 404},
}

BANNER = f"""
{C.CYAN}{C.BOLD}
  ██████  ██░ ██  ▒█████    ██████ ▄▄▄█████▓
▒██    ▒ ▓██░ ██▒▒██▒  ██▒▒██    ▒ ▓  ██▒ ▓▒
░ ▓██▄   ▒██▀▀██░▒██░  ██▒░ ▓██▄   ▒ ▓██░ ▒░
  ▒   ██▒░▓█ ░██ ▒██   ██░  ▒   ██▒░ ▓██▓ ░ 
▒██████▒▒░▓█▒░██▓░ ████▓▒░▒██████▒▒  ▒██▒ ░ 
▒ ▒▓▒ ▒ ░ ▒ ░░▒░▒░ ▒░▒░▒░ ▒ ▒▓▒ ▒ ░  ▒ ░░   
░ ░▒  ░ ░ ▒ ░▒░ ░  ░ ▒ ▒░ ░ ░▒  ░ ░    ░    
░  ░  ░   ░  ░░ ░░ ░ ░ ▒  ░  ░  ░    ░      
      ░   ░  ░  ░    ░ ░        ░            
{C.RESET}{C.GRAY}         OSINT Username Scanner v1.0{C.RESET}
"""

# ─── Función principal de chequeo ─────────────────────────────────────────────
def check_platform(platform_name: str, config: dict, username: str, timeout: int = 8) -> dict:
    """
    Intenta hacer una petición HTTP GET a la URL de la plataforma.
    Retorna un dict con el resultado para ese sitio.
    
    - platform_name: nombre del sitio (ej. "GitHub")
    - config: dict con "url" y "not_found_code"
    - username: el usuario a buscar
    - timeout: segundos antes de abandonar la petición
    """
    url = config["url"].format(username)   # Rellena {} con el username
    result = {
        "platform": platform_name,
        "url": url,
        "status": "unknown",
        "http_code": None
    }

    try:
        headers = {
            # Simulamos un navegador real para evitar bloqueos por User-Agent
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        result["http_code"] = response.status_code

        if response.status_code == config["not_found_code"]:
            result["status"] = "not_found"
        elif response.status_code == 200:
            result["status"] = "found"
        else:
            result["status"] = "uncertain"  # Respuesta inesperada (429, 403, etc.)

    except requests.exceptions.Timeout:
        result["status"] = "timeout"
    except requests.exceptions.ConnectionError:
        result["status"] = "error"
    except Exception as e:
        result["status"] = "error"
        result["detail"] = str(e)

    return result

# ─── Impresión de resultados ───────────────────────────────────────────────────
def print_result(result: dict):
    """Imprime una línea formateada por resultado."""
    status = result["status"]
    platform = result["platform"]
    url = result["url"]
    code = result["http_code"] or "---"

    if status == "found":
        icon = f"{C.GREEN}[+]{C.RESET}"
        label = f"{C.GREEN}FOUND{C.RESET}"
        url_text = f"{C.CYAN}{url}{C.RESET}"
    elif status == "not_found":
        icon = f"{C.GRAY}[-]{C.RESET}"
        label = f"{C.GRAY}NOT FOUND{C.RESET}"
        url_text = f"{C.GRAY}{url}{C.RESET}"
    elif status == "timeout":
        icon = f"{C.YELLOW}[~]{C.RESET}"
        label = f"{C.YELLOW}TIMEOUT{C.RESET}"
        url_text = f"{C.GRAY}{url}{C.RESET}"
    else:
        icon = f"{C.RED}[!]{C.RESET}"
        label = f"{C.RED}ERROR{C.RESET}"
        url_text = f"{C.GRAY}{url}{C.RESET}"

    print(f"  {icon} {C.WHITE}{platform:<14}{C.RESET} {label:<22} {C.GRAY}[{code}]{C.RESET}  {url_text}")

# ─── Guardado de reporte ───────────────────────────────────────────────────────
def save_report(username: str, results: list):
    """Guarda los resultados en un archivo JSON con timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{username}_{timestamp}.json"
    report = {
        "username": username,
        "scan_date": datetime.now().isoformat(),
        "total_checked": len(results),
        "found": sum(1 for r in results if r["status"] == "found"),
        "results": results
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    return filename

# ─── Entry point ──────────────────────────────────────────────────────────────
def main():
    print(BANNER)

    # Argumentos de línea de comandos
    parser = argparse.ArgumentParser(
        description="OSINT Username Scanner — busca un username en múltiples plataformas",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("username", help="El username a buscar (ej: itz.gabx00)")
    parser.add_argument("--threads", type=int, default=10,
                        help="Hilos concurrentes (default: 10)")
    parser.add_argument("--timeout", type=int, default=8,
                        help="Timeout por petición en segundos (default: 8)")
    parser.add_argument("--save", action="store_true",
                        help="Guardar resultados en un archivo JSON")
    args = parser.parse_args()

    username = args.username.strip()
    print(f"  {C.BOLD}{C.WHITE}Target   :{C.RESET} {C.MAGENTA}{username}{C.RESET}")
    print(f"  {C.BOLD}{C.WHITE}Platforms:{C.RESET} {len(PLATFORMS)}")
    print(f"  {C.BOLD}{C.WHITE}Threads  :{C.RESET} {args.threads}")
    print(f"\n  {C.GRAY}{'─' * 60}{C.RESET}\n")

    results = []
    found_count = 0

    # ThreadPoolExecutor permite hacer múltiples peticiones al mismo tiempo
    # En vez de esperar una por una (lo que sería muy lento), las lanza en paralelo
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {
            executor.submit(check_platform, name, cfg, username, args.timeout): name
            for name, cfg in PLATFORMS.items()
        }

        # as_completed() nos da cada resultado en cuanto termina (no en orden)
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print_result(result)
            if result["status"] == "found":
                found_count += 1

    # ─── Resumen final ────────────────────────────────────────────────────────
    print(f"\n  {C.GRAY}{'─' * 60}{C.RESET}")
    print(f"\n  {C.BOLD}Resumen:{C.RESET}")
    print(f"  {C.GREEN}[+] Encontrado en: {found_count} plataforma(s){C.RESET}")
    print(f"  {C.GRAY}[-] No encontrado: {sum(1 for r in results if r['status'] == 'not_found')}{C.RESET}")
    print(f"  {C.YELLOW}[~] Errores/Timeout: {sum(1 for r in results if r['status'] in ['timeout','error','uncertain'])}{C.RESET}")

    if args.save:
        filename = save_report(username, results)
        print(f"\n  {C.CYAN}[*] Reporte guardado en: {filename}{C.RESET}")

    print()

if __name__ == "__main__":
    main()
