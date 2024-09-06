import base64

STATIC_KEY = b'your_static_key'  # Replace with your actual static key

def encrypt_message_static(message, key):
    encrypted_message = bytes([a ^ b for a, b in zip(message.encode('utf-8'), key)])
    return base64.b64encode(encrypted_message)

def decrypt_message_static(encrypted_message, key):
    decrypted_message = bytes([a ^ b for a, b in zip(base64.b64decode(encrypted_message), key)])
    return decrypted_message.decode('utf-8')
