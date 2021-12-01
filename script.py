from cryptography.fernet import Fernet

def write_key():
    key = Fernet.generate_key()
    with open("/home/odoo/src/user/api_lcd/pass.key", "wb") as key_file:
        key_file.write(key)
        
def load_key():
    return open("/home/odoo/src/user/api_lcd/pass.key", "rb").read()

write_key()
str_or = "admin"
str_spec = 'utf-8'
print(str_or, type(str_or))
byte_str = str_or.encode(str_spec)
key = load_key()
print(key, type(key))
f = Fernet(key)
encrypted_message = f.encrypt(byte_str)
print(encrypted_message, type(encrypted_message))