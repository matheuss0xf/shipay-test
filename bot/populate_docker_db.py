from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import date
from faker import Faker
import random

Base = declarative_base()

# Define as tabelas
class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)

class Claim(Base):
    __tablename__ = 'claims'
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)
    active = Column(Boolean, nullable=False, default=True)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    created_at = Column(Date, nullable=False)
    updated_at = Column(Date)

class UserClaim(Base):
    __tablename__ = 'user_claims'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    claim_id = Column(Integer, ForeignKey('claims.id'), primary_key=True)

# Configuração do banco de dados
DATABASE_URL = 'postgresql://shipay:shipay123@127.0.0.1:5432/backend_challenge'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Instância do Faker
faker = Faker()

# Função principal para popular o banco de dados
def populate_database():
    # Cria as tabelas no banco
    Base.metadata.create_all(engine)

    # Inserir roles
    roles = [
        Role(description="Admin"),
        Role(description="Edit"),
        Role(description="Member"),
    ]
    session.add_all(roles)

    # Inserir claims
    claims = [
        Claim(description="View", active=True),
        Claim(description="Edit", active=True),
        Claim(description="Delete", active=True),
    ]
    session.add_all(claims)

    # Commit inicial para garantir que Roles e Claims tenham IDs
    session.commit()

    # Associação manual de roles com claims
    role_claim_mapping = {
        "Admin": ["View", "Edit", "Delete"],
        "Edit": ["View", "Edit"],
        "Member": ["View"],
    }

    # Criar relações entre roles e claims
    role_claims = []
    for role in session.query(Role).all():
        claims_for_role = [
            claim.id
            for claim in session.query(Claim).filter(Claim.description.in_(role_claim_mapping[role.description])).all()
        ]
        for claim_id in claims_for_role:
            # Associa cada claim à role
            role_claims.append(UserClaim(user_id=None, claim_id=claim_id))  # Placeholders para posterior vinculação

    # Inserir 30 usuários aleatórios
    users = []
    for _ in range(30):
        user = User(
            name=faker.name(),
            email=faker.email(),
            password=faker.password(length=10),
            role_id=random.choice([1, 2, 3]),  # Escolha aleatória de role
            created_at=date.today(),
            updated_at=None
        )
        users.append(user)
    session.add_all(users)

    # Commit para garantir que os usuários tenham IDs
    session.commit()

    # Associar claims às roles dos usuários
    user_claims = []
    for user in session.query(User).all():
        claims_for_role = [
            claim.id
            for claim in session.query(Claim).filter(
                Claim.description.in_(role_claim_mapping[session.query(Role).get(user.role_id).description])
            ).all()
        ]
        for claim_id in claims_for_role:
            user_claims.append(UserClaim(user_id=user.id, claim_id=claim_id))

    session.add_all(user_claims)

    # Commit final
    session.commit()
    print("Banco de dados populado com sucesso com dados aleatórios!")

if __name__ == "__main__":
    populate_database()
