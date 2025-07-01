# corporate_pass_manager.py
import argparse
import json
import os
import random
import string
import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Configurações
DB_FILE = "corporate_credentials.enc"
SALT_FILE = "salt.key"

def derive_key(password: str, salt: bytes) -> bytes:
    """Deriva uma chave de 32 bytes a partir da senha"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def init_db():
    """Inicializa o banco de dados com senha mestra"""
    if os.path.exists(DB_FILE):
        print("Banco de dados já existe!")
        return
    
    print("=== Configuração Inicial do Gerenciador Corporativo ===")
    master_password = getpass.getpass("Defina sua senha mestra: ")
    confirm_password = getpass.getpass("Confirme sua senha mestra: ")
    
    if master_password != confirm_password:
        print("As senhas não coincidem!")
        return
    
    # Gera salt aleatório
    salt = os.urandom(16)
    with open(SALT_FILE, "wb") as f:
        f.write(salt)
    
    # Cria estrutura vazia de banco de dados
    empty_db = {
        "companies": {}
    }
    
    # Salva banco de dados criptografado
    save_db(empty_db, master_password)
    print("✅ Banco de dados corporativo inicializado com sucesso!")

def encrypt_data(data: bytes, key: bytes) -> bytes:
    """Criptografa dados usando Fernet"""
    f = Fernet(key)
    return f.encrypt(data)

def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """Descriptografa dados usando Fernet"""
    f = Fernet(key)
    return f.decrypt(encrypted_data)

def load_db(master_password: str) -> dict:
    """Carrega e descriptografa o banco de dados"""
    if not os.path.exists(DB_FILE):
        print("Banco de dados não encontrado! Execute 'init' primeiro.")
        return None
    
    with open(SALT_FILE, "rb") as f:
        salt = f.read()
    
    key = derive_key(master_password, salt)
    
    with open(DB_FILE, "rb") as f:
        encrypted_data = f.read()
    
    try:
        decrypted_data = decrypt_data(encrypted_data, key)
        return json.loads(decrypted_data.decode())
    except:
        print("❌ Senha mestra incorreta ou banco de dados corrompido!")
        return None

def save_db(db: dict, master_password: str):
    """Criptografa e salva o banco de dados"""
    with open(SALT_FILE, "rb") as f:
        salt = f.read()
    
    key = derive_key(master_password, salt)
    encrypted_data = encrypt_data(json.dumps(db).encode(), key)
    
    with open(DB_FILE, "wb") as f:
        f.write(encrypted_data)

def generate_password(length=16):
    """Gera uma senha segura"""
    characters = string.ascii_letters + string.digits + "!@#$%&*"
    return ''.join(random.choice(characters) for _ in range(length))

def add_credential(company, name, email, department, password=None, notes="", master_password=None):
    """Adiciona nova credencial corporativa ao banco de dados"""
    if not password:
        password = generate_password()
    
    db = load_db(master_password)
    if not db:
        return
    
    # Cria estrutura da empresa se não existir
    if company not in db["companies"]:
        db["companies"][company] = {
            "contacts": {},
            "departments": []  # Corrigido: lista em vez de set
        }
    
    # Adiciona departamento se não existir
    if department not in db["companies"][company]["departments"]:
        db["companies"][company]["departments"].append(department)
    
    # Adiciona contato
    contact_id = f"{name.lower()}-{email.split('@')[0]}"
    db["companies"][company]["contacts"][contact_id] = {
        "name": name,
        "email": email,
        "department": department,
        "password": password,
        "notes": notes
    }
    
    save_db(db, master_password)
    print(f"✅ Credencial de {name} ({company}/{department}) adicionada com sucesso!")
    return password

def find_credentials(company=None, name=None, department=None, master_password=None):
    """Busca credenciais por empresa, nome e/ou departamento"""
    db = load_db(master_password)
    if not db:
        return None
    
    results = []
    
    # Filtro por empresa
    companies = [company] if company else db["companies"].keys()
    
    for comp in companies:
        if comp not in db["companies"]:
            continue
            
        contacts = db["companies"][comp]["contacts"]
        
        # Filtro por nome
        if name:
            # Busca por aproximação no nome
            name_lower = name.lower()
            matched_contacts = [
                c for c in contacts.values() 
                if name_lower in c["name"].lower()
            ]
        else:
            matched_contacts = list(contacts.values())
        
        # Filtro por departamento
        if department:
            matched_contacts = [
                c for c in matched_contacts 
                if department.lower() in c["department"].lower()
            ]
        
        # Adiciona resultados
        for contact in matched_contacts:
            results.append({
                "company": comp,
                "name": contact["name"],
                "email": contact["email"],
                "department": contact["department"],
                "password": contact["password"],
                "notes": contact["notes"]
            })
    
    return results

def display_credentials(credentials):
    """Exibe credenciais de forma organizada"""
    if not credentials:
        print("❌ Nenhuma credencial encontrada com os critérios fornecidos")
        return
    
    print("\n🔍 Resultados da Busca:")
    print("-" * 60)
    for i, cred in enumerate(credentials, 1):
        print(f"{i}. Empresa: {cred['company']}")
        print(f"   Nome:    {cred['name']}")
        print(f"   E-mail:  {cred['email']}")
        print(f"   Setor:   {cred['department']}")
        print(f"   Senha:   {cred['password']}")
        if cred['notes']:
            print(f"   Notas:   {cred['notes']}")
        print("-" * 60)

def list_companies(master_password=None):
    """Lista todas as empresas no banco de dados"""
    db = load_db(master_password)
    if not db or not db["companies"]:
        print("❌ Nenhuma empresa cadastrada no banco de dados!")
        return
    
    print("\n🏢 Empresas Cadastradas:")
    for i, company in enumerate(db["companies"].keys(), 1):
        num_contacts = len(db["companies"][company]["contacts"])
        departments = ", ".join(db["companies"][company]["departments"])
        print(f"{i}. {company} ({num_contacts} contatos)")
        print(f"   Departamentos: {departments}")

def main():
    parser = argparse.ArgumentParser(
        description="Gerenciador Corporativo de Credenciais Seguras",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Comando: init
    subparsers.add_parser("init", help="Inicializar banco de dados")

    # Comando: add
    add_parser = subparsers.add_parser("add", help="Adicionar nova credencial corporativa")
    add_parser.add_argument("company", help="Nome da empresa")
    add_parser.add_argument("name", help="Nome completo do contato")
    add_parser.add_argument("email", help="E-mail corporativo")
    add_parser.add_argument("department", help="Setor/Departamento")
    add_parser.add_argument("-p", "--password", help="Senha (opcional)")
    add_parser.add_argument("-g", "--generate", action="store_true", help="Gerar senha segura automaticamente")
    add_parser.add_argument("-n", "--notes", default="", help="Notas adicionais sobre o contato")

    # Comando: find
    find_parser = subparsers.add_parser("find", help="Buscar credenciais")
    find_parser.add_argument("-c", "--company", help="Filtrar por empresa")
    find_parser.add_argument("-n", "--name", help="Filtrar por nome do contato")
    find_parser.add_argument("-d", "--department", help="Filtrar por departamento/setor")

    # Comando: list
    list_parser = subparsers.add_parser("list", help="Listar empresas cadastradas")

    args = parser.parse_args()

    if args.command == "init":
        init_db()
    else:
        master_password = getpass.getpass("🔑 Senha mestra: ")
        
        if args.command == "add":
            password = args.password
            if args.generate:
                password = generate_password()
                print(f"🔐 Senha gerada: {password}")
            
            add_credential(
                company=args.company,
                name=args.name,
                email=args.email,
                department=args.department,
                password=password,
                notes=args.notes,
                master_password=master_password
            )
        
        elif args.command == "find":
            credentials = find_credentials(
                company=args.company,
                name=args.name,
                department=args.department,
                master_password=master_password
            )
            display_credentials(credentials)
        
        elif args.command == "list":
            list_companies(master_password)

if __name__ == "__main__":
    main()