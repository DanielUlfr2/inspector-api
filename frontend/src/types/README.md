# Tipos (DTOs) del Proyecto

Este directorio contiene todas las definiciones de tipos TypeScript utilizadas en el proyecto.

## Estructura

### Registro.ts
Contiene las interfaces relacionadas con los registros:

- `Registro`: Interfaz completa de un registro con todos los campos
- `RegistroCreate`: Interfaz para crear un nuevo registro (sin el campo `id`)
- `RegistroUpdate`: Interfaz para actualizar un registro (todos los campos opcionales)

### Auth.ts
Contiene las interfaces relacionadas con la autenticación:

- `User`: Interfaz del usuario con id, username y rol
- `AuthContextType`: Interfaz del contexto de autenticación
- `LoginCredentials`: Interfaz para las credenciales de login
- `LoginResponse`: Interfaz para la respuesta del login

## Uso

### Importar tipos
```typescript
// Importar tipos específicos
import { Registro, RegistroCreate } from '../types/Registro';
import { User, LoginCredentials } from '../types/Auth';

// Importar todos los tipos
import * as Types from '../types';
```

### En servicios
```typescript
import { Registro, RegistroCreate } from '../types/Registro';

export async function getRegistros(): Promise<Registro[]> {
  // ...
}

export async function createRegistro(data: RegistroCreate): Promise<Registro> {
  // ...
}
```

### En componentes
```typescript
import { Registro } from '../types/Registro';

const [registros, setRegistros] = useState<Registro[]>([]);

{registros.map((registro: Registro) => (
  <tr key={registro.id}>
    <td>{registro.nombre}</td>
    <td>{registro.status}</td>
  </tr>
))}
```

## Beneficios

1. **Type Safety**: TypeScript detecta errores en tiempo de compilación
2. **IntelliSense**: Autocompletado y sugerencias en el IDE
3. **Documentación**: Los tipos sirven como documentación del código
4. **Refactoring**: Cambios seguros en la estructura de datos
5. **Consistencia**: Uso consistente de tipos en toda la aplicación

## Convenciones

- Usar `PascalCase` para nombres de interfaces
- Usar `camelCase` para nombres de propiedades
- Agregar comentarios JSDoc para interfaces complejas
- Mantener las interfaces en archivos separados por dominio
- Exportar todos los tipos desde `index.ts` 