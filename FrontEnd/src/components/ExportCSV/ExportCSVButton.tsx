// src/components/ExportCSV/ExportCSVButton.tsx
import { Download } from 'lucide-react';
import { Device } from '../../types/device';
import styles from './ExportCSVButton.module.css';

interface Props {
    data: Device[];
    fileName?: string;
}

const ExportCSVButton = ({ data, fileName = 'reporte_dispositivos.csv' }: Props) => {
    const exportToCSV = () => {
        // 1. Definir encabezados
        const headers = [
            "Estado",
            "Nombre del Inspector",
            "UUID",
            "Flota",
            "Nota (Serial)",
            "IP Address",
            "Version OS"
        ];

        // 2. Transformar los datos (excluyendo el link/dashboard_url)
        const rows = data.map(device => [
            device.jsonbobservaciones.overall_status_raw || 'N/A',
            `"${device.strinspectorname}"`, // Comillas para evitar errores con comas en nombres
            device.uuidinspector,
            `"${device.stridinspectorfleet}"`,
            `"${device.strnote}"`,
            device.stripaddress.split(' ')[0],
            `"${device.strosversion}"`
        ]);

        // 3. Unir encabezados y filas
        const csvContent = [
            headers.join(','),
            ...rows.map(row => row.join(','))
        ].join('\n');

        // 4. Crear el archivo y descargar (incluyendo BOM para caracteres especiales)
        const blob = new Blob(["\ufeff" + csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");

        link.setAttribute("href", url);
        link.setAttribute("download", fileName);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <button
            onClick={exportToCSV}
            className={styles.exportBtn}
            title="Exportar a CSV"
            disabled={data.length === 0}
        >
            <Download size={18} />
            <span>Exportar CSV</span>
        </button>
    );
};

export default ExportCSVButton;