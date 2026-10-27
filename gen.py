#!/usr/bin/env python3
"""Perfil estilo panel NOC / status page. Uso: python3 gen.py <dir_salida>"""
import sys, os
from xml.sax.saxutils import escape as esc

OUT = sys.argv[1] if len(sys.argv) > 1 else "assets"
os.makedirs(OUT, exist_ok=True)

BG, CARD, EDGE = "#0d1326", "#141b35", "#243056"
TEXT, MUTED = "#e8ecff", "#8f9bc4"
OK, INFO, WARN, VIO, PINK = "#34d399", "#38bdf8", "#fbbf24", "#a78bfa", "#f472b6"
FONT = "'Segoe UI','Helvetica Neue',Arial,'DejaVu Sans',sans-serif"
MONO = "'DejaVu Sans Mono','Courier New',monospace"


def svg(name, w, h, body, title, desc, defs=""):
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
         f'aria-labelledby="t d" font-family="{FONT}"><title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>'
         f'<defs>{defs}</defs><rect width="{w}" height="{h}" rx="18" fill="{BG}"/>{body}</svg>')
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(s)


def card(x, y, w, h, accent=None):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{CARD}" stroke="{EDGE}" stroke-width="1.5"/>'
    if accent:
        s += f'<rect x="{x}" y="{y+14}" width="4" height="{h-28}" rx="2" fill="{accent}"/>'
    return s


def pulse(cx, cy, c=OK, r=6):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{c}" stroke-width="2">'
            f'<animate attributeName="r" values="{r};{r*3}" dur="2s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values=".8;0" dur="2s" repeatCount="indefinite"/></circle>')


# ---------------------------------------------------------------- HEADER / STATUS
def header():
    w, h = 1200, 300
    d = (f'<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{INFO}"/><stop offset="1" stop-color="{VIO}"/></linearGradient>'
         f'<linearGradient id="bgl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#101a3a"/><stop offset="1" stop-color="#1b1546"/></linearGradient>')
    b = f'<rect width="{w}" height="{h}" rx="18" fill="url(#bgl)"/>'
    # rejilla de red decorativa
    for i in range(0, 1200, 60):
        b += f'<line x1="{i}" y1="0" x2="{i}" y2="{h}" stroke="{EDGE}" stroke-opacity=".35"/>'
    for j in range(0, 300, 60):
        b += f'<line x1="0" y1="{j}" x2="{w}" y2="{j}" stroke="{EDGE}" stroke-opacity=".35"/>'
    b += f'<text x="60" y="120" font-size="64" font-weight="800" fill="{TEXT}">CarlosNuBa</text>'
    b += f'<text x="62" y="170" font-size="26" fill="url(#g)" font-weight="600">Técnico de Sistemas</text>'
    b += f'<text x="62" y="208" font-size="19" fill="{MUTED}">Infraestructura híbrida · Redes · Seguridad · Automatización</text>'
    # píldora de estado
    b += f'<rect x="60" y="236" width="360" height="40" rx="20" fill="{OK}" fill-opacity=".14" stroke="{OK}" stroke-opacity=".6"/>'
    b += pulse(86, 256) + f'<text x="106" y="262" font-size="16" font-weight="700" fill="{OK}" letter-spacing="1">ALL SYSTEMS OPERATIONAL</text>'
    # nodos animados a la derecha
    nodes = [(820, 90), (960, 150), (1090, 80), (900, 230), (1060, 220)]
    links = [(0, 1), (1, 2), (1, 3), (1, 4), (3, 4)]
    for a, c in links:
        b += f'<line x1="{nodes[a][0]}" y1="{nodes[a][1]}" x2="{nodes[c][0]}" y2="{nodes[c][1]}" stroke="{INFO}" stroke-opacity=".5" stroke-width="2"/>'
    for k, (a, c) in enumerate(links):
        x1, y1 = nodes[a]; x2, y2 = nodes[c]
        b += (f'<circle r="4" fill="{WARN}"><animate attributeName="cx" values="{x1};{x2}" dur="{2+k*.4:.1f}s" repeatCount="indefinite"/>'
              f'<animate attributeName="cy" values="{y1};{y2}" dur="{2+k*.4:.1f}s" repeatCount="indefinite"/></circle>')
    cols = [INFO, VIO, OK, PINK, WARN]
    for (x, y), c in zip(nodes, cols):
        b += f'<circle cx="{x}" cy="{y}" r="16" fill="{BG}" stroke="{c}" stroke-width="3"/><circle cx="{x}" cy="{y}" r="6" fill="{c}"/>'
    svg("header-v2.svg", w, h, b, "CarlosNuBa, Técnico de Sistemas",
        "Cabecera estilo panel de estado: CarlosNuBa, Técnico de Sistemas. Infraestructura híbrida, redes, seguridad y automatización. Indicador ALL SYSTEMS OPERATIONAL y una red de nodos con paquetes animados.", d)


# ---------------------------------------------------------------- KPIs (cualitativos)
def status_cards():
    w, h = 1200, 150
    items = [("Backups", "Verificados", OK), ("Cambios", "Con rollback", INFO), ("Accesos", "Por clave, nominales", VIO), ("Documentación", "Al día", WARN)]
    b = ""
    cw = 277
    for i, (k, v, c) in enumerate(items):
        x = 10 + i * (cw + 20)
        b += card(x, 15, cw, 120, c)
        b += f'<text x="{x+28}" y="55" font-size="15" fill="{MUTED}" letter-spacing="1.5">{k.upper()}</text>'
        b += f'<text x="{x+28}" y="98" font-size="24" font-weight="700" fill="{TEXT}">{esc(v)}</text>'
        b += pulse(x + cw - 30, 40, c, 5)
        b += f'<rect x="{x+28}" y="112" width="{cw-56}" height="5" rx="2.5" fill="{EDGE}"/>'
        b += (f'<rect x="{x+28}" y="112" width="0" height="5" rx="2.5" fill="{c}">'
              f'<animate attributeName="width" from="0" to="{cw-56}" dur="1.4s" begin="{i*.3:.1f}s" fill="freeze"/></rect>')
    svg("status.svg", w, h, b, "Estado de buenas prácticas",
        "Cuatro tarjetas de estado: backups verificados, cambios con rollback, accesos por clave y nominales, documentación al día.")


# ---------------------------------------------------------------- TOPOLOGÍA
def topology():
    w, h = 1200, 380
    b = f'<text x="40" y="52" font-size="22" font-weight="700" fill="{TEXT}">Topología de trabajo</text>'
    b += f'<text x="40" y="78" font-size="15" fill="{MUTED}">Cómo suelo organizar un entorno: borde, segmentos, cómputo, copias y vigilancia.</text>'
    N = {  # id: (x, y, label, color)
        "usr": (110, 230, "Usuarios", INFO),
        "edge": (330, 230, "Borde · Proxy", VIO),
        "vlan": (550, 140, "VLANs", OK),
        "dc": (550, 320, "AD · DNS", PINK),
        "pve": (800, 140, "Proxmox", WARN),
        "pbs": (1040, 140, "Backups", OK),
        "soc": (800, 320, "SOC · Wazuh", INFO),
    }
    L = [("usr", "edge"), ("edge", "vlan"), ("edge", "dc"), ("vlan", "pve"), ("pve", "pbs"), ("dc", "soc"), ("pve", "soc")]
    for a, c in L:
        (x1, y1, _, _), (x2, y2, _, _) = N[a], N[c]
        b += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{EDGE}" stroke-width="3"/>'
    for k, (a, c) in enumerate(L):
        (x1, y1, _, _), (x2, y2, _, _) = N[a], N[c]
        dur = 2.4 + k * .35
        b += (f'<circle r="5" fill="{WARN}"><animate attributeName="cx" values="{x1};{x2}" dur="{dur:.2f}s" repeatCount="indefinite"/>'
              f'<animate attributeName="cy" values="{y1};{y2}" dur="{dur:.2f}s" repeatCount="indefinite"/></circle>')
    for _id, (x, y, lab, c) in N.items():
        b += f'<rect x="{x-72}" y="{y-26}" width="144" height="52" rx="12" fill="{CARD}" stroke="{c}" stroke-width="2.5"/>'
        b += f'<text x="{x}" y="{y+6}" text-anchor="middle" font-size="16" font-weight="600" fill="{TEXT}">{esc(lab)}</text>'
    svg("topology.svg", w, h, b, "Topología de trabajo",
        "Diagrama: usuarios llegan al borde con proxy; del borde salen las VLANs y el directorio con DNS; las VLANs alimentan Proxmox, que envía copias a los backups; el SOC con Wazuh vigila Proxmox y el directorio. Paquetes animados recorren los enlaces.")


# ---------------------------------------------------------------- SERVICIOS (stack)
def services():
    w = 1200
    rows = [
        ("Virtualización", "Proxmox VE · Proxmox Backup Server", INFO),
        ("Sistemas", "Windows Server · Active Directory · GPO · Ubuntu · systemd", VIO),
        ("Redes", "VLAN · VPN WireGuard · DNS interno · Caddy", OK),
        ("Seguridad", "Wazuh · ENS · SSH por clave", PINK),
        ("Automatización", "Bash · PowerShell · Python · Go · Docker", WARN),
        ("Plataforma", "Forgejo · CI/CD · PostgreSQL · Claude Code", INFO),
    ]
    h = 90 + len(rows) * 56
    b = f'<text x="40" y="52" font-size="22" font-weight="700" fill="{TEXT}">Servicios</text>'
    y = 80
    for i, (k, v, c) in enumerate(rows):
        b += f'<rect x="30" y="{y}" width="1140" height="46" rx="10" fill="{CARD}" stroke="{EDGE}"/>'
        b += pulse(58, y + 23, c, 5)
        b += f'<text x="84" y="{y+29}" font-size="17" font-weight="700" fill="{TEXT}">{k}</text>'
        b += f'<text x="300" y="{y+29}" font-size="16" fill="{MUTED}">{esc(v)}</text>'
        b += f'<text x="1150" y="{y+29}" text-anchor="end" font-size="13" font-weight="700" fill="{c}" letter-spacing="1">OPERATIVO</text>'
        y += 56
    svg("services.svg", w, h, b, "Servicios",
        "Tabla de estado con mis áreas: virtualización con Proxmox, sistemas con Windows Server y Linux, redes con VLAN y WireGuard, seguridad con Wazuh y ENS, automatización con Bash, PowerShell, Python, Go y Docker, y plataforma con Forgejo, CI/CD y PostgreSQL.")


# ---------------------------------------------------------------- FLUJO
def workflow():
    w, h = 1200, 250
    steps = [("1", "Detectar", "Alertas y logs", INFO), ("2", "Diagnosticar", "Hechos vs hipótesis", VIO),
             ("3", "Cambiar", "Con backup y rollback", WARN), ("4", "Validar", "Evidencia, no suposición", OK),
             ("5", "Documentar", "Runbook reutilizable", PINK)]
    b = f'<text x="40" y="52" font-size="22" font-weight="700" fill="{TEXT}">Cómo trabajo</text>'
    sw = 212
    for i, (n, t, s, c) in enumerate(steps):
        x = 30 + i * (sw + 20)
        b += card(x, 80, sw, 130)
        b += f'<circle cx="{x+36}" cy="122" r="18" fill="{c}" fill-opacity=".2" stroke="{c}" stroke-width="2"/>'
        b += f'<text x="{x+36}" y="128" text-anchor="middle" font-size="17" font-weight="800" fill="{c}">{n}</text>'
        b += f'<text x="{x+64}" y="128" font-size="20" font-weight="700" fill="{TEXT}">{t}</text>'
        b += f'<text x="{x+20}" y="170" font-size="15" fill="{MUTED}">{esc(s)}</text>'
        if i < 4:
            b += (f'<path d="M{x+sw+3} 145 l12 0" stroke="{c}" stroke-width="3"/>'
                  f'<path d="M{x+sw+9} 138 l8 7 l-8 7" fill="none" stroke="{c}" stroke-width="3"/>')
        b += (f'<rect x="{x}" y="80" width="{sw}" height="130" rx="14" fill="none" stroke="{c}" stroke-width="2.5" opacity="0">'
              f'<animate attributeName="opacity" values="0;1;0" dur="7.5s" begin="{i*1.5}s" repeatCount="indefinite"/></rect>')
    svg("workflow.svg", w, h, b, "Cómo trabajo",
        "Flujo en cinco pasos: detectar con alertas y logs, diagnosticar separando hechos de hipótesis, cambiar con backup y rollback, validar con evidencia y documentar en un runbook reutilizable.")


# ---------------------------------------------------------------- FOOTER
def footer():
    w, h = 1200, 120
    b = (f'<rect x="40" y="25" width="1120" height="70" rx="14" fill="#070b19" stroke="{EDGE}"/>'
         f'<text x="70" y="68" font-family="{MONO}" font-size="22" fill="{OK}">$</text>'
         f'<text x="96" y="68" font-family="{MONO}" font-size="22" fill="{TEXT}">echo "Documentar es la mitad del trabajo"</text>'
         f'<rect x="640" y="46" width="12" height="28" fill="{OK}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>')
    svg("footer.svg", w, h, b, "Lema", "Terminal con el lema: documentar es la mitad del trabajo.")


for f in (header, status_cards, topology, services, workflow, footer):
    f()
print("ok", sorted(os.listdir(OUT)))
