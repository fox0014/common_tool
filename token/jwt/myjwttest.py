import jwt


def create_jwt_token(data=None):
    encoded = jwt.encode(data, 'secret', algorithm='HS256')
    return encoded.decode('ascii')

def decrypt_jwt_token(encoded=None):
    data = jwt.decode(encoded, 'secret', algorithms=['HS256'])
    return data


if __name__ == '__main__':
    data = {'name': 'xiongxiong'}
    create_data = create_jwt_token(data)
    decrypt_data = decrypt_jwt_token(encoded=create_data)
    print(create_data)
    print(decrypt_data)