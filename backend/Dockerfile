# Imagen base con Python
FROM python:3.11-slim

# Instalar Java (para Pellet)
RUN apt-get update && apt-get install -y default-jre && apt-get clean

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el contenido del backend
COPY . .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto (Railway lo usará automáticamente)
EXPOSE 8000

# Comando para iniciar el servidor
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
