FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY server.py .

# Expõe a porta que o servidor SSE utilizará
EXPOSE 8000

# Executa o servidor MCP
CMD ["python", "server.py"]
