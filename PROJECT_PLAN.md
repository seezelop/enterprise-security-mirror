# Enterprise Security Mirror

**Plan maestro del proyecto | Versión 0.2 | 26 de octubre de 2026**  
**Estado:** diseño aprobado conceptualmente; implementación pendiente.  
**Repositorio previsto:** `enterprise-security-mirror` (todavía no creado ni modificado por este documento).  
**Proyecto precedente:** [Lab 12, Enterprise Network Security Architecture & Validation](https://github.com/seezelop/network-security-labs/tree/main/labs/12-enterprise-network-security).

## 1. Propósito

Crear una **empresa ficticia pequeña, pero plausible**, con sede central (HQ), tres sucursales, servicios de negocio, identidades, permisos, comunicaciones y controles defensivos. Partir de la topología probada del Lab 12 y desarrollar **tres escenarios de seguridad interrelacionados**. El valor del portfolio no será el número de productos instalados, sino la capacidad de reproducir problemas, capturar evidencias, investigar, endurecer controles y demostrar sus límites.

**Filosofía del escenario espejo**, aplicable a los tres escenarios:

1. **Capa 1, construir y observar:** infraestructura y servicio real; actividad legítima; línea base; riesgos; sensores y reglas de detección justificadas.
2. **Capa 2, atacar y defender:** prueba adversaria autorizada y aislada; secuencia reproducible; evidencias; hallazgos detectados y no detectados; controles correctivos.
3. **Capa 3, explorar límites y validar:** una variación controlada de la prueba para analizar fallas o puntos ciegos de detección; explicación causal; mejora y regresión. Para pruebas de disponibilidad, sustituir «evasión» por análisis de fallas y límites de resiliencia.

**Alcance ético:** todos los ensayos se ejecutan solo en la infraestructura aislada del laboratorio, sin tráfico a terceros ni datos reales.

## 2. Decisiones de arquitectura ya acordadas

- **Un repositorio nuevo** con una empresa y tres escenarios, no tres repositorios ni laboratorios completamente independientes.
- **El Lab 12 permanece intacto.** Su topología se reutiliza como base versionada en el nuevo proyecto; los cambios se realizan en la variante nueva.
- **Tres bloques técnicos transversales**, presentes en distintos escenarios:
  - **A. Secure Enterprise Infrastructure:** arquitectura centralizada/descentralizada, redundancia, routing, IPsec, segmentación, DMZ y defensa en profundidad.
  - **B. Identity & Access Security:** Active Directory (cuando sea viable), identidades, permisos, RADIUS, EAP/EAP-TLS, 802.1X, NAC y autenticación/autorización.
  - **C. Threat Detection & Defense Validation:** telemetría, IDS/IPS, detecciones, correlación, investigación, pruebas de evasión, hardening y automatización.
- **GitHub Actions desde el inicio y durante todo el proyecto** para comprobaciones estáticas, tests offline y regresiones de detección. Las pruebas dinámicas que requieren la topología se harán inicialmente en Ubuntu local. Los workflows se introducirán progresivamente, incluyendo la lectura de resultados PASS/FAIL para aprender CI.
- **Evidencia reproducible y sanitizada** por escenario. El portfolio presenta proyectos prácticos, no experiencia laboral en producción.
- **Instalación incremental y modular**, dada la limitación de hardware. No es necesario encender todos los servicios simultáneamente.

## 3. Infraestructura de partida, verificada en el repositorio anterior

El Lab 12 contiene HQ, tres sucursales, OSPF, switches OVS, FRRouting, nftables, Internet simulado y DMZ; segmentación USERS (`10.70.10.0/24`), SERVERS (`10.70.20.0/24`), ADMIN (`10.70.30.0/24`), MANAGEMENT (`10.70.99.0/24`) y DMZ (`10.70.50.0/24`). Tiene 18 contenedores y 12 comprobaciones automatizadas de política. Los puertos de DNS, SSH y HTTPS actualmente se simulan mediante listeners Netcat: **no son servicios funcionales de aplicación**. Los sistemas propuestos se añaden o sustituyen en la variante del nuevo repo.

**Hardware medido:** Ubuntu sobre equipo físico, aproximadamente 7 GiB de RAM utilizables, Intel i7-7500U (2 núcleos/4 hilos), KVM accesible y 849 GB libres en la partición raíz durante la medición. Con Firefox y VS Code cerrados y el Lab 12 activo se observaron aproximadamente **5 GiB de RAM disponible**. Esto no garantiza que puedan ejecutarse a la vez Windows Server, cliente Windows y Wazuh completo.

**Cuestiones técnicas que deben verificarse:** conectar VM a OVS sin alterar los bridges existentes; adaptar ACL para AD (Kerberos, DNS, LDAP, SMB, RPC); garantizar que la red de gestión Docker no eluda las políticas de datos; evitar que scripts de limpieza destruyan interfaces de VM; ubicar sensores donde puedan ver los flujos (el firewall de `core-r01` no ve necesariamente tráfico intravlan).

## 4. Empresa simulada

**Caso de negocio propuesto:** una empresa de servicios con sede central y tres sucursales. Los empleados usan un portal interno y una aplicación en la DMZ; IT administra infraestructura; algunas operaciones dependen de servicios centralizados. Los departamentos mínimos serán Operaciones, Administración e IT. Las cuentas, grupos, documentos y mensajes serán ficticios. Definiremos explícitamente qué comportamientos son normales, quién puede acceder a cada recurso y qué incidentes preocupan a la organización.

## 5. Tres escenarios principales

### ESC-001: DMZ Web Application Compromise

**Problema:** un servicio publicado en la DMZ ofrece una superficie vulnerable y la segmentación no responde todas las preguntas sobre actividad maliciosa.  
**Bloques:** A y C; B para las identidades de la aplicación.  
**Tecnologías candidatas:** servidor HTTPS real en `web01`, aplicación controlada, logs de aplicación, nftables, Suricata en modo IDS inicialmente y posteriormente IPS si hay recursos y un punto inline definido.

- **Capa 1:** sustituir el listener por una aplicación funcional; crear usuarios, operaciones legítimas, registros y detecciones basadas en comportamiento.
- **Capa 2:** ensayar una vulnerabilidad o error de configuración conocido dentro del entorno; reconstruir el recorrido y verificar firewall, aplicación e IDS.
- **Capa 3:** variar una característica observable para exponer limitaciones de detección; explicar qué telemetría faltó o qué regla fue excesivamente específica; corregir y verificar.
- **Evidencia:** solicitudes de referencia, logs y PCAP saneados, alertas, reglas, políticas, resultados de bloqueo y cobertura.
- **Dependencia:** IDS primero en modo pasivo; IPS inline solo tras demostrar que no rompe la conectividad y que se puede revertir.

### ESC-002: Identity & Privilege Abuse

**Problema:** una identidad obtiene o usa acceso superior al necesario, o un dispositivo intenta entrar a una red sin cumplir la política.  
**Bloques:** B como eje; A y C como controles y observabilidad.  
**Tecnologías candidatas:** FreeRADIUS; EAP-TLS y 802.1X/NAC mediante autenticador compatible (a verificar); AD/Windows Server cuando el hardware lo permita; logs de identidad y red.

- **Capa 1:** crear empleados, grupos y políticas; definir accesos legítimos; configurar registros de autenticación, autorizaciones y alertas.
- **Capa 2:** reproducir un permiso excesivo o intento de acceso no autorizado; recoger eventos, mapear la decisión de acceso y corregir la política.
- **Capa 3:** repetir con una variación legítimamente observable que revele el límite de la regla o la falta de contexto; ajustar la detección y repetir los tests.
- **Evidencia:** matriz de roles/permisos, trazas de autenticación, decisiones RADIUS/AD, reglas, comparativa antes/después y pruebas negativas.
- **Dependencia:** AD real y 802.1X de extremo a extremo son hitos condicionados; no presentar un mock como equivalente a Microsoft AD DS o NAC real.

### ESC-003: Lateral Movement, Segmentation & Resilience

**Problema:** una identidad o estación comprometida intenta alcanzar sistemas internos desde una zona menos confiable; además, la empresa depende de HQ para sus operaciones y debe mantener controles ante fallas de enlace.  
**Bloques:** A, B y C de forma conjunta.  
**Tecnologías candidatas:** OSPF y políticas existentes del Lab 12, túneles IPsec con strongSwan, enlace redundante, logs de red y endpoints, identidad empresarial, detecciones de movimientos no autorizados.

- **Capa 1:** establecer flujos de negocio permitidos por sucursal, segmentación, rutas principales/alternativas y sensores; registrar estado saludable y tráfico normal.
- **Capa 2:** simular intentos controlados de acceso entre segmentos y una falla de enlace; comprobar qué bloquea la red, qué alerta, cuánto tarda la convergencia y si los controles permanecen activos.
- **Capa 3:** evaluar variaciones de trayectoria/flujo que revelen puntos ciegos de observabilidad; para la disponibilidad, analizar límites de failover (no fingir evasión adversaria); corregir y repetir.
- **Evidencia:** topologías, tablas de rutas, cambios OSPF, políticas, logs, PCAP, tiempos de recuperación medidos, mapas de visibilidad y regresiones.
- **Dependencia:** un segundo enlace no existe aún en el Lab 12; debe diseñarse y verificarse. IPsec, si se introduce, debe mostrar el efecto del cifrado sobre la visibilidad del IDS.

**Orden definitivo de implementación y numeración:** **ESC-001 DMZ Web Application Compromise** primero por su menor dependencia de máquinas virtuales; **ESC-002 Identity & Privilege Abuse** después de validar la infraestructura de identidad; **ESC-003 Lateral Movement, Segmentation & Resilience** cuando existan servicios e identidades reales. Los tres siguen siendo objetivos obligatorios del proyecto.

## 6. Temas Security+ y su lugar

| Tema | Lugar | Alcance inicial |
|---|---|---|
| Centralizada vs. descentralizada | ESC-003 | Medir dependencia de HQ y alternativas locales |
| Redundancia de enlaces | ESC-003 | Segundo camino y conmutación con OSPF |
| Defensa en profundidad | Transversal | Perímetro, transporte, acceso, aplicaciones y observabilidad |
| IPsec | ESC-003 | Una VPN site-to-site entre HQ y una sucursal |
| IDS / IPS | ESC-001 y ESC-003 | IDS primero; IPS después, medido |
| EAP / EAP-TLS / RADIUS / 802.1X / NAC | ESC-002 | Pruebas reales si hay autenticador compatible |
| Active Directory / privilegios | ESC-002 y ESC-003 | VM condicionada a viabilidad de recursos |
| SPF / DKIM / DMARC | Extensión posterior del bloque C | Subsistema de correo empresarial simulado, sin forzarlo en los tres escenarios iniciales |

**Regla de alcance:** un tema no se considera implementado solo por instalar una herramienta: necesita un requisito empresarial, una prueba observable, un riesgo y evidencia de funcionamiento. SPF/DKIM/DMARC se preserva explícitamente en el backlog, pero no debe distraer de cerrar los tres escenarios principales.

## 7. Contrato de evidencia por escenario

Cada escenario debe incluir:

1. Problema y riesgo empresarial.
2. Estado inicial, arquitectura y configuraciones relevantes.
3. Actividad normal y comportamiento esperado.
4. Hipótesis, procedimiento de prueba y alcance autorizado.
5. Evidencias de red, host, aplicación o identidad con referencias temporales.
6. Matriz de resultados: permitido/bloqueado, detectado/no detectado, falsos positivos y limitaciones.
7. Medida defensiva, cambio realizado y comparación antes/después.
8. Prueba de regresión automatizada y resultados reproducibles.
9. Sanitización de credenciales, datos y rutas personales antes de publicar.

Un escenario **no está terminado** solo porque el ataque funcionó o apareció una alerta: debe existir una explicación verificable de los resultados y de los límites del control.

## 8. GitHub Actions y validación

**Compromiso didáctico:** el usuario no utilizó anteriormente GitHub Actions. Se aprenderá paso a paso con ejemplos del propio laboratorio: `workflow` → `trigger` (`push`/`pull_request`) → `job` → `step` → `runner` → interpretación de resultados y fallas. No introducir un pipeline complejo sin explicar primero qué ejecuta y por qué.

**Incrementos de CI previstos:**

1. **CI-01, antes del primer servicio:** workflow básico en `.github/workflows/ci.yml` que valide sintaxis de archivos, código Python y tests `pytest` mínimos con datos sintéticos. Observar al menos un check verde y diagnosticar un fallo controlado.
2. **CI-02, ESC-001:** reproducir fixtures de logs HTTP y de aplicación; comprobar reglas, resultados positivos/negativos y regresiones de detección.
3. **CI-03, ESC-002:** verificar políticas de roles, resultados de autenticación y casos de acceso autorizado/no autorizado con fixtures sintéticos.
4. **CI-04, ESC-003:** verificar archivos de políticas de red, escenarios de failover descritos como fixtures, y resultados registrados de tests locales; no presentar una prueba offline como failover medido en ejecución.

Cada workflow deberá justificar el riesgo que controla, indicar qué *no* comprueba y producir un estado legible de PASS/FAIL. Evitar duplicaciones y pipelines sin propósito.


- **CI temprana en runners hospedados:** lint de YAML/JSON y Python, `pytest`, validación de reglas y detecciones contra fixtures sintéticos/sanitizados, comprobaciones de configuraciones y detección de secretos.
- **Pruebas integrales locales:** despliegue Containerlab/OVS, pruebas reales de conectividad, autenticación, rutas, firewall, generación de eventos, sensores y captura de evidencias.
- **Futuro:** valorar CI integral en runners efímeros adecuadamente aislados, solamente tras validar soporte y coste de ejecución.
- **Seguridad:** no ejecutar ataques reales en runners hospedados ni exponer la notebook personal mediante un runner autogestionado permanente para PR públicos.

## 9. Estructura prevista

```text
enterprise-security-mirror/
├── README.md
├── PROJECT_PLAN.md
├── architecture/
├── infrastructure/
│   ├── containerlab/
│   ├── services/
│   └── provisioning/
├── blocks/
│   ├── A-secure-infrastructure/
│   ├── B-identity-access/
│   └── C-threat-detection/
├── scenarios/
│   ├── ESC-001-dmz-web/
│   ├── ESC-002-identity-privileges/
│   └── ESC-003-lateral-movement-resilience/
├── detections/
├── tests/
├── evidence/
└── .github/workflows/
```

## 10. Hitos y criterios de avance

- [ ] **H0:** crear el repositorio y guardar este plan como `PROJECT_PLAN.md`; registrar la revisión/hash del Lab 12 que se reutiliza.
- [ ] **H1:** reproducir la topología original en la variante sin romper las 12 validaciones ni la aislación.
- [ ] **H2:** incorporar un servicio empresarial real y definir su línea base y telemetría.
- [ ] **H3:** completar ESC-001 en sus tres capas, con evidencia sanitizada y tests CI offline.
- [ ] **H4:** implementar la prueba de identidad (FreeRADIUS/802.1X o AD, según viabilidad) y completar ESC-002.
- [ ] **H5:** validar IPsec, redundancia y políticas intersegmento; completar ESC-003.
- [ ] **H6:** publicar matriz de cobertura, resultados de regresión, limitaciones y demostraciones seleccionadas.

## 11. Estado y decisiones pendientes

**Acordado:** un solo proyecto, tres bloques, tres escenarios, tres capas de análisis, Lab 12 sin cambios, GitHub Actions y documentación orientada a portfolio Blue Team. El tema de publicaciones en LinkedIn queda expresamente fuera de esta etapa.

**Pendiente de comprobar:** instalación efectiva de QEMU/libvirt; recursos medidos con VM; conexión KVM↔OVS; viabilidad real de AD y 802.1X; ubicación y consumo de sensores; servicios del portal empresarial; segundo enlace; políticas modificadas sin romper regresiones.

**Próximo paso:** obtener un snapshot versionado del Lab 12 original en el repositorio nuevo (sin copiar `.git/` ni estado generado de Containerlab), desplegar solo una variante por vez y preparar CI-01; después diseñar e implementar **ESC-001 como piloto**, incluyendo los procesos normales, el servicio real, eventos que queremos observar y métricas de éxito, antes de instalar nuevas herramientas.

---

**Nota de persistencia:** este archivo es la referencia de planificación v0.2. Para conservarla en GitHub y revisarla con historial, incorporarla al nuevo repositorio como `PROJECT_PLAN.md` y actualizar versión, fecha, decisiones y hitos con cada cambio relevante. Este documento no crea ni modifica por sí mismo ningún repositorio.

## 12. Estrategia de derivación del Lab 12 (ADR-008)

- **No hacer un fork ni clonar de nuevo toda la serie de 12 labs**: crear un repositorio Git independiente e importar solo el árbol versionado `labs/12-enterprise-network-security` desde un SHA concreto de `network-security-labs`, preferentemente mediante `git archive`.
- Guardar el SHA y el enlace del commit fuente en un archivo `BASELINE_SOURCE.md`, para permitir auditoría y reproducción.
- Los scripts originales (`deploy-lab.sh`, `cleanup-ovs.sh`, `test_policy.py`) contienen nombres `lab12`, `clab-lab12-*` y bridges OVS externos. En la primera validación **no ejecutar ambas topologías simultáneamente**: aunque sean repositorios distintos, competirían por recursos con los mismos nombres.
- Verificar en el nuevo proyecto la copia sin cambios y las 12 pruebas antes de modificar servicios; a continuación diseñar la renominación del nombre de topología, contenedores, bridges/interfaces OVS y test fixtures.
- No copiar `clab-lab12/`, caches, secretos ni otros elementos generados o no versionados.
- No ejecutar `cleanup-ovs.sh` contra una topología activa sin revisar sus efectos: elimina bridges de alcance host.

**Documentos:** `ARCHITECTURE.md` detalla la arquitectura y `BOOTSTRAP.md` contiene el procedimiento preparatorio sin alterar el Lab 12 original.
