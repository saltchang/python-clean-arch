import pytest

from core.utility.user import hash_password, verify_password


class TestUserUtility:
    def test_hash_password_generates_different_hashes(self):
        password = 'test_password'
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert len(hash1) > 0
        assert hash1 != hash2
        assert len(hash1) == len(hash2)

    def test_verify_password_with_correct_password(self):
        password = 'test_password'
        hashed = hash_password(password)

        assert verify_password(password, hashed)

    def test_verify_password_with_incorrect_password(self):
        password = 'test_password'
        wrong_password = 'wrong_password'
        hashed = hash_password(password)

        assert not verify_password(wrong_password, hashed)

    def test_verify_password_with_empty_password(self):
        password = ''
        hashed = hash_password(password)

        assert verify_password(password, hashed)
        assert not verify_password('some_password', hashed)

    @pytest.mark.parametrize(
        'password',
        [
            'simple',
            'complex_P@ssw0rd!@#$%^&*()_+-=[]{}\\|;:\'",<.?/>',
            'some_password_with_symbols_123',
            '!@#$%^&*()',
            'a' * 100,
        ],
    )
    def test_hash_and_verify_with_different_passwords(self, password: str):
        hashed = hash_password(password)

        assert verify_password(password, hashed)
        assert not verify_password(password + 'modified', hashed)
