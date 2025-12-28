import { useState, useRef, useEffect } from 'react';
import keycloak from '../../features/auth/keycloakService';
import { User, ShieldCheck, Pencil, X, Lock, ArrowRight, AlertCircle } from 'lucide-react';
import styles from './Settings.module.css';

const availableAvatars = [
    { id: 'avatar-01.png', label: 'Ovni' }, { id: 'avatar-02.png', label: 'Año nuevo' },
    { id: 'avatar-03.png', label: 'Pescador' }, { id: 'avatar-04.png', label: 'Galaxia' },
    { id: 'avatar-05.png', label: 'Granja' }, { id: 'avatar-06.png', label: 'Playa' },
    { id: 'avatar-07.png', label: 'Mundial' }, { id: 'avatar-08.png', label: 'Cometa' },
    { id: 'avatar-09.png', label: 'Tierra' }, { id: 'avatar-10.png', label: 'Halloween' },
    { id: 'avatar-11.png', label: 'Invierno' }, { id: 'avatar-12.png', label: 'Navidad' }
];

const Settings = () => {
    const [selectedAvatar, setSelectedAvatar] = useState(keycloak.tokenParsed?.avatar || 'avatar-01.png');
    const [tempAvatar, setTempAvatar] = useState(selectedAvatar);
    const [isPickerOpen, setIsPickerOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const pickerRef = useRef<HTMLDivElement>(null);

    // ESTADOS PARA CONTRASEÑA
    const [showVerifyInput, setShowVerifyInput] = useState(false);
    const [currentPass, setCurrentPass] = useState('');
    const [passError, setPassError] = useState('');

    const userInfo = {
        username: keycloak.tokenParsed?.preferred_username || '',
        fullName: keycloak.tokenParsed?.name || 'Usuario',
        email: keycloak.tokenParsed?.email || '',
        firstName: keycloak.tokenParsed?.given_name || '',
        lastName: keycloak.tokenParsed?.family_name || '',
        role: (() => {
            const realmRoles = keycloak.tokenParsed?.realm_access?.roles || [];
            const clientRoles = keycloak.tokenParsed?.resource_access?.[import.meta.env.VITE_KEYCLOAK_CLIENT]?.roles || [];
            const allRoles = [...realmRoles, ...clientRoles].filter(r =>
                !['offline_access', 'uma_authorization', 'default-roles-milicon'].includes(r)
            );
            return allRoles.find(r => r.toLowerCase().includes('admin')) ||
                allRoles.find(r => r.toLowerCase().includes('manager')) ||
                allRoles[0] || 'Viewer';
        })()
    };

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (pickerRef.current && !pickerRef.current.contains(event.target as Node)) {
                setIsPickerOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    // 1. GUARDAR AVATAR (POST a /account)
    const saveAvatar = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${keycloak.authServerUrl}/realms/${keycloak.realm}/account`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${keycloak.token}`
                },
                body: JSON.stringify({
                    username: userInfo.username,
                    email: userInfo.email,
                    firstName: userInfo.firstName,
                    lastName: userInfo.lastName,
                    attributes: { avatar: [tempAvatar] }
                })
            });
            if (!response.ok) throw new Error();
            window.dispatchEvent(new CustomEvent('avatarUpdated', { detail: tempAvatar }));
            setSelectedAvatar(tempAvatar);
            alert("Avatar actualizado ✅");
            setIsPickerOpen(false);
        } catch (error) {
            alert("Error al guardar avatar.");
        } finally {
            setLoading(false);
        }
    };

    // 2. VERIFICAR Y REDIRIGIR
    const handleVerifyAndRedirect = async () => {
        setLoading(true);
        setPassError('');
        try {
            // Validamos la contraseña actual usando el flujo de token
            const params = new URLSearchParams();
            params.append('grant_type', 'password');
            params.append('client_id', 'inspector_client');
            params.append('username', userInfo.username);
            params.append('password', currentPass);

            const response = await fetch(`${keycloak.authServerUrl}/realms/${keycloak.realm}/protocol/openid-connect/token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: params
            });

            if (response.ok) {
                // Si es correcta, usamos la ACCIÓN de Keycloak para ir directo al cambio
                // Esto abrirá la página oficial de Keycloak solo para poner la NUEVA clave.
                keycloak.login({
                    action: 'UPDATE_PASSWORD',
                    redirectUri: window.location.href // Para que vuelva a /settings al terminar
                });
            } else {
                setPassError('La contraseña actual no es correcta.');
            }
        } catch (error) {
            setPassError('Error de conexión con Keycloak.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.layout}>
            <aside className={styles.settingsSidebar}>
                <div className={styles.sidebarSection}>
                    <p className={styles.sectionLabel}>Cuenta</p>
                    <button className={`${styles.sideBtn} ${styles.active}`}><User size={16} /> Mi Perfil</button>
                </div>
            </aside>

            <main className={styles.content}>
                <section className={styles.section}>
                    <h2 className={styles.title}>Mi Perfil</h2>
                    <div className={styles.profileHeader}>
                        <div className={styles.avatarContainer}>
                            <img src={`/src/assets/avatars/${tempAvatar}`} className={styles.mainAvatar} alt="Avatar" />
                            <button className={styles.editBadge} onClick={() => setIsPickerOpen(!isPickerOpen)}><Pencil size={14} /></button>
                            {isPickerOpen && (
                                <div className={styles.avatarDropdown} ref={pickerRef}>
                                    <div className={styles.avatarGrid}>
                                        {availableAvatars.map((av) => (
                                            <div key={av.id} className={`${styles.gridItem} ${tempAvatar === av.id ? styles.selected : ''}`} onClick={() => setTempAvatar(av.id)}>
                                                <img src={`/src/assets/avatars/${av.id}`} alt={av.label} />
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                        <div className={styles.userActionZone}>
                            <h3>{userInfo.fullName}</h3>
                            <p className={styles.userRole}>{userInfo.role}</p>
                            <p>{userInfo.email}</p>
                            {tempAvatar !== selectedAvatar && (
                                <button className={styles.btnSaveAvatar} onClick={saveAvatar} disabled={loading}>
                                    {loading ? 'Guardando...' : 'Guardar nueva foto'}
                                </button>
                            )}
                        </div>
                    </div>
                </section>

                <section className={styles.section}>
                    <h2 className={styles.title}>Seguridad</h2>
                    <div className={styles.securityCard}>
                        {!showVerifyInput ? (
                            <div className={styles.passwordStepContent}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <Lock size={20} />
                                    <h4>Cambiar Contraseña</h4>
                                </div>
                                <p>Para cambiar tu clave, primero verificaremos que eres tú.</p>
                                <button className={styles.btnPrimary} onClick={() => setShowVerifyInput(true)} style={{ marginTop: '15px' }}>
                                    Iniciar proceso de cambio
                                </button>
                            </div>
                        ) : (
                            <div className={styles.passwordStepContent}>
                                <h4>Confirma tu identidad</h4>
                                <p>Ingresa tu contraseña actual:</p>
                                <input
                                    type="password"
                                    placeholder="Contraseña actual"
                                    className={styles.inputField}
                                    value={currentPass}
                                    onChange={(e) => setCurrentPass(e.target.value)}
                                    autoFocus
                                />
                                {passError && <div className={styles.errorMessage}><AlertCircle size={14} /> {passError}</div>}
                                <div className={styles.stepActions}>
                                    <button onClick={handleVerifyAndRedirect} className={styles.btnPrimary} disabled={!currentPass || loading}>
                                        {loading ? 'Verificando...' : 'Siguiente'} <ArrowRight size={16} />
                                    </button>
                                    <button onClick={() => { setShowVerifyInput(false); setCurrentPass(''); setPassError(''); }} className={styles.btnGhost}>Cancelar</button>
                                </div>
                            </div>
                        )}
                    </div>
                </section>
            </main>
        </div>
    );
};

export default Settings;