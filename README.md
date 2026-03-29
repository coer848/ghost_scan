# 👻 ghost_scan — OSINT Username Scanner

> Busca la presencia de un username en múltiples plataformas simultáneamente.

![Python](https://img.shields.io/badge/Python-3.8+-cyan?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-gray?style=flat-square)
![OSINT](https://img.shields.io/badge/Category-OSINT-red?style=flat-square)

---

## ¿Qué hace?

`ghost_scan` toma un username y lanza peticiones HTTP en paralelo a +15 plataformas para detectar si existe una cuenta activa. Los resultados se muestran en tiempo real en la terminal.

```
  [+] GitHub         FOUND              [200]  https://github.com/objetivo
  [-] TikTok         NOT FOUND          [404]  https://www.tiktok.com/@objetivo
  [~] Instagram      TIMEOUT            [---]  https://www.instagram.com/objetivo/
```

---

## Plataformas incluidas

| Plataforma | Plataforma | Plataforma |
|------------|------------|------------|
| GitHub | Twitter/X | Instagram |
| TikTok | Reddit | Pinterest |
| Twitch | Steam | Spotify |
| DeviantArt | Keybase | HackerNews |
| GitLab | Replit | Pastebin |

---

## Instalación

```bash
# Clona el repo
git clone https://github.com/tu-usuario/ghost_scan.git
cd ghost_scan

# Instala la única dependencia
pip install requests
```

---

## Uso

```bash
# Búsqueda básica
python ghost_scan.py objetivo

# Con más hilos (más rápido)
python ghost_scan.py objetivo --threads 20

# Guardando reporte JSON
python ghost_scan.py objetivo --save

# Ajustar timeout por petición
python ghost_scan.py objetivo --timeout 5
```

---

## Opciones

| Flag | Descripción | Default |
|------|-------------|---------|
| `username` | Username a buscar (requerido) | — |
| `--threads` | Hilos concurrentes | 10 |
| `--timeout` | Segundos por petición | 8 |
| `--save` | Exportar resultados a JSON | false |

---

## Ejemplo de reporte JSON

```json
{
  "username": "objetivo",
  "scan_date": "2026-03-28T21:00:00",
  "total_checked": 15,
  "found": 4,
  "results": [
    {
      "platform": "GitHub",
      "url": "https://github.com/objetivo",
      "status": "found",
      "http_code": 200
    }
  ]
}
```

---

## ⚠️ Aviso legal

Esta herramienta es solo para uso educativo e investigación OSINT ética.  
No uses esta herramienta para acosar, stalkear, o dañar a terceros.  
El autor no se hace responsable del uso indebido.

---

## Autor

**Gabo** — Estudiante de Técnico en Programación de Software (SENA) y Redes (UNIMINUTO).  
Intereses: ciberseguridad, automatización, desarrollo de herramientas CLI.

---

*"Know your footprint before others do."*
