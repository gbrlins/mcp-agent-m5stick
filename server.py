import os
import sys
import httpx
import logging
from fastmcp import FastMCP

# Configura o logging básico para aparecer no stdout do Kubernetes imediatamente
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("mcp-agent")

# Inicializa o servidor FastMCP (da biblioteca gofastmcp)
mcp = FastMCP("M5Stick-ENV2-Agent")

# Obtém as configurações do ambiente do Kubernetes
M5STICK_SCHEME = os.environ.get("M5STICK_SCHEME", "http").strip()
M5STICK_HOST = os.environ.get("M5STICK_HOST", "metricas.suseverse.com").strip()
M5STICK_PORT = os.environ.get("M5STICK_PORT", "").strip()  # Vazio para usar portas padrão (80/443)

@mcp.tool()
async def get_environment_data() -> str:
    """
    Obtém os dados atuais de temperatura, humidade e pressão atmosférica
    diretamente do sensor ENV2 conectado ao M5Stick exposto publicamente.
    """
    # Monta a URL de forma limpa. Se não houver porta definida, usa apenas o domínio puro
    if M5STICK_PORT:
        url = f"{M5STICK_SCHEME}://{M5STICK_HOST}:{M5STICK_PORT}/"
    else:
        url = f"{M5STICK_SCHEME}://{M5STICK_HOST}/"
        
    logger.info("=== [TOOL CALL] get_environment_data() acionada pela Liz ===")
    logger.info(f"Tentando conectar ao M5Stick no endereço: {url}")
    
    try:
        # Utiliza um cliente HTTP assíncrono com timeout de 10 segundos
        async with httpx.AsyncClient() as client:
            logger.info("Enviando requisição GET para o endpoint público...")
            response = await client.get(url, timeout=10.0)
            
            logger.info(f"Resposta recebida. Status HTTP: {response.status_code}")
            response.raise_for_status()
            
            # Lê o JSON retornado pelo seu M5Stick
            data = response.json()
            logger.info(f"Dados brutos decodificados do JSON: {data}")
            
            temp = data.get('temp')
            hum = data.get('hum')
            pres = data.get('pres')
            
            result = (f"Dados atuais do Sensor M5Stick:\n"
                    f"- Temperatura: {temp} °C\n"
                    f"- Humidade: {hum} %\n"
                    f"- Pressão atmosférica: {pres} hPa")
            
            logger.info("Retornando dados formatados com sucesso para a Liz.")
            return result
                    
    except httpx.ConnectTimeout:
        err_msg = f"TIMEOUT: Limite de tempo de 10s expirou ao tentar conectar em {url}."
        logger.error(err_msg)
        return err_msg
    except httpx.ConnectError as e:
        err_msg = f"ERRO DE CONEXÃO: Não foi possível alcançar o host {M5STICK_HOST}. Detalhes: {e}"
        logger.error(err_msg)
        return err_msg
    except Exception as e:
        err_msg = f"ERRO INESPERADO ao consultar o sensor: {str(e)}"
        logger.error(err_msg, exc_info=True)
        return err_msg

if __name__ == "__main__":
    logger.info("=== CONFIGURAÇÕES DE INICIALIZAÇÃO DO AGENTE ===")
    logger.info(f"Host Configurado: {M5STICK_HOST}")
    logger.info(f"Esquema/Protocolo: {M5STICK_SCHEME}")
    logger.info(f"Porta Alvo: '{M5STICK_PORT}' (Vazio significa porta padrão HTTP/HTTPS)")
    logger.info("================================================")
    
    logger.info("Iniciando o servidor FastMCP com transporte streamable-http na porta 8080...")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8080)
