import { useState, useEffect, useCallback } from 'react';
import { Fleet } from '../types/fleet';
import { fleetService } from '../features/fleets/fleetService';

export const useFleets = () => {
    const [fleets, setFleets] = useState<Fleet[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchFleets = useCallback(async () => {
        try {
            setLoading(true);
            const data = await fleetService.getAllFleets();
            setFleets(data);
        } catch (err) {
            setError("Error al cargar flotas");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchFleets();
    }, [fetchFleets]);

    return { fleets, loading, error, refresh: fetchFleets };
};