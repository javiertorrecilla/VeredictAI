# Imagen base con Python 3.11 y Debian slim
FROM python:3.11-slim

# Evita prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Instalar Java (para Pellet) y utilidades básicas
RUN apt-get update && \
    apt-get install -y default-jre build-essential curl && \
    apt-get clean

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos del backend
COPY . .

# Instalar dependencias Python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto de FastAPI
EXPOSE 8000

# Comando por defecto para iniciar Uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
