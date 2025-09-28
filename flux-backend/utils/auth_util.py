
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from config.env import EncryptConfig


class AuthUtil:
    """
    授权管理模块
    实现AES-CBC加密算法，用于软件授权管理
    """

    @classmethod
    def encrypt(cls, plaintext):
        """使用AES-CBC加密数据"""
        # 对数据进行PKCS7填充
        padder = padding.PKCS7(128).padder()
        data_to_encrypt = plaintext.encode('utf-8')
        padded_data = padder.update(data_to_encrypt) + padder.finalize()

        # 创建密码器并加密
        key = base64.b64decode(EncryptConfig.ENCRYPTION_KEY)
        iv = base64.b64decode(EncryptConfig.ENCRYPTION_IV)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # 返回Base64编码的密文，去除末尾的等号
        return base64.b64encode(ciphertext).decode('utf-8').rstrip('=')

    @classmethod
    def decrypt(cls, ciphertext):
        """使用AES-CBC解密数据"""
        # 解码Base64密文
        decoded_ciphertext = base64.b64decode(ciphertext)

        # 创建密码器并解密
        key = base64.b64decode(EncryptConfig.ENCRYPTION_KEY)
        iv = base64.b64decode(EncryptConfig.ENCRYPTION_IV)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(decoded_ciphertext) + decryptor.finalize()

        # 去除PKCS7填充
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

        return plaintext.decode('utf-8')

# 示例用法
if __name__ == '__main__':

    try:
        auth_util = AuthUtil()
        print("授权管理器初始化成功")

        # 测试加密解密
        plaintext = "这是一段测试文本"
        encrypted = auth_util.encrypt(plaintext)
        decrypted = auth_util.decrypt(encrypted)
        print(f"原文: {plaintext}")
        print(f"加密后: {encrypted}")
        print(f"解密后: {decrypted}")
        print(f"解密是否成功: {plaintext == decrypted}")
    except Exception as e:
        print(f"错误: {e}")