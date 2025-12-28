import { NavLink, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    LayoutDashboard,
    MonitorSmartphone,
    Truck,      // Nuevo icono para Flotas
    Activity,   // Nuevo icono para Monitoreo
    LogOut,
    Sun,
    Moon,
    ChevronLeft,
    ChevronRight,
    Settings
} from 'lucide-react';
import defaultAvatar from '../../assets/avatars/avatar-01.png'; // Un avatar por defecto
import { GiCargoShip } from 'react-icons/gi';

import keycloak from '../../features/auth/keycloakService';
import styles from './Sidebar.module.css';
import { useState, useEffect } from 'react';

// Logo imports
import LogoInspector from '../../assets/logos/LogoInspector.png';
import LogoInspectorBlack from '../../assets/logos/LogoInspectorBlack.png';
import IconoInspector from '../../assets/icons/IconoInspector.png';
import IconoInspectorBlack from '../../assets/icons/IconoInspectorBlack.png';

// Estructura de menú actualizada
const menuItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard', color: '#6366f1' },
    { icon: GiCargoShip, label: 'Flotas', path: '/fleets', color: '#ec4899' },
    { icon: MonitorSmartphone, label: 'Dispositivos', path: '/devices', color: '#8b5cf6' },
    { icon: Activity, label: 'Monitoreo', path: 'http://186.97.133.242:3000/d/edk1x2oz8gx6oa/estado-de-inspector?orgId=1&refresh=5m', color: '#06b6d4', isExternal: true },
];

export const Sidebar = () => {
    const navigate = useNavigate();
    const [theme, setTheme] = useState(() => {
        return localStorage.getItem('theme') || 'dark';
    });
    const [isCollapsed, setIsCollapsed] = useState(false);
    const [userInfo, setUserInfo] = useState({ name: '', role: '', avatar: '' });

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }, [theme]);

    useEffect(() => {
        if (keycloak.tokenParsed) {
            const name = keycloak.tokenParsed.preferred_username || keycloak.tokenParsed.name || 'Usuario';
            let role = 'Viewer';
            const realmRoles = keycloak.tokenParsed.realm_access?.roles || [];
            const clientId = import.meta.env.VITE_KEYCLOAK_CLIENT;
            const resourceRoles = keycloak.tokenParsed.resource_access?.[clientId]?.roles || [];
            const allRoles = [...realmRoles, ...resourceRoles];

            const validRoles = allRoles.filter((r: string) =>
                !['offline_access', 'uma_authorization', 'default-roles-milicon'].includes(r)
            );

            if (validRoles.length > 0) {
                role = validRoles.find(r => r.toLowerCase().includes('admin')) ||
                    validRoles.find(r => r.toLowerCase().includes('manager')) ||
                    validRoles[0];
            }

            // 1. Extraemos el atributo 'avatar' que configuramos en el Mapper de Keycloak
            const avatarFile = (keycloak.tokenParsed as any).avatar || '';

            setUserInfo({ name, role, avatar: avatarFile });
        }

        // Listener para actualizar el avatar en tiempo real desde Settings
        const handleAvatarUpdate = (event: Event) => {
            const customEvent = event as CustomEvent;
            setUserInfo(prev => ({ ...prev, avatar: customEvent.detail }));
        };

        window.addEventListener('avatarUpdated', handleAvatarUpdate);

        return () => {
            window.removeEventListener('avatarUpdated', handleAvatarUpdate);
        };
    }, []);

    const toggleTheme = (e: React.MouseEvent) => {
        e.stopPropagation();
        setTheme(prev => prev === 'light' ? 'dark' : 'light');
    };

    const toggleSidebar = () => {
        setIsCollapsed(!isCollapsed);
    };

    const handleProfileClick = () => {
        navigate('/settings');
    };

    return (
        <motion.aside
            className={`${styles.sidebar} ${isCollapsed ? styles.collapsed : ''}`}
            animate={{
                width: isCollapsed ? 80 : 280,
                paddingLeft: isCollapsed ? 10 : 20,
                paddingRight: isCollapsed ? 10 : 20
            }}
            transition={{
                type: 'tween',
                duration: 0.3,
                ease: [0.4, 0, 0.2, 1]
            }}
        >
            {/* Botón de colapso */}
            <button className={styles.toggleBtn} onClick={toggleSidebar}>
                {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
            </button>

            {/* Sección del Logo */}
            <div className={styles.logoSection}>
                {isCollapsed ? (
                    <img
                        src={theme === 'dark' ? IconoInspector : IconoInspectorBlack}
                        alt="Icono"
                        className={styles.logoIconImg}
                    />
                ) : (
                    <img
                        src={theme === 'dark' ? LogoInspector : LogoInspectorBlack}
                        alt="Logo Completo"
                        className={styles.logoFullImg}
                    />
                )}
            </div>

            {/* Navegación Principal */}
            <nav className={styles.nav}>
                {menuItems.map((item) => {
                    const content = (isActive: boolean) => (
                        <div className={styles.navItemContent}>
                            <div
                                className={styles.iconWrapper}
                                style={{
                                    backgroundColor: isActive ? item.color : `${item.color}15`,
                                    boxShadow: isActive ? `0 0 20px ${item.color}40` : 'none'
                                }}
                            >
                                <item.icon
                                    size={20}
                                    strokeWidth={2.5}
                                    style={{ color: isActive ? '#fff' : item.color }}
                                />
                            </div>

                            {!isCollapsed && (
                                <span className={styles.navLabel}>{item.label}</span>
                            )}

                            {isActive && !isCollapsed && (
                                <motion.div
                                    className={styles.activeIndicator}
                                    layoutId="activeIndicator"
                                    style={{ backgroundColor: item.color }}
                                />
                            )}
                        </div>
                    );

                    if ((item as any).isExternal) {
                        return (
                            <a
                                key={item.path}
                                href={item.path}
                                className={styles.navItem}
                                title={isCollapsed ? item.label : ''}
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                {content(false)}
                            </a>
                        );
                    }

                    return (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) => `${styles.navItem} ${isActive ? styles.active : ''}`}
                            title={isCollapsed ? item.label : ''}
                        >
                            {({ isActive }) => content(isActive)}
                        </NavLink>
                    );
                })}
            </nav>

            {/* Acciones del Footer */}
            <div className={styles.footer}>
                <div className={styles.userProfile} onClick={handleProfileClick}>
                    <div className={styles.avatarWrapper}>
                        <div className={styles.userAvatar}>
                            {userInfo.avatar ? (
                                <img
                                    src={`/src/assets/avatars/${userInfo.avatar}`}
                                    alt="Profile"
                                    className={styles.avatarImage}
                                    onError={(e) => {
                                        (e.target as HTMLImageElement).src = defaultAvatar;
                                        (e.target as HTMLImageElement).onerror = null; // Previene loop infinito
                                    }}
                                />
                            ) : (
                                userInfo.name.charAt(0).toUpperCase()
                            )}
                        </div>
                        <div className={styles.settingsBadge}>
                            <Settings size={10} />
                        </div>
                    </div>

                    {!isCollapsed && (
                        <div className={styles.userInfo}>
                            <span className={styles.userName}>{userInfo.name}</span>
                            <span className={styles.userRole}>{userInfo.role}</span>
                        </div>
                    )}
                </div>

                <div className={styles.divider} />

                <button
                    onClick={toggleTheme}
                    className={styles.actionBtn}
                    title={theme === 'light' ? 'Modo Oscuro' : 'Modo Claro'}
                >
                    <div className={styles.iconWrapper} style={{ backgroundColor: '#f59e0b15' }}>
                        {theme === 'light' ?
                            <Moon size={18} style={{ color: '#f59e0b' }} /> :
                            <Sun size={18} style={{ color: '#f59e0b' }} />
                        }
                    </div>
                    {!isCollapsed && (
                        <span>{theme === 'light' ? 'Modo Oscuro' : 'Modo Claro'}</span>
                    )}
                </button>

                <button
                    onClick={() => keycloak.logout()}
                    className={styles.logoutBtn}
                    title="Cerrar Sesión"
                >
                    <div className={styles.iconWrapper} style={{ backgroundColor: '#ef444415' }}>
                        <LogOut size={18} style={{ color: '#ef4444' }} />
                    </div>
                    {!isCollapsed && <span>Cerrar Sesión</span>}
                </button>
            </div>
        </motion.aside>
    );
};