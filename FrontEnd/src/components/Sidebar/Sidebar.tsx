import { NavLink, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LayoutDashboard, Database, History, LogOut, Sun, Moon, Activity, ChevronLeft, ChevronRight, Settings } from 'lucide-react';
import keycloak from '../../features/auth/keycloakService';
import styles from './Sidebar.module.css';
import { useState, useEffect } from 'react';

const menuItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard', color: '#6366f1' },
    { icon: Database, label: 'Dispositivos', path: '/devices', color: '#8b5cf6' },
    { icon: History, label: 'Historial', path: '/history', color: '#ec4899' },
];

export const Sidebar = () => {
    const navigate = useNavigate();
    const [theme, setTheme] = useState(() => {
        return localStorage.getItem('theme') || 'dark';
    });
    const [isCollapsed, setIsCollapsed] = useState(false);
    const [userInfo, setUserInfo] = useState({ name: '', role: '' });

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

            setUserInfo({ name, role });
        }
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
            animate={{ width: isCollapsed ? 80 : 280 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        >
            {/* Toggle Button */}
            <button className={styles.toggleBtn} onClick={toggleSidebar}>
                {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
            </button>

            {/* Logo Section */}
            <div className={styles.logoSection}>
                <div className={styles.logoIcon}>
                    <Activity size={28} strokeWidth={2.5} />
                </div>
                {!isCollapsed && (
                    <div className={styles.logoText}>
                        <h1>Inspector</h1>
                        <p>Monitor Regional</p>
                    </div>
                )}
            </div>

            {/* Navigation */}
            <nav className={styles.nav}>
                {menuItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) => `${styles.navItem} ${isActive ? styles.active : ''}`}
                        title={isCollapsed ? item.label : ''}
                    >
                        {({ isActive }) => (
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
                        )}
                    </NavLink>
                ))}
            </nav>

            {/* Footer Actions */}
            <div className={styles.footer}>
                {/* User Profile Section */}
                <div className={styles.userProfile} onClick={handleProfileClick}>
                    <div className={styles.avatarWrapper}>
                        <div className={styles.userAvatar}>
                            {userInfo.name.charAt(0).toUpperCase()}
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