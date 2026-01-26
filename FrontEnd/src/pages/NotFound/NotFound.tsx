import { useNavigate } from 'react-router-dom';
import { Home } from 'lucide-react';
import Lottie from 'lottie-react';
import animationData from '../../assets/Public/error_edit.json';
import styles from './NotFound.module.css';

const NotFound = () => {
    const navigate = useNavigate();

    return (
        <div className={styles.container}>
            <div className={styles.content}>
                <div className={styles.lottieWrapper}>
                    <Lottie
                        animationData={animationData}
                        loop={true}
                        className={styles.lottie}
                    />
                </div>

                <h2 className={styles.subtitle}>Página no encontrada</h2>
                <p className={styles.description}>
                    Lo sentimos, la página que buscas no existe o ha sido movida.
                </p>
                <button onClick={() => navigate('/dashboard')} className={styles.homeButton}>
                    <Home size={20} />
                    <span>Volver al Dashboard</span>
                </button>
            </div>
        </div>
    );
};

export default NotFound;
