from auth_service import AuthService
from client_repository import ClientRepository
from access_code_repository import AccessCodeRepository

auth = AuthService(
    ClientRepository(),
    AccessCodeRepository()
)

result = auth.authenticate(
    client_id="asdfasdf",
    password="1234456",
    access_code="123456"
)

print(result)

