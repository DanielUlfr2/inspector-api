import { Outlet } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sidebar } from '../../components/Sidebar/Sidebar';
import styles from './MainLayout.module.css';

const MainLayout = () => {
    return (
        <motion.div
            className={styles.wrapper}
            layout
            transition={{
                type: 'tween',
                duration: 0.3,
                ease: [0.4, 0, 0.2, 1]
            }}
        >
            <Sidebar />
            <motion.main
                className={styles.content}
                layout
                transition={{
                    type: 'tween',
                    duration: 0.3,
                    ease: [0.4, 0, 0.2, 1]
                }}
            >
                <Outlet />
            </motion.main>
        </motion.div>
    );
};

export default MainLayout;