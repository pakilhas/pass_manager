# 🔒 Gerenciador de Credenciais Corporativas CLI

## Visão Geral do Projeto
Um aplicativo de linha de comando seguro para gerenciar credenciais de funcionários por empresa, departamento e nome. Desenvolvido em Python com criptografia AES-256 para proteger informações sensíveis.

## Recursos Principais

### Bibliotecas: cryptography

### Linguagem e Bibliotecas

  -  **Armazenamento seguro de credenciais corporativas** (nome, e-mail, setor, senha)

  -  **Busca hierárquica por empresa → departamento → nome**

  - **Geração automática de senhas seguras** (16 caracteres)

  - **Criptografia avançada com AES-256 e PBKDF2HMAC**

  - **Interface intuitiva de linha de comando**

  - **Persistência de dados com criptografia em repouso**

## Módulos e Funcionalidades
### Sistema de Criptografia
- **PBKDF2HMAC**: Deriva uma chave segura da senha mestra
- **AES-256**: Criptografia de nível industrial para os dados
- **Gerenciamento de Salt**: Gera um salt único para cada instância

## Gerenciamento de Banco de Dados

### Estrutura Hierárquica
    Empresas → Departamentos → Funcionários

## Gerador de Senhas Seguras

## Sistema de Busca Hierárquica

## 🔒 Medidas de Segurança

- **Criptografia AES-256**: Padrão ouro para proteção de dados
- **Derivação de Chave PBKDF2**: 100,000 iterações do SHA-256
- **Armazenamento Seguro**: Dados sempre criptografados em disco
- **Mínima Exposição**: Senhas mestras não são armazenadas

