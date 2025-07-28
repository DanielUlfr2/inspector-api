// Función para obtener la URL completa de una imagen desde el backend
export const getImageUrl = (imagePath: string | null): string | null => {
  if (!imagePath) return null;
  
  // Si la imagen ya tiene una URL completa, la devolvemos tal como está
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }
  
  // Si es una ruta relativa, la combinamos con la URL del backend y agregamos un parámetro único para evitar caché
  return `http://localhost:8000${imagePath}?t=${Date.now()}`;
}; 