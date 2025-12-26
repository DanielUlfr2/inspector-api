import { Outlet } from 'react-router-dom';
import { Sidebar } from '../../components/Sidebar/Sidebar';
import styles from './MainLayout.module.css';

const MainLayout = () => {
    return (
        /* Asegúrate de que aquí diga 'wrapper', no 'layoutWrapper' */
        <div className={styles.wrapper}>
            <Sidebar />
      /* Asegúrate de que aquí diga 'content', no 'mainArea' */
            <main className={styles.content}>
                <Outlet />
            </main>
        </div>
    );
};

export default MainLayout;