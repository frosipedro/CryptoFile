# 🔐 CryptoFile v1.0

**CryptoFile** é uma ferramenta de criptografia e descriptografia de arquivos desenvolvida em Python. O projeto oferece suporte a três algoritmos amplamente reconhecidos — AES-256-GCM, 3DES-CBC e RSA-2048 —, sendo acessível tanto por uma interface gráfica moderna (GUI) quanto por uma interface de terminal (CLI). O objetivo é fornecer uma solução simples, segura e flexível para proteger arquivos locais, adequada tanto para uso pessoal quanto para fins educacionais e técnicos.

---

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Algoritmos Suportados](#-algoritmos-suportados)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
  - [Interface Gráfica (GUI)](#interface-gráfica-gui)
  - [Interface de Terminal (CLI)](#interface-de-terminal-cli)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Detalhes Técnicos](#-detalhes-técnicos)
  - [AES-256-GCM](#aes-256-gcm)
  - [3DES-CBC](#3des-cbc)
  - [RSA-2048](#rsa-2048)
- [Gerenciamento de Chaves RSA](#-gerenciamento-de-chaves-rsa)
- [Segurança](#-segurança)
- [Licença](#-licença)

---

## ✨ Funcionalidades

- **Criptografia e descriptografia** de qualquer tipo de arquivo
- **3 algoritmos disponíveis:** AES-256-GCM, 3DES-CBC e RSA-2048 (híbrido)
- **Detecção automática** do algoritmo usado ao descriptografar
- **Interface gráfica** moderna com tema escuro (Material Design 3) via `customtkinter`
- **Interface de terminal** totalmente funcional com navegador de arquivos interativo
- **Derivação segura de chaves** via PBKDF2-HMAC-SHA256
- **Geração e gerenciamento** de pares de chaves RSA-2048 (.pem)
- **Autenticação de integridade** nos arquivos cifrados (GCM tag / HMAC-SHA256)

---

## 🔑 Algoritmos Suportados

| Algoritmo   | Tipo        | Chave                         | Indicado para                            |
| ----------- | ----------- | ----------------------------- | ---------------------------------------- |
| AES-256-GCM | Simétrico   | Senha (PBKDF2, 600k iter.)    | Uso geral — rápido, seguro e autenticado |
| 3DES-CBC    | Simétrico   | Senha (PBKDF2, 300k iter.)    | Compatibilidade com sistemas legados     |
| RSA-2048    | Assimétrico | Par de chaves pública/privada | Troca segura de arquivos entre partes    |

---

## 🖥️ Pré-requisitos

- Python **3.10** ou superior
- pip

---

## 📦 Instalação

**1. Clone o repositório:**

```bash
git clone https://github.com/seu-usuario/cryptography-tool.git
cd cryptography-tool
```

**2. Crie e ative um ambiente virtual (recomendado):**

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

**3. Instale as dependências:**

```bash
pip install cryptography
pip install customtkinter   # opcional — apenas para a GUI
```

---

## 🚀 Como Usar

### Interface Gráfica (GUI)

Execute sem argumentos para abrir a interface gráfica:

```bash
python main.py
```

> **Requisito:** `customtkinter` instalado. Caso não esteja, o programa exibirá uma mensagem orientando a instalação ou o uso do modo CLI.

A GUI é organizada em quatro abas:

| Aba             | Descrição                                              |
| --------------- | ------------------------------------------------------ |
| Criptografar    | Seleciona arquivo, algoritmo e senha/chave para cifrar |
| Descriptografar | Seleciona arquivo cifrado e fornece credenciais        |
| Chaves RSA      | Gera e lista pares de chaves RSA-2048 (.pem)           |
| Sobre           | Informações sobre os algoritmos e recomendações        |

---

### Interface de Terminal (CLI)

Para usar o modo terminal:

```bash
python main.py --cli
```

Você navegará por menus interativos:

```
[1]  Criptografar arquivo
[2]  Descriptografar arquivo
[3]  Gerenciar chaves RSA
[4]  Sobre os algoritmos
[0]  Sair
```

**Interrompendo a execução:** pressione `Ctrl+C` a qualquer momento para sair com segurança.

---

## 📁 Estrutura do Projeto

```
cryptography-tool/
│
├── main.py                  # Ponto de entrada — GUI ou CLI
│
├── crypto/
│   ├── __init__.py          # Registro central de handlers
│   ├── base.py              # Classe abstrata CryptoHandler
│   ├── aes_handler.py       # Implementação AES-256-GCM
│   ├── des_handler.py       # Implementação 3DES-CBC
│   └── rsa_handler.py       # Implementação RSA-2048 (híbrido)
│
├── ui/
│   ├── gui.py               # Interface gráfica (customtkinter)
│   └── terminal.py          # Interface de terminal (ANSI/CLI)
│
├── utils/
│   └── file_utils.py        # Utilitários de arquivo e navegador CLI
│
├── requirements.txt         # (recomendado criar — veja abaixo)
├── LICENSE
└── README.md
```

---

## 🔬 Detalhes Técnicos

### AES-256-GCM

Algoritmo simétrico autenticado. A chave é derivada da senha usando PBKDF2-HMAC-SHA256 com 600.000 iterações. O modo GCM garante simultaneamente **confidencialidade** e **autenticidade**, dispensando HMAC externo.

**Formato do arquivo cifrado:**

```
[MAGIC 9b] [SALT 16b] [NONCE 12b] [TAG 16b] [CIPHERTEXT]
```

---

### 3DES-CBC

Algoritmo simétrico legado (TripleDES). A chave de 24 bytes é derivada com PBKDF2-HMAC-SHA256 (300.000 iterações). A integridade é verificada via **HMAC-SHA256** sobre o ciphertext.

**Formato do arquivo cifrado:**

```
[MAGIC 9b] [SALT 16b] [IV 8b] [HMAC 32b] [CIPHERTEXT (PKCS7)]
```

> ⚠️ Use 3DES apenas quando houver necessidade de compatibilidade com sistemas legados. Para novos projetos, prefira AES-256-GCM.

---

### RSA-2048

Como RSA não é adequado para cifrar dados grandes diretamente, é utilizado um esquema **híbrido**:

1. Uma chave de sessão AES-256 aleatória é gerada
2. O arquivo é cifrado com AES-256-GCM usando essa chave
3. A chave de sessão é cifrada com a **chave pública RSA** (OAEP + SHA-256)

**Formato do arquivo cifrado:**

```
[MAGIC 9b] [ENC_KEY_LEN 4b] [ENC_SESSION_KEY] [NONCE 12b] [TAG 16b] [CIPHERTEXT]
```

---

## 🗝️ Gerenciamento de Chaves RSA

As chaves RSA são armazenadas no formato PEM e ficam salvas por padrão em:

```
~/.cryptofile/keys/
```

**Para gerar um novo par de chaves:**

- **GUI:** acesse a aba _Chaves RSA_ e preencha o formulário
- **CLI:** selecione a opção `[3] Gerenciar chaves RSA` → `[1] Gerar novo par`

Dois arquivos serão criados:

```
<nome>_private.pem   ← chave privada (protegida por senha opcional)
<nome>_public.pem    ← chave pública (pode ser compartilhada)
```

> ⚠️ **Guarde a chave privada em local seguro.** Sem ela, não é possível descriptografar os arquivos cifrados com a chave pública correspondente.

---

## 🛡️ Segurança

- Toda derivação de chave usa **PBKDF2-HMAC-SHA256** com alto número de iterações para dificultar ataques de força bruta
- O modo **AES-256-GCM** autentica o ciphertext — qualquer adulteração é detectada na descriptografia
- O **3DES-CBC** utiliza HMAC-SHA256 separado para verificação de integridade
- O esquema RSA usa **OAEP com SHA-256**, que é resistente a ataques de texto cifrado escolhido
- Senhas nunca são armazenadas — apenas o salt derivado é salvo no arquivo cifrado

---

## 📄 Licença

Distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

```
Copyright (c) 2026 Pedro Rockenbach Frosi
```

---

## Créditos

- Cristian dos Santos Siquiera — https://github.com/CristianSSiqueira
- Pedro Rockenbach Frosi — https://github.com/frosipedro
