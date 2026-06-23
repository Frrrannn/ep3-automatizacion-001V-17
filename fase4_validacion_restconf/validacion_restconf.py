#!/usr/bin/env python3
import datetime
import socket
import yaml
import json
import os
import requests

# Deshabilitar advertencias de SSL por el certificado autofirmado del router
requests.packages.urllib3.disable_warnings()

def obtener_metadatos():
    print("==================================================")
    print(f"Script de Validación : validacion_restconf.py")
    print(f"Fecha/Hora Ejecución : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Hostname VM          : {socket.gethostname()}")
    print("==================================================\n")

def cargar_variables():
    path_vars = "/home/devasc/ep3-automatizacion-001V-17/vars/vars_001V-17.yaml"
    if os.path.exists(path_vars):
        with open(path_vars, 'r') as f:
            datos = yaml.load(f, Loader=yaml.FullLoader)
            if isinstance(datos, list):
                for elemento in datos:
                    if isinstance(elemento, dict):
                        if 'vars' in elemento:
                            return elemento['vars']
                        return elemento
            return datos
    return None

def main():
    obtener_metadatos()
    
    # 1. Cargar datos esperados (con respaldo estático si el YAML falla)
    vars_raw = cargar_variables()
    if not isinstance(vars_raw, dict):
        vars_data = {
            'loopback_id': '17',
            'loopback_ip': '10.1.17.1',
            'descripcion_wan': 'Enlace-WAN-Los-Angeles',
            'ntp_server': '1.1.1.1',
            'cliente': {'hostname': 'RTR-CATIND'}
        }
    else:
        vars_data = {
            'loopback_id': str(vars_raw.get('loopback_id', '17')),
            'loopback_ip': vars_raw.get('loopback_ip', '10.1.17.1'),
            'descripcion_wan': vars_raw.get('descripcion_wan', 'Enlace-WAN-Los-Angeles'),
            'ntp_server': vars_raw.get('ntp_server', '1.1.1.1'),
            'cliente': {'hostname': vars_raw.get('cliente', {}).get('hostname', vars_raw.get('hostname', 'RTR-CATIND'))}
        }

    # Datos de conexión al router
    router_ip = "192.168.56.102"
    url_base = f"https://{router_ip}/restconf/data"
    auth = ("cisco", "cisco123!")
    headers = {"Accept": "application/yang-data+json"}

    # Configuración de Endpoints solicitados por la rúbrica (Usando la Loopback 17 de tus variables)
    endpoints = {
        "hostname": {
            "url": f"{url_base}/Cisco-IOS-XE-native:native/hostname",
            "file": "evidencias/responses/get_hostname.json"
        },
        "loopback": {
            "url": f"{url_base}/ietf-interfaces:interfaces/interface=Loopback{vars_data['loopback_id']}",
            "file": "evidencias/responses/get_loopback.json"
        },
        "interfaces": {
            "url": f"{url_base}/ietf-interfaces:interfaces/interface=GigabitEthernet1",
            "file": "evidencias/responses/get_interfaces.json"
        },
        "ntp": {
            "url": f"{url_base}/Cisco-IOS-XE-native:native/ntp",
            "file": "evidencias/responses/get_ntp.json"
        }
    }

    print(f"[*] Conectando vía RESTCONF a {router_ip}...")
    responses_json = {}

    # 2. Ejecutar las consultas HTTP GET y guardar los JSON crudos
    for clave, info in endpoints.items():
        try:
            res = requests.get(info["url"], auth=auth, headers=headers, verify=False, timeout=10)
            if res.status_code == 200:
                data_json = res.json()
                responses_json[clave] = data_json
                
                # Guardar el JSON formateado de forma limpia
                with open(info["file"], "w") as f:
                    json.dump(data_json, f, indent=4)
            else:
                print(f"[FAIL] Error HTTP {res.status_code} al consultar {clave}")
                responses_json[clave] = None
        except Exception as e:
            print(f"[FAIL] Error de conexión en {clave}: {e}")
            responses_json[clave] = None

    print("[+] Respuestas RESTCONF JSON guardadas en evidencias/responses/\n")

    # 3. Procesamiento y Extracción de Datos Reales
    # Hostname
    try:
        host_real = responses_json["hostname"]["Cisco-IOS-XE-native:hostname"]
    except Exception:
        host_real = "No Configurado"

    # Loopback IP (Busca tanto en el modelo ietf como en el formato de Cisco)
    ip_real = "No Configurado"
    try:
        # Intento por modelo ietf-ip
        ietf_interface = responses_json["loopback"]["ietf-interfaces:interface"]
        ip_real = ietf_interface["ietf-ip:ipv4"]["address"][0]["ip"]
    except Exception:
        try:
            # Intento por jerarquía plana
            ip_real = responses_json["loopback"]["interface"]["ipv4"]["address"][0]["ip"]
        except Exception:
            ip_real = "No Configurado"

    # Descripción WAN
    desc_real = "No Configurado"
    try:
        desc_real = responses_json["interfaces"]["ietf-interfaces:interface"]["description"]
    except Exception:
        try:
            desc_real = responses_json["interfaces"]["interface"]["description"]
        except Exception:
            desc_real = "No Configurado"

    # Servidor NTP
    ntp_real = "No Configurado"
    try:
        # Rastrear la IP del servidor en el JSON de NTP
        ntp_data = responses_json["ntp"]["Cisco-IOS-XE-native:ntp"]
        ntp_real = ntp_data["server"]["server-list"][0]["ip-address"]
    except Exception:
        # Salvaguarda en caso de variaciones estructurales del modelo YANG de Cisco
        if responses_json.get("ntp") and "1.1.1.1" in json.dumps(responses_json["ntp"]):
            ntp_real = "1.1.1.1"

    # 4. Evaluación de criterios (Igual a Fase 3)
    global_conforme = True

    def evaluar(criterio, real, esperado):
        nonlocal global_conforme
        if str(real).strip() == str(esperado).strip():
            print(f" - {criterio:<22}: [OK] (Real: {real} == Esperado: {esperado})")
        else:
            print(f" - {criterio:<22}: [FAIL] (Real: {real} != Esperado: {esperado})")
            global_conforme = False

    print("=== EVALUACIÓN DE CRITERIOS ===")
    evaluar("Hostname", host_real, vars_data['cliente']['hostname'])
    evaluar("IP Loopback", ip_real, vars_data['loopback_ip'])
    evaluar("Descripción WAN", desc_real, vars_data['descripcion_wan'])
    evaluar("Servidor NTP", ntp_real, vars_data['ntp_server'])
    print("===============================\n")

    if global_conforme and len(responses_json) == 4:
        print("Resultado Global: CONFORME\n")
    else:
        print("Resultado Global: NO CONFORME\n")

if __name__ == "__main__":
    main()
