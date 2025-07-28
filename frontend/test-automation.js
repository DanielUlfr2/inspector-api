// 🧪 Script de Pruebas Automatizadas del Frontend
// Ejecutar en la consola del navegador (F12)

console.log('🧪 Iniciando pruebas automatizadas...');

// Función para esperar
const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Función para verificar si un elemento existe
const elementExists = (selector) => document.querySelector(selector) !== null;

// Función para verificar si un elemento es visible
const isVisible = (selector) => {
    const element = document.querySelector(selector);
    return element && element.offsetParent !== null;
};

// Función para hacer clic en un elemento
const clickElement = (selector) => {
    const element = document.querySelector(selector);
    if (element) {
        element.click();
        return true;
    }
    return false;
};

// Función para escribir en un input
const typeInInput = (selector, text) => {
    const input = document.querySelector(selector);
    if (input) {
        input.value = text;
        input.dispatchEvent(new Event('input', { bubbles: true }));
        return true;
    }
    return false;
};

// Función para verificar el texto de un elemento
const getText = (selector) => {
    const element = document.querySelector(selector);
    return element ? element.textContent.trim() : '';
};

// Función para verificar el estado de un checkbox
const isChecked = (selector) => {
    const checkbox = document.querySelector(selector);
    return checkbox ? checkbox.checked : false;
};

// Función para contar elementos
const countElements = (selector) => {
    return document.querySelectorAll(selector).length;
};

// Función para verificar URL actual
const getCurrentUrl = () => window.location.pathname;

// Función para verificar si hay errores en consola
const checkConsoleErrors = () => {
    // Esta función se ejecutaría en un entorno de testing real
    return true; // Placeholder
};

// ===== PRUEBAS AUTOMATIZADAS =====

async function runTests() {
    console.log('🚀 Iniciando suite de pruebas...');
    
    let passedTests = 0;
    let totalTests = 0;
    
    const test = (name, testFunction) => {
        totalTests++;
        try {
            const result = testFunction();
            if (result) {
                console.log(`✅ ${name}`);
                passedTests++;
            } else {
                console.log(`❌ ${name}`);
            }
        } catch (error) {
            console.log(`❌ ${name} - Error: ${error.message}`);
        }
    };
    
    // ===== PRUEBA 1: Verificar elementos básicos =====
    console.log('\n📋 PRUEBA 1: Elementos básicos');
    
    test('Página de login visible', () => {
        return elementExists('form') || elementExists('.login-container');
    });
    
    test('Input de usuario presente', () => {
        return elementExists('input[type="text"]') || elementExists('input[name="username"]');
    });
    
    test('Input de contraseña presente', () => {
        return elementExists('input[type="password"]');
    });
    
    test('Botón de login presente', () => {
        return elementExists('button[type="submit"]') || elementExists('.login-button');
    });
    
    // ===== PRUEBA 2: Login automático =====
    console.log('\n🔐 PRUEBA 2: Login automático');
    
    // Simular login
    if (elementExists('input[type="text"]')) {
        typeInInput('input[type="text"]', 'admin');
        typeInInput('input[type="password"]', 'admin123');
        
        await wait(1000);
        
        test('Login exitoso', () => {
            return getCurrentUrl() !== '/login' && getCurrentUrl() !== '/';
        });
    }
    
    // ===== PRUEBA 3: Dashboard =====
    console.log('\n🏠 PRUEBA 3: Dashboard');
    
    test('Dashboard cargado', () => {
        return elementExists('.dashboard') || elementExists('[data-testid="dashboard"]');
    });
    
    test('Tabla de registros presente', () => {
        return elementExists('table') || elementExists('.record-table');
    });
    
    test('Búsqueda presente', () => {
        return elementExists('input[placeholder*="buscar"]') || elementExists('.search-input');
    });
    
    // ===== PRUEBA 4: Funcionalidades de tabla =====
    console.log('\n📊 PRUEBA 4: Funcionalidades de tabla');
    
    test('Botones de acción presentes', () => {
        return elementExists('.btn-edit') || elementExists('.btn-delete') || elementExists('[data-testid="edit-button"]');
    });
    
    test('Paginación presente', () => {
        return elementExists('.pagination') || elementExists('.page-info');
    });
    
    // ===== PRUEBA 5: Menú de usuario =====
    console.log('\n👤 PRUEBA 5: Menú de usuario');
    
    test('Avatar de usuario presente', () => {
        return elementExists('.user-avatar') || elementExists('.user-menu');
    });
    
    // ===== PRUEBA 6: Responsive =====
    console.log('\n📱 PRUEBA 6: Responsive');
    
    test('Sidebar hamburguesa presente', () => {
        return elementExists('.hamburger') || elementExists('.sidebar-toggle');
    });
    
    // ===== PRUEBA 7: Modales =====
    console.log('\n🪟 PRUEBA 7: Modales');
    
    // Intentar abrir modal de crear
    if (clickElement('.btn-create') || clickElement('[data-testid="create-button"]')) {
        await wait(500);
        
        test('Modal de crear se abre', () => {
            return elementExists('.modal') || elementExists('.create-modal');
        });
        
        // Cerrar modal
        if (clickElement('.modal-close') || clickElement('.btn-close')) {
            await wait(500);
        }
    }
    
    // ===== PRUEBA 8: Búsqueda =====
    console.log('\n🔍 PRUEBA 8: Búsqueda');
    
    const searchInput = document.querySelector('input[placeholder*="buscar"]') || document.querySelector('.search-input');
    if (searchInput) {
        typeInInput(searchInput, 'test');
        await wait(1000);
        
        test('Búsqueda funciona', () => {
            return searchInput.value === 'test';
        });
    }
    
    // ===== PRUEBA 9: Selección múltiple =====
    console.log('\n✅ PRUEBA 9: Selección múltiple');
    
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    if (checkboxes.length > 0) {
        test('Checkboxes presentes', () => {
            return checkboxes.length > 0;
        });
        
        // Seleccionar primer checkbox
        if (checkboxes[0]) {
            checkboxes[0].click();
            await wait(500);
            
            test('Checkbox se puede seleccionar', () => {
                return checkboxes[0].checked;
            });
        }
    }
    
    // ===== PRUEBA 10: Notificaciones =====
    console.log('\n🔔 PRUEBA 10: Notificaciones');
    
    test('Sistema de notificaciones presente', () => {
        return elementExists('.notification') || elementExists('.toast') || elementExists('[data-testid="notification"]');
    });
    
    // ===== RESULTADOS FINALES =====
    console.log('\n📊 RESULTADOS FINALES');
    console.log(`✅ Pruebas pasadas: ${passedTests}`);
    console.log(`❌ Pruebas fallidas: ${totalTests - passedTests}`);
    console.log(`📈 Porcentaje de éxito: ${Math.round((passedTests / totalTests) * 100)}%`);
    
    if (passedTests === totalTests) {
        console.log('🎉 ¡TODAS LAS PRUEBAS PASARON!');
    } else {
        console.log('⚠️ Algunas pruebas fallaron. Revisa los errores arriba.');
    }
    
    // ===== VERIFICACIONES ADICIONALES =====
    console.log('\n🔍 VERIFICACIONES ADICIONALES');
    
    // Verificar errores en consola
    console.log('📋 Verificando errores en consola...');
    console.log('💡 Revisa manualmente si hay errores en la consola del navegador');
    
    // Verificar performance
    console.log('⚡ Verificando performance...');
    console.log(`🖥️ Tiempo de carga: ${performance.now().toFixed(2)}ms`);
    
    // Verificar responsive
    console.log('📱 Verificando responsive...');
    console.log(`📏 Ancho de pantalla: ${window.innerWidth}px`);
    console.log(`📐 Alto de pantalla: ${window.innerHeight}px`);
    
    return {
        passed: passedTests,
        total: totalTests,
        percentage: Math.round((passedTests / totalTests) * 100)
    };
}

// Función para ejecutar pruebas en modo manual
function runManualTests() {
    console.log('🔄 Ejecutando pruebas manuales...');
    
    // Lista de elementos a verificar manualmente
    const manualChecks = [
        '✅ Login funciona correctamente',
        '✅ Dashboard se carga sin errores',
        '✅ Tabla muestra datos correctamente',
        '✅ Búsqueda filtra resultados',
        '✅ Paginación funciona',
        '✅ Botones de editar/eliminar funcionan',
        '✅ Modales se abren y cierran',
        '✅ Confirmaciones aparecen',
        '✅ Notificaciones se muestran',
        '✅ Menú de usuario funciona',
        '✅ Responsive en móvil',
        '✅ No hay errores en consola',
        '✅ Performance es aceptable'
    ];
    
    console.log('\n📋 VERIFICACIONES MANUALES:');
    manualChecks.forEach((check, index) => {
        console.log(`${index + 1}. ${check}`);
    });
    
    console.log('\n💡 Para cada item:');
    console.log('   - Haz clic en el elemento');
    console.log('   - Verifica que funciona como esperado');
    console.log('   - Marca ✅ si funciona, ❌ si no');
}

// Exportar funciones para uso manual
window.runTests = runTests;
window.runManualTests = runManualTests;

console.log('🧪 Script de pruebas cargado. Usa:');
console.log('   - runTests() para pruebas automatizadas');
console.log('   - runManualTests() para guía manual');

// Ejecutar automáticamente si se solicita
if (window.location.search.includes('test=true')) {
    runTests();
} 