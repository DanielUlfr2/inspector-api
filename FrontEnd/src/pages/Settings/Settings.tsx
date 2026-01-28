import { useState, useRef, useEffect } from 'react';
import { User, Pencil, Lock, ArrowRight, BookOpen } from 'lucide-react';
import styles from './Settings.module.css';
import Documentation from '../../components/Documentation/Documentation';
import { getUserProfile } from '../../features/auth/keycloakService';
import apiClient from '../../api/apiClient';

const availableAvatars = [
    { id: 'avatar-01.png', label: 'Ovni' }, { id: 'avatar-02.png', label: 'Año nuevo' },
    { id: 'avatar-03.png', label: 'Pescador' }, { id: 'avatar-04.png', label: 'Galaxia' },
    { id: 'avatar-05.png', label: 'Granja' }, { id: 'avatar-06.png', label: 'Playa' },
    { id: 'avatar-07.png', label: 'Mundial' }, { id: 'avatar-08.png', label: 'Cometa' },
    { id: 'avatar-09.png', label: 'Tierra' }, { id: 'avatar-10.png', label: 'Halloween' },
    { id: 'avatar-11.png', label: 'Invierno' }, { id: 'avatar-12.png', label: 'Navidad' }
];

const Settings = () => {
    // Estado inicial vacío
    const [selectedAvatar, setSelectedAvatar] = useState('avatar-01.png');
    const [tempAvatar, setTempAvatar] = useState('avatar-01.png');
    const [isPickerOpen, setIsPickerOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const pickerRef = useRef<HTMLDivElement>(null);
    const buttonRef = useRef<HTMLButtonElement>(null);

    // ESTADO PARA TABS
    const [activeTab, setActiveTab] = useState<'profile' | 'documentation'>('profile');

    const [userInfo, setUserInfo] = useState({
        username: '',
        fullName: 'Cargando...',
        email: '',
        role: ''
    });

    useEffect(() => {
        const loadUserData = () => {
            const profile = getUserProfile();
            if (profile) {
                const username = profile.username || '';
                const fullName = profile.name || 'Usuario';
                const email = profile.email || '';

                // Avatar desde Keycloak (puede ser array o string)
                let avatar = 'avatar-01.png';
                if (profile.avatar) {
                    avatar = Array.isArray(profile.avatar) ? profile.avatar[0] : profile.avatar;
                }

                let role = 'Viewer';
                // Lógica simplificada de roles
                const realmRoles = profile.roles || [];
                if (realmRoles.length > 0) {
                    const validRoles = realmRoles.filter((r: string) =>
                        !['offline_access', 'uma_authorization', 'default-roles-milicon'].includes(r)
                    );
                    if (validRoles.length > 0) {
                        role = validRoles.find((r: string) => r.toLowerCase().includes('admin')) ||
                            validRoles.find((r: string) => r.toLowerCase().includes('manager')) ||
                            validRoles[0];
                    }
                }

                setUserInfo({ username, fullName, email, role });
                setSelectedAvatar(avatar);
                setTempAvatar(avatar);
            }
        };
        loadUserData();
    }, []);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            // Si el clic ocurre fuera del picker, cerrar
            if (pickerRef.current && !pickerRef.current.contains(event.target as Node)) {
                setIsPickerOpen(false);
            }
        };
        // Usar capture=true a veces ayuda, pero bubbling standard deberia bastar si usamos stopPropagation
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    // ... (saveAvatar logic unchanged)

    // ... (render)

    const saveAvatar = async () => {
        setLoading(true);
        try {
            // Llamada al backend para actualizar atributo en Keycloak
            await apiClient.post('/auth/avatar', { avatar_id: tempAvatar });

            setSelectedAvatar(tempAvatar);

            // Notificar al Sidebar (Optimistic Update)
            const event = new CustomEvent('avatarUpdated', {
                detail: { avatar: tempAvatar, username: userInfo.username }
            });
            window.dispatchEvent(event);

            alert("Avatar actualizado. El cambio será drástico en el próximo inicio de sesión.");
        } catch (error) {
            console.error(error);
            alert("Error al actualizar avatar.");
        } finally {
            setLoading(false);
        }
    };

    // 2. VERIFICAR Y REDIRIGIR (Cambio de Contraseña)
    const handleVerifyAndRedirect = () => {
        setLoading(true);
        try {
            const clientId = import.meta.env.VITE_KEYCLOAK_CLIENT;
            const realm = import.meta.env.VITE_KEYCLOAK_REALM;
            const keycloakUrl = import.meta.env.VITE_KEYCLOAK_URL;
            const redirectUri = encodeURIComponent(window.location.href);

            // Redirección directa a la acción de Keycloak UPDATE_PASSWORD
            const actionUrl = `${keycloakUrl}/realms/${realm}/protocol/openid-connect/auth?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=openid&kc_action=UPDATE_PASSWORD`;

            window.location.href = actionUrl;
        } catch (error) {
            console.error(error);
            setLoading(false);
        }
    };

    return (
        <div className={styles.layout}>
            <aside className={styles.settingsSidebar}>
                <div className={styles.sidebarSection}>
                    <p className={styles.sectionLabel}>Cuenta</p>
                    <button
                        className={`${styles.sideBtn} ${activeTab === 'profile' ? styles.active : ''}`}
                        onClick={() => setActiveTab('profile')}
                    >
                        <User size={16} /> Mi Perfil
                    </button>
                    <button
                        className={`${styles.sideBtn} ${activeTab === 'documentation' ? styles.active : ''}`}
                        onClick={() => setActiveTab('documentation')}
                    >
                        <BookOpen size={16} /> Documentación
                    </button>
                </div>
            </aside>

            <main className={styles.content}>
                {activeTab === 'profile' ? (
                    <>
                        <section className={styles.section}>
                            <h2 className={styles.title}>Mi Perfil</h2>
                            <div className={styles.profileHeader}>
                                <div className={styles.avatarContainer}>
                                    <img src={`/src/assets/avatars/${tempAvatar}`} className={styles.mainAvatar} alt="Avatar" onError={(e) => (e.target as HTMLImageElement).src = '/src/assets/avatars/avatar-01.png'} />
                                    <button
                                        ref={buttonRef}
                                        className={styles.editBadge}
                                        onMouseDown={(e) => e.stopPropagation()}
                                        onClick={() => setIsPickerOpen(prev => !prev)}
                                    >
                                        <Pencil size={14} />
                                    </button>
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
                                <div className={styles.passwordStepContent}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                        <Lock size={20} />
                                        <h4>Cambiar Contraseña</h4>
                                    </div>
                                    <p>Serás redirigido a la página segura de administración de cuenta.</p>
                                    <button
                                        className={styles.btnPrimary}
                                        onClick={handleVerifyAndRedirect}
                                        disabled={loading}
                                        style={{ marginTop: '15px' }}
                                    >
                                        {loading ? 'Redirigiendo...' : 'Ir a cambiar contraseña'} <ArrowRight size={16} />
                                    </button>
                                </div>
                            </div>
                        </section>
                    </>
                ) : (
                    <Documentation />
                )}
            </main>
        </div>
    );
};

export default Settings;
