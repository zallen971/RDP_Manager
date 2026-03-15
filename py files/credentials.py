import keyring

SERVICE_NAME = "PyRDM"


def save_password(connection_id, password):
    keyring.set_password(SERVICE_NAME, str(connection_id), password)


def get_password(connection_id):
    return keyring.get_password(SERVICE_NAME, str(connection_id))


def delete_password(connection_id):
    try:
        keyring.delete_password(SERVICE_NAME, str(connection_id))
    except Exception:
        pass
