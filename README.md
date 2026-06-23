# Informe Técnico de Implementación - Código: 001V-17

## 1. Objetivo del Proyecto
Este proyecto consistió en el aprovisionamiento, despliegue automatizado y auditoría de infraestructura programable sobre el router de borde de la empresa cliente CATIND. El objetivo principal fue migrar las configuraciones heredadas y de fábrica del equipo a una arquitectura estandarizada bajo parámetros institucionales corporativos utilizando prácticas modernas de DevNet y NetDevOps, asegurando la verificación independiente de cada servicio configurado.

## 2. Alcance
El alcance del proyecto abarcó la captura del estado inicial del router (baseline), el cambio automático del Hostname corporativo, la instalación del banner de acceso restringido, la asignación de la interfaz lógica Loopback 17 para telemetría, la parametrización de la descripción WAN en GigabitEthernet1 y la sincronización con un servidor NTP centralizado. Quedó fuera del alcance el enrutamiento dinámico y políticas avanzadas de firewall perimetral. Las herramientas empleadas se limitaron al entorno de automatización local interactuando mediante protocolos controlados por APIs.

## 3. Infraestructura Utilizada
* **Dispositivo de Red:** Cisco CSR1000v (Virtual Edge Router) operando con Cisco IOS-XE versión 16.9.
* **Máquina de Control:** Máquina Virtual Linux Ubuntu (DevAsc LabVM) provista por Cisco Networking Academy.
* **Software de Orquestación y Auditoría:** * Ansible Core 2.10+ (Provisionamiento)
  * pyATS & Genie Framework (Auditoría operacional del dispositivo)
  * Python 3.x con librerías `ncclient` y `requests` (Validación de protocolos independientes)

## 4. Tecnologías Empleadas y Justificación
* **pyATS / Genie:** Se utilizó en la Fase 1 y Fase 5 para capturar de forma exacta el estado operacional interno del router como un objeto de datos estructurado, facilitando la creación automatizada de un reporte diferencial de cambios (diff).
* **Ansible:** Empleado en la Fase 2 como el motor principal de aprovisionamiento de configuración debido a su naturaleza sin agentes (agentless) y su capacidad nativa de asegurar la idempotencia.
* **NETCONF:** Protocolo de red basado en XML seleccionado en la Fase 3 para validar de manera estructurada y segura que el árbol total de datos del equipo reflejaba fielmente los cambios pretendidos por el negocio.
* **RESTCONF:** Utilizado en la Fase 4 con respuestas JSON por su bajo consumo de recursos y agilidad de llamadas REST específicas a través de HTTPs, permitiendo validar componentes aislados sin sobrecargar el hardware del router.

## 5. Configuración Aplicada
| Parámetro de Red | Valor Final Configurado |
| :--- | :--- |
| **Hostname** | `RTR-CATIND` |
| **Banner de Acceso** | `ACCESO RESTRINGIDO - CATIND` |
| **Interfaz Creada** | `Loopback17` |
| **Direccionamiento IP Loopback** | `10.1.17.1` / `255.255.255.0` |
| **Descripción WAN (Giga1)** | `Enlace-WAN-Los-Angeles` |
| **Servidor NTP Primario** | `1.1.1.1` |

## 6. Resultados de Validación
La verificación independiente arrojó una coincidencia exacta de los datos configurados frente al diccionario corporativo esperado:

| Componente Evaluado | Protocolo | Estado | Resultado |
| :--- | :--- | :--- | :--- |
| Identidad del Router | NETCONF | [OK] | CONFORME |
| Interfaz Loopback IP & Mask | NETCONF | [OK] | CONFORME |
| Descripción WAN Link | NETCONF | [OK] | CONFORME |
| Servidor de Tiempo NTP | NETCONF | [OK] | CONFORME |
| Identidad del Router | RESTCONF | [OK] | CONFORME |
| Direccionamiento de Gestión | RESTCONF | [OK] | CONFORME |
| Descripción Enlace | RESTCONF | [OK] | CONFORME |
| Sincronización NTP | RESTCONF | [OK] | CONFORME |

## 7. Conclusiones
El router perimetral corporativo `RTR-CATIND` ha sido aprovisionado de forma exitosa y sin reportar discrepancias. La implementación alcanzó un nivel de compliance completo (100% de los criterios auditados conformes). La infraestructura cumple con los estándares exigidos para el traspaso de la plataforma al departamento de Operaciones Globales, cerrándose formalmente el ticket de implementación.
