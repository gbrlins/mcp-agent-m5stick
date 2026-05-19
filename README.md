# MCP Agent - M5Stick ENV2

Este repositório contém a implementação completa de um Agente MCP (Model Context Protocol) integrado a um sensor físico de temperatura, umidade e pressão **M5Stick ENV2** rodando em um cluster Kubernetes.

A arquitetura permite que assistentes de IA (como o **Rancher Liz Assistant**) consultem métricas ambientais em tempo real diretamente de um hardware físico conectado à internet.

## 📱 Estrutura do Projeto

* `m5stick_env2.py`: Código em MicroPython para gravar no M5Stick que lê o sensor e serve os dados via HTTP.
* `server.py`: Servidor MCP Agent em Python utilizando `fastmcp` para expor as ferramentas de leitura do sensor.
* `Dockerfile`: Configuração para containerizar o servidor MCP.
* `k8s-manifest.yaml`: Manifesto de Deployment, Service (NodePort) e Namespace para o Kubernetes.
* `requirements.txt`: Dependências necessárias para rodar o servidor Python.

## 🚀 Como Configurar e Implantar

### 1. Gravar o M5Stick

1. Configure o seu M5Stick com o firmware do MicroPython/UIFlow.
2. Certifique-se de que o seu sensor **ENV2** está conectado na **Porta A**.
3. Atualize as credenciais do Wi-Fi no arquivo `m5stick_env2.py`:
   ```python
   wifi.connect('NOME_DA_REDE', 'SENHA_DA_REDE')
