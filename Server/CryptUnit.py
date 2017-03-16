#! /usr/bin/env Python

# #########################
#    Гибридная система
#       шифрования
# #########################


from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random

'''
# Генерация ключей для сеанса связи
def _GenerateKeys():
    return (
        "",
        ""
    ) # Вернем пару ключей ( Приватный, Публичный )


# Генерация сеансового ключа, создание ЦП сообщения,

def _GenSessionKeyAndEncryptMsg(Msg, BobPublicKey, AlicePrivateKey):
    return ( Msg, "" ) # Возвращаем пару ( открытое сообщение, "")


# Расшифровка сообщения закрытым ключом
def _DecryptMessageAndCheckDS(Msg, MetaDataX, BobPrivateKey, BobPublicKey, AlicePublicKey):
    return Msg
'''

# Генерация ключей для сеанса связи
def _GenerateKeys():

    Key = RSA.generate(2048)
    return (
        Key.exportKey('PEM'), # Приватный ключ
        Key.publickey().exportKey('PEM') # Публичный ключ
    ) # Вернем пару ключей ( Приватный, Публичный )


# Генерация сеансового ключа, создание ЦП сообщения,
# шифрование этим ключом сообщения и шифрование
# этого ключа вместе с ЦП открытым ключом
def _GenSessionKeyAndEncryptMsg(Msg, BobPublicKey, AlicePrivateKey):
    # Генерация сеансового ключа
    SessionKey = Random.new().read(32) # 256 bit

    # Шифрование сообщения алг. AES с помощью сессионного ключа
    IV = Random.new().read(16) # 128 bit
    Obj = AES.new(SessionKey, AES.MODE_CFB, IV)
    CryptMessage = IV + Obj.encrypt(Msg)

    # Создадим цифровую подпись (digital signature) с помощью закрытого ключа Алисы
    _PrivateKey = RSA.importKey(AlicePrivateKey)
    HashMsg = SHA.new(Msg)
    DigitalSignature = PKCS1_v1_5.new(_PrivateKey)
    DigitalSignature = DigitalSignature.sign(HashMsg)

    # Шифрование сессионного ключа и ЦП открытым ключом Боба
    _PublicKey = RSA.importKey(BobPublicKey)
    Obj = PKCS1_OAEP.new(_PublicKey)

    MetaDataX = Obj.encrypt(SessionKey)
    MetaDataX += Obj.encrypt(DigitalSignature[:128])
    MetaDataX += Obj.encrypt(DigitalSignature[128:]) # Сессионный ключ + ЦП

    return ( CryptMessage, MetaDataX ) # Возвращаем пару ( Шифрованное сообщение, шифрованый ключ с ЦП )


# Расшифровка сообщения закрытым ключом
def _DecryptMessageAndCheckDS(Msg, MetaDataX, BobPrivateKey, BobPublicKey, AlicePublicKey):
    # Расшифровка сессионного ключа и ЦП с помощью секретного ключа Боба
    _PrivateKey = RSA.importKey(BobPrivateKey)
    Obj = PKCS1_OAEP.new(_PrivateKey)
    SessionKey = Obj.decrypt(MetaDataX[:256])
    sig = Obj.decrypt(MetaDataX[256:512])
    sig += Obj.decrypt(MetaDataX[512:]) # Сессионный ключ + ЦП

    # Расшифровка сообщения алг. AES
    IV = Msg[:16]
    Obj = AES.new(SessionKey, AES.MODE_CFB, IV)
    DMess = Obj.decrypt(Msg[16:])

    # Сверим ЦП
    _PublicKey = RSA.importKey(AlicePublicKey)
    HashMsg = SHA.new(DMess)
    DSign = PKCS1_v1_5.new(_PublicKey)

    if DSign.verify(HashMsg, sig):
        return DMess # ЦП верна, возвратим сообщение
    return # ЦП не совпадает, выводим null


'''
KEYS1 = _GenerateKeys()
KEYS2 = _GenerateKeys()
msg = "Test msg"


X = _GenSessionKeyAndEncryptMsg(msg, KEYS2[1], KEYS1[0])

print _DecryptMessageAndCheckDS(X[0], X[1], KEYS2[0], KEYS2[1], KEYS1[1])

'''

