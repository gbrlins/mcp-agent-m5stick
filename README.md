# MCP Agent - M5Stick ENV2

Este repositório contém a implementação completa de um Agente MCP (Model Context Protocol) integrado a um sensor físico de temperatura, umidade e pressão **M5Stick ENV2** rodando em um cluster Kubernetes.

A arquitetura permite que assistentes de IA (como o **Rancher Liz Assistant**) consultem métricas ambientais em tempo real diretamente de um hardware físico conectado à internet.

## 📱 Estrutura do Projeto

- `m5stick_env2.py`: Código em MicroPython para gravar no M5Stick que lê o sensor e serve os dados via HTTP.
- `server.py`: Servidor MCP Agent em Python utilizando `fastmcp` para expor as ferramentas de leitura do sensor.
- `Dockerfile`: Configuração para containerizar o servidor MCP.
- `k8s-manifest.yaml`: Manifesto de Deployment, Service (NodePort) e Namespace para o Kubernetes.
- `requirements.txt`: Dependências necessárias para rodar o servidor Python.

## 🚀 Como Configurar e Implantar

### 1. Gravar o M5Stick

1. Configure o seu M5Stick com o firmware do MicroPython/UIFlow.
2. Certifique-se de que o seu sensor **ENV2** está conectado na **Porta A**.
3. Atualize as credenciais do Wi-Fi no arquivo `m5stick_env2.py`:

```
wifi.connect('NOME_DA_REDE', 'SENHA_DA_REDE')
```

1. Grave o arquivo `m5stick_env2.py` no seu dispositivo. Ele inicializará exibindo o IP recebido na tela, as métricas do sensor em tempo real e um contador de requisições.

### 2. Build e Push da Imagem do Agente MCP

Suba o servidor MCP para o seu registro de container Docker:

```
# Build da imagem
docker build -t seuregistry/mcp-m5stick-agent:latest .

# Push da imagem
docker push seuregistry/mcp-m5stick-agent:latest
```

### 3. Deploy no Kubernetes

1. Abra o arquivo `k8s-manifest.yaml` e atualize o campo `image` com o endereço da sua imagem do Docker Hub/Registry.
2. Certifique-se de que as variáveis de ambiente apontam para a URL do seu sensor (ex: `metricas.suseverse.com`):

```
- name: M5STICK_HOST
  value: "metricas.suseverse.com"
```

1. Aplique o manifesto no seu cluster:

```
kubectl apply -f k8s-manifest.yaml
```

### 4. Integração com a Rancher Liz Assistant

1. Descubra a porta aleatória (`NodePort`) criada para o serviço executando:

```
kubectl get svc mcp-m5stick-service -n mcp-agents
```

1. No painel da **Rancher Liz**, adicione um novo Agente com a configuração MCP apontando para o seu Node IP e a NodePort correspondente no caminho `/mcp`:
- **Endpoint:** `http://<IP-DO-NODE-K8S>:<NODEPORT>/mcp`

## 🛠️ Tecnologias Utilizadas

- **MicroPython** (para programação embarcada no ESP32/M5Stick)
- **Python 3.11** & **FastMCP** (GoFastMCP)
- **Docker**
- **Kubernetes** (Namespace, Deployment, NodePort Service)
- **Model Context Protocol (MCP)**

Desenvolvido com ❤️ para conectar o mundo físico às inteligências artificiais.
