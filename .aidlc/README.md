# AIDLC Documentation - InspectorGestion 5.0

> **Metodología AIDLC** (AI-Driven Lifecycle) aplicada al proyecto InspectorGestion 5.0

---

## 📋 Contenido de la Documentación

Este directorio contiene la documentación formal del sistema siguiendo la metodología AIDLC, diseñada para ser clara, auditable y escalable tanto para humanos como para sistemas de IA.

### Documentos Principales

| Documento | Propósito | Requisitos EARS | Diagramas |
|-----------|-----------|-----------------|-----------|
| **[overview.md](./overview.md)** | Visión general del sistema | - | ✅ |
| **[requirements.md](./requirements.md)** | Requisitos funcionales y no funcionales | ✅ | - |
| **[design.md](./design.md)** | Arquitectura técnica y decisiones de diseño | - | ✅ |
| **[tasks.md](./tasks.md)** | Descomposición de implementación en tareas | - | - |
| **[diagrams.md](./diagrams.md)** | Especificaciones de diagramas para draw.io | - | ✅ |

---

## 📖 Guía de Lectura

### Para Stakeholders y Product Owners
1. Leer **overview.md** para entender el propósito y alcance del sistema
2. Revisar **requirements.md** sección 2 (Requisitos Funcionales) para validar funcionalidades
3. Consultar **diagrams.md** diagramas 1 y 9 (Contexto y Casos de Uso)

### Para Arquitectos y Tech Leads
1. Leer **overview.md** para contexto general
2. Estudiar **design.md** completo para entender arquitectura técnica
3. Revisar **requirements.md** sección 3 (Requisitos No Funcionales)
4. Consultar **diagrams.md** diagramas 2, 5 y 7 (Componentes, Modelo de Datos, Despliegue)

### Para Desarrolladores
1. Leer **overview.md** secciones 4 y 5 (Flujos y Arquitectura)
2. Estudiar **design.md** secciones relevantes a su módulo
3. Consultar **tasks.md** para entender secuencia de implementación
4. Revisar **requirements.md** para criterios de aceptación
5. Usar **diagrams.md** como referencia visual

### Para QA y Testers
1. Leer **overview.md** sección 4 (Flujos Principales)
2. Estudiar **requirements.md** completo (criterios de verificación en cada requisito)
3. Revisar **tasks.md** sección 12 (Testing y Validación)
4. Consultar **diagrams.md** diagramas 3, 4 y 10 (Flujos de negocio)

---

## 🎯 Metodología AIDLC

### Principios

1. **Claridad**: Cada requisito debe ser entendible sin ambigüedad
2. **Trazabilidad**: Relación clara entre requisitos → diseño → tareas → código
3. **Verificabilidad**: Cada requisito tiene criterios de verificación explícitos
4. **Mantenibilidad**: Documentación actualizable y escalable

### Notación EARS

Los requisitos funcionales utilizan la notación **EARS** (Easy Approach to Requirements Syntax):

- **Mientras**: Condición de estado del sistema
- **Cuando**: Evento que dispara el requisito
- **Si**: Condición adicional que debe cumplirse
- **Entonces**: Respuesta esperada del sistema
- **Debe**: Obligatorio (requisito mandatorio)

**Ejemplo**:
> **Cuando** un usuario con permisos solicita reiniciar un dispositivo,  
> **si** el dispositivo está en estado operativo,  
> **entonces** el sistema debe ejecutar el comando de reinicio y monitorear su completitud.

---

## 📊 Estadísticas de la Documentación

| Métrica | Valor |
|---------|-------|
| **Requisitos Funcionales** | 60+ |
| **Requisitos No Funcionales** | 15+ |
| **Tareas de Implementación** | 60 |
| **Diagramas Especificados** | 12 |
| **Tablas de Base de Datos** | 20+ |
| **Endpoints API** | 30+ |
| **Servicios Docker** | 9 |
| **Páginas de Documentación** | ~150 |

---

## 🔄 Trazabilidad

### Ejemplo de Trazabilidad Completa

**Requisito** → **Diseño** → **Tarea** → **Código** → **Verificación**

```
RF-ADM-001: Reinicio de Aplicación
    ↓
Design §4.1: BalenaService.restart_device()
    ↓
T-013: Implementar acciones de dispositivos
    ↓
src/services/balena_service.py::restart_device()
    ↓
Test: T-056 (Tests de Celery Tasks)
```

### Matriz de Trazabilidad

Ver **requirements.md** sección 5 y **tasks.md** sección "Matriz de Trazabilidad".

---

## 🛠️ Diagramas

### Diagramas Prioritarios (Alta)

1. **Contexto del Sistema** - Entender actores y límites
2. **Arquitectura de Componentes** - Entender estructura técnica
3. **Flujo de Sincronización** - Proceso crítico del sistema
4. **Flujo de Reinicio** - Acción principal de administración
5. **Modelo de Datos** - Estructura de persistencia
6. **Casos de Uso** - Funcionalidades desde perspectiva de usuario

### Herramientas Recomendadas

- **draw.io** (diagrams.net) - Recomendado, gratuito, online/offline
- **PlantUML** - Para diagramas de secuencia en texto
- **Mermaid** - Para diagramas embebidos en Markdown

### Ubicación de Diagramas

Los diagramas creados deben guardarse en:
```
.aidlc/diagrams/
├── 01_contexto_sistema.png
├── 02_arquitectura_componentes.png
├── 03_flujo_sincronizacion.png
├── 04_flujo_reinicio.png
├── 05_modelo_datos.png
├── ...
└── README.md
```

---

## 📝 Mantenimiento de la Documentación

### Cuándo Actualizar

La documentación debe actualizarse cuando:

- ✅ Se agregan nuevas funcionalidades (actualizar requirements.md, design.md, tasks.md)
- ✅ Se modifican flujos principales (actualizar overview.md, diagrams.md)
- ✅ Se cambia la arquitectura (actualizar design.md, diagrams.md)
- ✅ Se agregan/eliminan tablas de BD (actualizar design.md, diagrams.md)
- ✅ Se identifican errores o inconsistencias

### Responsables

| Documento | Responsable | Frecuencia de Revisión |
|-----------|-------------|------------------------|
| overview.md | Product Owner / Arquitecto | Trimestral |
| requirements.md | Product Owner / QA Lead | Por sprint |
| design.md | Arquitecto / Tech Lead | Por sprint mayor |
| tasks.md | Tech Lead / Scrum Master | Semanal |
| diagrams.md | Arquitecto | Trimestral |

### Versionado

- Todos los documentos deben estar en Git
- Usar commits descriptivos al actualizar documentación
- Crear tags para versiones mayores (v1.0, v2.0, etc.)

---

## 🔗 Referencias Externas

### Documentación Técnica

- [Balena CLI Documentation](https://www.balena.io/docs/reference/balena-cli/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Keycloak Documentation](https://www.keycloak.org/documentation)

### Metodologías

- [EARS Notation](https://www.iaria.org/conferences2012/filesICCGI12/Tutorial%20EARS.pdf)
- [C4 Model](https://c4model.com/) - Inspiración para diagramas de arquitectura

---

## 📞 Contacto

Para preguntas sobre la documentación:

- **Arquitecto de Software**: [Contacto]
- **Tech Lead**: [Contacto]
- **Product Owner**: [Contacto]

---

## 📄 Licencia

Esta documentación es propiedad de [Organización] y está sujeta a las mismas condiciones de licencia que el código fuente del proyecto InspectorGestion 5.0.

---

**Última actualización**: 2026-01-26  
**Versión de la documentación**: 1.0  
**Versión del sistema**: 5.0
