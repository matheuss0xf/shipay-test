from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from populate_docker_db import User, Role, Claim, UserClaim

query = (
    select(
        User.name.label('user_name'),
        User.email.label('user_email'),
        Role.description.label('role_description'),
        func.string_agg(Claim.description, ', ').label('claim_descriptions'),
    )
    .join(Role, User.role_id == Role.id)
    .join(UserClaim, User.id == UserClaim.user_id)
    .join(Claim, UserClaim.claim_id == Claim.id)
    .group_by(User.id, Role.description)
)

engine = create_engine('postgresql://shipay:shipay123@127.0.0.1:5432/backend_challenge')
with Session(engine) as session:
    results = session.execute(query).all()

for row in results:
    print(row)