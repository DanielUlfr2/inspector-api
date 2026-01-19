import { BarChart3, Truck, MonitorSmartphone, Activity, Wrench, AlertCircle, CheckCircle, Info } from 'lucide-react';
import styles from './Documentation.module.css';
import ImageCarousel from './ImageCarousel';

const Documentation = () => {
    return (
        <div className={styles.container}>
            {/* Hero Section */}
            <div className={styles.hero}>
                <h1 className={styles.heroTitle}>📘 Manual de Usuario</h1>
                <p className={styles.heroSubtitle}>
                    Ecosistema Inspector IQI - Guía completa para la gestión y monitoreo de 198 vehículos (sondas) en tiempo real
                </p>
            </div>

            {/* Section 1: Dashboard */}
            <section className={styles.section}>
                <div className={styles.sectionHeader}>
                    <div className={styles.iconWrapper} style={{ backgroundColor: 'rgba(99, 102, 241, 0.15)' }}>
                        <BarChart3 size={32} style={{ color: '#6366f1' }} />
                    </div>
                    <div>
                        <h2 className={styles.sectionTitle}>Dashboard de Inspección</h2>
                        <p className={styles.sectionSubtitle}>La Vista Global</p>
                    </div>
                </div>

                <div className={styles.content}>
                    <p className={styles.description}>
                        El Dashboard es el centro de mando donde se visualiza la salud de los 198 vehículos (sondas) en tiempo real.
                        Se divide en cuatro estados críticos:
                    </p>

                    <div className={styles.statusGrid}>
                        <div className={styles.statusCard}>
                            <div className={styles.statusIcon} style={{ backgroundColor: 'rgba(34, 197, 94, 0.15)' }}>
                                🟢
                            </div>
                            <h4>Operativo</h4>
                            <p>Equipo asignado, aprovisionado y ejecutando pruebas correctamente.</p>
                        </div>

                        <div className={styles.statusCard}>
                            <div className={styles.statusIcon} style={{ backgroundColor: 'rgba(168, 85, 247, 0.15)' }}>
                                🟣
                            </div>
                            <h4>Libre</h4>
                            <p>Equipos funcionales que no tienen una asignación específica o cliente vinculado.</p>
                        </div>

                        <div className={styles.statusCard}>
                            <div className={styles.statusIcon} style={{ backgroundColor: 'rgba(251, 146, 60, 0.15)' }}>
                                🟠
                            </div>
                            <h4>Reducido</h4>
                            <p>Sondas con degradación en el servicio, posibles fallos de software o imagen corrupta.</p>
                        </div>

                        <div className={styles.statusCard}>
                            <div className={styles.statusIcon} style={{ backgroundColor: 'rgba(239, 68, 68, 0.15)' }}>
                                🔴
                            </div>
                            <h4>Disconnected</h4>
                            <p>Equipos asignados que han perdido conectividad total con el Tenant.</p>
                        </div>
                    </div>

                    <div className={styles.tip}>
                        <Info size={18} />
                        <div>
                            <strong>Tip de Operación:</strong> La gráfica de Tendencia de Estado permite identificar caídas masivas en franjas horarias específicas.
                        </div>
                    </div>

                    {/* Image Carousel */}
                    <ImageCarousel
                        images={[
                            '/placeholder-dashboard-1.png',
                            '/placeholder-dashboard-2.png',
                            '/placeholder-dashboard-3.png'
                        ]}
                        sectionName="Dashboard de Inspección"
                    />
                </div>
            </section>

            {/* Section 2: Fleet Management */}
            <section className={styles.section}>
                <div className={styles.sectionHeader}>
                    <div className={styles.iconWrapper} style={{ backgroundColor: 'rgba(236, 72, 153, 0.15)' }}>
                        <Truck size={32} style={{ color: '#ec4899' }} />
                    </div>
                    <div>
                        <h2 className={styles.sectionTitle}>Gestión de Flotas</h2>
                        <p className={styles.sectionSubtitle}>Agrupación Lógica</p>
                    </div>
                </div>

                <div className={styles.content}>
                    <p className={styles.description}>
                        La sección de Flotas permite segmentar el hardware según su propósito o arquitectura.
                    </p>

                    <div className={styles.subsection}>
                        <h3>Creación</h3>
                        <p>
                            Al pulsar <strong>+ Nueva Flota</strong>, el sistema solicita el tipo de hardware
                            (ej: Raspberry Pi 4 o Aetina N310) y un nombre único.
                        </p>
                    </div>

                    <div className={styles.subsection}>
                        <h3>Administración</h3>
                        <p>Dentro de cada flota (ej: Andina_2), puedes realizar acciones globales:</p>

                        <ul className={styles.list}>
                            <li>
                                <strong>Renombrar:</strong> Protegido contra inyecciones de código y caracteres maliciosos.
                            </li>
                            <li>
                                <strong>Variables de Entorno:</strong> El corazón de la configuración.
                            </li>
                        </ul>
                    </div>

                    <div className={styles.alert}>
                        <AlertCircle size={20} />
                        <div>
                            <strong>Regla de Oro:</strong> Los nombres de variables deben ser en MAYÚSCULAS.
                        </div>
                    </div>

                    <div className={styles.alert}>
                        <AlertCircle size={20} />
                        <div>
                            <strong>Sintaxis:</strong> Los valores consecutivos (como listas de IPs o dominios) deben ingresarse
                            sin espacios innecesarios para no romper la lógica del motor de ejecución.
                        </div>
                    </div>

                    {/* Image Carousel */}
                    <ImageCarousel
                        images={[
                            '/placeholder-fleets-1.png',
                            '/placeholder-fleets-2.png',
                            '/placeholder-fleets-3.png'
                        ]}
                        sectionName="Gestión de Flotas"
                    />
                </div>
            </section>

            {/* Section 3: Device Control */}
            <section className={styles.section}>
                <div className={styles.sectionHeader}>
                    <div className={styles.iconWrapper} style={{ backgroundColor: 'rgba(139, 92, 246, 0.15)' }}>
                        <MonitorSmartphone size={32} style={{ color: '#8b5cf6' }} />
                    </div>
                    <div>
                        <h2 className={styles.sectionTitle}>Control de Dispositivos e Inventario</h2>
                        <p className={styles.sectionSubtitle}>Gestión del átomo del sistema: la sonda individual</p>
                    </div>
                </div>

                <div className={styles.content}>
                    <div className={styles.subsection}>
                        <h3>Acciones Rápidas</h3>
                        <p>
                            Desde la lista general, puedes marcar equipos para ejecutar <strong>Restart</strong>,
                            <strong>Reboot</strong> o <strong>Shutdown</strong> de forma remota.
                        </p>
                    </div>

                    <div className={styles.subsection}>
                        <h3>Ficha Técnica</h3>
                        <p>Al acceder vía el icono de <strong>Link</strong>, entras al detalle profundo:</p>

                        <ul className={styles.list}>
                            <li>
                                <strong>Inventariado (Botón Lápiz):</strong> Abre el panel de Gestión de Inventario y Aprovisionamiento.
                                Aquí vinculas la sonda con datos reales:
                                <ul className={styles.nestedList}>
                                    <li>Service ID</li>
                                    <li>Ubicación geográfica (País/Ciudad)</li>
                                    <li>Nodo OLT/CMTS</li>
                                    <li>Velocidad contratada</li>
                                </ul>
                            </li>
                            <li>
                                <strong>Métricas en Tiempo Real:</strong> Visualización instantánea de CPU, RAM,
                                Almacenamiento y Temperatura.
                            </li>
                        </ul>
                    </div>

                    {/* Image Carousel */}
                    <ImageCarousel
                        images={[
                            '/placeholder-devices-1.png',
                            '/placeholder-devices-2.png',
                            '/placeholder-devices-3.png'
                        ]}
                        sectionName="Control de Dispositivos"
                    />
                </div>
            </section>

            {/* Section 4: Performance Analysis */}
            <section className={styles.section}>
                <div className={styles.sectionHeader}>
                    <div className={styles.iconWrapper} style={{ backgroundColor: 'rgba(6, 182, 212, 0.15)' }}>
                        <Activity size={32} style={{ color: '#06b6d4' }} />
                    </div>
                    <div>
                        <h2 className={styles.sectionTitle}>Análisis de Rendimiento y Salud</h2>
                        <p className={styles.sectionSubtitle}>Diagnósticos avanzados y telemetría</p>
                    </div>
                </div>

                <div className={styles.content}>
                    <p className={styles.description}>
                        Para diagnósticos avanzados, Inspector IQI ofrece herramientas visuales de telemetría:
                    </p>

                    <div className={styles.subsection}>
                        <h3>Histórico de Rendimiento</h3>
                        <p>
                            Al hacer clic en cualquier métrica (ej: Temperatura 60°C), se despliega una gráfica temporal.
                            Esto permite ver si un equipo entró en estado "Reducido" por sobrecalentamiento o saturación
                            de memoria en las últimas 24h.
                        </p>
                    </div>

                    <div className={styles.subsection}>
                        <h3>Terminal de Logs</h3>
                        <p>
                            Ubicado en la parte inferior del detalle del equipo, proporciona el flujo de eventos del
                            sistema operativo en vivo.
                        </p>
                    </div>

                    <div className={styles.subsection}>
                        <h3>Notas (Serial)</h3>
                        <p>
                            Espacio dedicado para datos físicos únicos como la Dirección MAC, facilitando la
                            identificación en campo.
                        </p>
                    </div>

                    {/* Image Carousel */}
                    <ImageCarousel
                        images={[
                            '/placeholder-performance-1.png',
                            '/placeholder-performance-2.png',
                            '/placeholder-performance-3.png'
                        ]}
                        sectionName="Análisis de Rendimiento"
                    />
                </div>
            </section>

            {/* Section 5: Image Deployment Guide */}
            <section className={styles.section}>
                <div className={styles.sectionHeader}>
                    <div className={styles.iconWrapper} style={{ backgroundColor: 'rgba(0, 217, 255, 0.15)' }}>
                        <Wrench size={32} style={{ color: '#00D9FF' }} />
                    </div>
                    <div>
                        <h2 className={styles.sectionTitle}>Guía: Creación y Despliegue de Imagen</h2>
                        <p className={styles.sectionSubtitle}>Paso a Paso</p>
                    </div>
                </div>

                <div className={styles.content}>
                    <p className={styles.description}>
                        Aquí es donde unimos lo anterior para que el usuario "cree" su primera sonda:
                    </p>

                    <div className={styles.steps}>
                        <div className={styles.step}>
                            <div className={styles.stepNumber}>1</div>
                            <div className={styles.stepContent}>
                                <h4>Registro en Flota</h4>
                                <p>Crea la flota en el panel (Gestión de Flotas) para obtener las variables base.</p>
                            </div>
                        </div>

                        <div className={styles.step}>
                            <div className={styles.stepNumber}>2</div>
                            <div className={styles.stepContent}>
                                <h4>Configuración de Variables</h4>
                                <p>Define los DNS_IPV4_HOST y demás parámetros obligatorios en el modal de variables.</p>
                            </div>
                        </div>

                        <div className={styles.step}>
                            <div className={styles.stepNumber}>3</div>
                            <div className={styles.stepContent}>
                                <h4>Preparación de SD</h4>
                                <p>Descarga el archivo de configuración del Tenant y graba la imagen certificada en la MicroSD.</p>
                            </div>
                        </div>

                        <div className={styles.step}>
                            <div className={styles.stepNumber}>4</div>
                            <div className={styles.stepContent}>
                                <h4>Validación</h4>
                                <p>
                                    Una vez encendida, busca el equipo en la Gestión de Dispositivos.
                                    Si aparece como <strong>Libre</strong>, procede a darle al botón de lápiz para Inventariar.
                                </p>
                            </div>
                        </div>

                        <div className={styles.step}>
                            <div className={styles.stepNumber}>5</div>
                            <div className={styles.stepContent}>
                                <h4>Activación</h4>
                                <p>
                                    Una vez aprovisionado con sus datos de servicio, el estado cambiará automáticamente a
                                    <strong> Operativo</strong>.
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className={styles.success}>
                        <CheckCircle size={20} />
                        <div>
                            <strong>¡Listo!</strong> Tu sonda está ahora completamente operativa y lista para ejecutar pruebas.
                        </div>
                    </div>

                    {/* Image Carousel */}
                    <ImageCarousel
                        images={[
                            '/placeholder-deployment-1.png',
                            '/placeholder-deployment-2.png',
                            '/placeholder-deployment-3.png'
                        ]}
                        sectionName="Proceso de Despliegue"
                    />
                </div>
            </section>

            {/* Section 6: Image Creation and Configuration */}
            <section className={styles.section}>
                <div className={styles.sectionHeader}>
                    <div className={styles.iconWrapper} style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)' }}>
                        <Wrench size={32} style={{ color: '#10b981' }} />
                    </div>
                    <div>
                        <h2 className={styles.sectionTitle}>Creación y Configuración de Imagen</h2>
                        <p className={styles.sectionSubtitle}>Subir una imagen a la flota con Balena CLI</p>
                    </div>
                </div>

                <div className={styles.content}>
                    <p className={styles.description}>
                        Este proceso técnico te guiará paso a paso en la descarga, configuración y despliegue de imágenes
                        del sistema operativo para tus sondas utilizando Balena CLI.
                    </p>

                    <div className={styles.subsection}>
                        <h3>📥 Paso 1: Descarga de la Imagen</h3>
                        <p>
                            Descarga la imagen del sistema operativo desde la página oficial de Balena para el hardware específico
                            de tu flota (ej: Raspberry Pi 4, Aetina N310).
                        </p>
                    </div>

                    <div className={styles.subsection}>
                        <h3>📦 Paso 2: Descompresión</h3>
                        <p>Una vez descargada, descomprime el archivo. En Linux, usa el siguiente comando:</p>

                        <div className={styles.codeBlock}>
                            <code>unzip raspberrypi4-64-6.4.2-v16.12.7.img.zip</code>
                        </div>
                    </div>

                    <div className={styles.subsection}>
                        <h3>⚙️ Paso 3: Configuración de la Imagen</h3>
                        <p>Configura la imagen para tu flota específica con el comando Balena CLI:</p>

                        <div className={styles.codeBlock}>
                            <code>balena os configure --dev --fleet InspectorLab raspberrypi4-64-6.4.2-v16.12.7.img</code>
                        </div>

                        <ul className={styles.list}>
                            <li>
                                <strong>--dev</strong>: Indica que es una imagen en modo desarrollo
                            </li>
                            <li>
                                <strong>--fleet InspectorLab</strong>: Asigna la imagen a la flota que creaste
                            </li>
                        </ul>

                        <div className={styles.tip}>
                            <Info size={18} />
                            <div>
                                <strong>Recomendación:</strong> Para cada flota, crea una carpeta específica, ingresa a ella
                                y desde allí carga la imagen. Esto mantiene tu proyecto organizado.
                            </div>
                        </div>
                    </div>

                    <div className={styles.subsection}>
                        <h3>💾 Paso 4: Quemar la Imagen en una Sonda</h3>
                        <p>
                            Una vez configurada la imagen, grábala en una MicroSD. Puedes usar herramientas como
                            <strong> balenaEtcher</strong> (interfaz gráfica) o el comando <strong>dd</strong> en Linux.
                        </p>
                    </div>

                    <div className={styles.subsection}>
                        <h3>🏗️ Estructura Recomendada del Proyecto</h3>
                        <p>Tu proyecto Inspector IQI debe seguir esta estructura de archivos:</p>

                        <div className={styles.codeBlock}>
                            <pre>{`Inspector_iqi/
├── balena.yml
├── CHANGELOG.md
├── docker-compose.yml
├── inspector/
│   ├── app.py
│   ├── constants/
│   ├── Dockerfile.template
│   ├── requirements.txt
│   ├── src/
│   │   ├── Check_Ip_Connection.py
│   │   ├── Db_Inspector.py
│   │   ├── Dns_Test.py
│   │   ├── Events.py
│   │   ├── Http_Test.py
│   │   ├── IQI_Calculator.py
│   │   ├── Ping_Test.py
│   │   ├── Send_Data.py
│   │   └── Speedtest_Ookla.py
│   ├── start.sh
│   └── utils/
├── license.md
├── logo.png
├── README.md
├── repo.yml
└── VERSION`}</pre>
                        </div>
                    </div>

                    <div className={styles.subsection}>
                        <h3>🐳 Docker Compose Configuration</h3>
                        <p>Ejemplo de configuración del archivo <code>docker-compose.yml</code>:</p>

                        <div className={styles.codeBlock}>
                            <pre>{`version: "2.1"

services:
  inspector_4.0:
    build: ./inspector
    labels:
      io.balena.features.dbus: '1'
      io.balena.features.supervisor-api: '1'
      io.balena.update.strategy: download-then-kill
    environment:
      - DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket
    network_mode: host
    volumes:
      - inspector-data:/home/inspector/files
    cap_add:
      - NET_ADMIN

volumes:
  inspector-data:`}</pre>
                        </div>

                        <div className={styles.alert}>
                            <AlertCircle size={20} />
                            <div>
                                <strong>Importante:</strong> La etiqueta <code>io.balena.update.strategy: download-then-kill</code>
                                asegura que las actualizaciones se descarguen completamente antes de reiniciar el contenedor.
                            </div>
                        </div>
                    </div>

                    <div className={styles.subsection}>
                        <h3>📄 Dockerfile Template</h3>
                        <p>Estructura del <code>Dockerfile.template</code> para el servicio Inspector:</p>

                        <div className={styles.codeBlock}>
                            <pre>{`FROM balenalib/%%BALENA_MACHINE_NAME%%-python:3.10.9-bullseye-run

# Instalación de paquetes del sistema
RUN install_packages curl gcc libc6-dev libdbus-1-dev \\
    libglib2.0-dev cmake network-manager vim iw dnsutils \\
    traceroute iproute2 jq openssh-client libsqlite3-dev sqlite3

# Instalación de Speedtest CLI
RUN curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | bash
RUN apt-get install speedtest
RUN speedtest --accept-license --accept-gdpr

# Configuración del entorno Python
WORKDIR /home/inspector/
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache

# Copiar archivos de la aplicación
COPY . ./

# Comando de inicio
CMD ["bash","start.sh"]`}</pre>
                        </div>
                    </div>

                    <div className={styles.subsection}>
                        <h3>🚀 Despliegue a la Flota</h3>
                        <p>Para desplegar tu aplicación a la flota, usa el comando Balena CLI:</p>

                        <div className={styles.codeBlock}>
                            <code>balena deploy Costa_3 --build --emulated --debug</code>
                        </div>

                        <ul className={styles.list}>
                            <li>
                                <strong>Costa_3</strong>: Nombre de tu flota destino
                            </li>
                            <li>
                                <strong>--build</strong>: Construye la imagen localmente
                            </li>
                            <li>
                                <strong>--emulated</strong>: Usa emulación para arquitecturas diferentes
                            </li>
                            <li>
                                <strong>--debug</strong>: Muestra información detallada del proceso
                            </li>
                        </ul>
                    </div>

                    <div className={styles.subsection}>
                        <h3>🛠️ Requisitos Previos</h3>
                        <p>Antes de comenzar, asegúrate de tener instalado:</p>

                        <ul className={styles.list}>
                            <li>
                                <strong>Balena CLI</strong>: Herramienta de línea de comandos de Balena
                            </li>
                            <li>
                                <strong>Docker</strong>: Para construir y gestionar contenedores
                            </li>
                            <li>
                                <strong>Git</strong>: Para control de versiones del proyecto
                            </li>
                            <li>
                                <strong>balenaEtcher</strong>: Para grabar imágenes en MicroSD (opcional)
                            </li>
                        </ul>
                    </div>

                    <div className={styles.success}>
                        <CheckCircle size={20} />
                        <div>
                            <strong>¡Configuración Completa!</strong> Tu imagen está lista para ser desplegada en las sondas de tu flota.
                        </div>
                    </div>

                    {/* Image Carousel */}
                    <ImageCarousel
                        images={[
                            '/placeholder-config-1.png',
                            '/placeholder-config-2.png',
                            '/placeholder-config-3.png'
                        ]}
                        sectionName="Configuración de Imagen"
                    />
                </div>
            </section>
        </div>
    );
};

export default Documentation;
