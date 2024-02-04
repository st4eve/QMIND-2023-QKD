from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def encrypt(plain_text, key):
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    cipher_text, tag = cipher.encrypt_and_digest(plain_text)
    return cipher_text, tag, nonce

def decrypt(cipher_text, tag, nonce, key):
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plain_text = cipher.decrypt(cipher_text)
    try:
        cipher.verify(tag)
        return plain_text
    except ValueError:
        return False
    
def generate_key():
    return get_random_bytes(16)

def generate_binary_key(key):
    byte_key = key
    bits = ''.join(format(byte, '08b') for byte in byte_key)
    # Convert binary string to an integer
    integer_value = int(bits, 2)
    # Convert integer to bytes
    byte_array = integer_value.to_bytes((len(bits) + 7) // 8, byteorder='big')
    return byte_array

def main():
    key = generate_key() 
    plain_text = b'Hello, World!'
    cipher_text, tag, nonce = encrypt(plain_text, key)
    key = generate_binary_key(key)
    decrypted_text = decrypt(cipher_text, tag, nonce, key)
    print(decrypted_text)
    
if __name__ == '__main__':
    main()

