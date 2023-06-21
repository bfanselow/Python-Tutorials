# Fixtures can return functions, allowing you to pass specific "seed" args to a fixture

from core.utils import make_complicated_user

@pytest.fixture
def make_admin():
    def inner_function(username, email, password):
        return make_complicated_user(
            username=username,
            email=email,
            password=password,
            is_admin=True,
            can_create_public_repos=True,
            can_create_private_repos=True,
        )
    return inner_function

def test_admin_creation(make_admin):
    admin = make_admin(username='frank', email='frank@revsys.com', password='django')
    assert admin.username == 'frank'
    assert admin.is_admin == True
