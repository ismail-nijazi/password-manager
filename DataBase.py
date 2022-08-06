import sqlite3
from datetime import datetime
from cryptography.fernet import Fernet, MultiFernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import hashlib

def hashPassword(password):
    # salt for hashing
    salt = b'\x9a\x10\xa4\x8b\xc3y\xa0\xdcy\xd2\xe1\x8a?pu\x81\xab\xce\xf7\x8e\xc7A\xb8\\fC\x06=\x97\xa5(P'
    key = PBKDF2HMAC(algorithm=hashes.SHA1(), salt=salt, iterations=100000, backend=default_backend(), length=32)
    return base64.urlsafe_b64encode(key.derive(password.encode()))


# This class will create a new table in the database
# The hash of key.txt will be store in that table
class MasterKey:
    def __init__(self):
        # Create a database if it dosent exist otherwise we will just connect ot it
        self.db = sqlite3.connect('data.KeepUrPass')
        self.cur = self.db.cursor()
        # Create a table to store hash of key.txt file in it
        # CHECK(id=1) will prevent of adding more then 1 row to the table
        self.cur.execute("""CREATE TABLE IF NOT EXISTS masterKey(
            id INTEGER PRIMARY KEY,
            key TEXT ,
            date_time DATETIME,
            CHECK (id==1))
            """)

    def createMasterKey(self, update=None):
        time = datetime.now()

        # Initialize which hashing algorithm we are going to use
        hashMaker = hashlib.sha256()
        with open("key.txt", "rb") as hashFile:
            buffer = hashFile.read()
            # Append files content to our hashMaker
            hashMaker.update(buffer)

        # If update is None means it is the first time we are going to create a masterkey
        # And if Update is not None we will just update the current hash that is stored in the table
        if not update:
            # hashMaker.hexdigest(): Generate the hash
            self.cur.execute("INSERT INTO masterKey(key,date_time) VALUES(?,?)", (hashMaker.hexdigest(), time))
        else:
            self.cur.execute("UPDATE masterKey SET key=?, date_time=? WHERE id == 1", (hashMaker.hexdigest(), time))
        self.db.commit()

    # Return the hash which is stored in the table
    def getMasterKey(self):
        self.cur.execute("SELECT * FROM masterKey")
        key = self.cur.fetchall()
        if key:
            return key[0]


# All the user interaction with database will happen in this class
# Create tables
# Add data, Delete data, Update data
# Encrypt the data
class UserInfo:
    def __init__(self, key):
        self.masterkey = key
        self.db = sqlite3.connect('data.KeepUrPass')
        self.cur = self.db.cursor()
        self.createTables()

    # Create 3 tables
    # One for note, one for logins and lastly one for passwords
    def createTables(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY,
            type TEXT,
            title TEXT NOT NULL,
            content TEXT,
            date_time DATETIME)
            """)

        self.cur.execute("""CREATE TABLE IF NOT EXISTS logins (
            id INTEGER PRIMARY KEY,
            type TEXT,
            name TEXT NOT NULL,
            username TEXT,
            url TEXT,
            password TEXT,
            email Text,
            phone TEXT,
            moreInfo TEXT,
            date_time DATETIME)
            """)

        self.cur.execute("""CREATE TABLE IF NOT EXISTS password (
            id INTEGER PRIMARY KEY,
            type TEXT,
            name TEXT NOT NULL,
            username TEXT,
            password TEXT,
            moreInfo TEXT,
            date_time DATETIME)
            """)

    # Get all data to show them in firs page of UI after user is logged in
    def getAllData(self):
        self.cur.execute("SELECT * FROM password")
        passwords = self.cur.fetchall()
        if passwords:
            for i in range(len(passwords)):
                # Convert the passwords[i] to list becuase it will be a tuple which we can't modify
                password = list(passwords[i])
                # Decrypt the password so it can be displayed as a readable text
                password[4] = self.encryptDecrypt(password[4], False).decode()
                passwords[i] = password

        self.cur.execute("SELECT * FROM logins")
        logins = self.cur.fetchall()
        if logins:
            for i in range(len(logins)):
                login = list(logins[i])
                # Decrypt password, email, phone
                login[5] = self.encryptDecrypt(login[5], False).decode()
                login[6] = self.encryptDecrypt(login[6], False).decode()
                login[7] = self.encryptDecrypt(login[7], False).decode()
                logins[i] = login

        self.cur.execute("SELECT * FROM notes")
        notes = self.cur.fetchall()
        if notes:
            for i in range(len(notes)):
                note = list(notes[i])
                # Dcrypt title and the main text
                note[2] = self.encryptDecrypt(note[2], False).decode()
                note[3] = self.encryptDecrypt(note[3], False).decode()
                notes[i] = note

        # Return all decrypted data
        return passwords + logins + notes

    def addPassword(self, name, username, password, more, time=None, idNumber=None):
        if time == None:
            time = datetime.now()
        ecnryptedPassword = self.encryptDecrypt(password, True).decode()
        if idNumber == None:
            self.cur.execute("INSERT INTO password(type,name,username,password,moreInfo,date_time) VALUES('password',?,?,?,?,?)", (
                name, username, ecnryptedPassword, more, time))
        else:
            self.cur.execute("UPDATE password SET name = ?,username = ?,password = ?, moreInfo = ? WHERE id=?",
                             (name, username, ecnryptedPassword, more, idNumber,))

        self.db.commit()

    def updatePassword(self, password, idNumber):
        ecnryptedPassword = self.encryptDecrypt(password, True).decode()
        self.cur.execute("UPDATE password SET password = ? WHERE id=?", (ecnryptedPassword, idNumber,))
        self.db.commit()

    def addLogin(self, name, username, url, password, email, phone, moreinfo, time=None, idNumber=None):
        if time == None:
            time = datetime.now()

        ecnryptedPassword = self.encryptDecrypt(password, True).decode()
        ecryptEmail = self.encryptDecrypt(email, True).decode()
        ecryptPhone = self.encryptDecrypt(phone, True).decode()
        if idNumber == None:
            self.cur.execute("INSERT INTO logins(type,name,username,url,password,email,phone,moreInfo,date_time) VALUES('login',?,?,?,?,?,?,?,?)",
                             (name, username, url, ecnryptedPassword, ecryptEmail, ecryptPhone, moreinfo, time))
        else:
            self.cur.execute("UPDATE logins SET name = ?,username = ?,url = ?,password = ?,email=?,phone=?, moreInfo = ? WHERE id=?",
                             (name, username, url, ecnryptedPassword, ecryptEmail, ecryptPhone, moreinfo, idNumber,))
        self.db.commit()

    def updateLogin(self, password, email, phone, idNumber):
        ecnryptedPassword = self.encryptDecrypt(password, True).decode()
        ecryptEmail = self.encryptDecrypt(email, True).decode()
        ecryptPhone = self.encryptDecrypt(phone, True).decode()
        self.cur.execute("UPDATE logins SET password = ?,email=?,phone=?  WHERE id=?",
                         (ecnryptedPassword, ecryptEmail, ecryptPhone, idNumber,))
        self.db.commit()

    def addNote(self, title, content, time=None, idNumber=None):
        if time == None:
            time = datetime.now()

        ecnryptedTitle = self.encryptDecrypt(title, True).decode()
        ecnryptedText = self.encryptDecrypt(content, True).decode()
        if idNumber == None:
            self.cur.execute("INSERT INTO notes(type,title,content,date_time) VALUES('note',?,?,?)", (ecnryptedTitle, ecnryptedText, time))
        else:
            self.cur.execute("UPDATE notes SET title = ?,content = ? WHERE id=?",
                             (ecnryptedTitle, ecnryptedText, idNumber,))
        self.db.commit()

    def deletePassword(self, idNumber):
        self.cur.execute("DELETE FROM password WHERE id=?", (idNumber,))
        self.db.commit()

    def deleteLogin(self, idNumber):
        self.cur.execute("DELETE FROM logins WHERE id=?", (idNumber,))
        self.db.commit()

    def deleteNote(self, idNumber):
        self.cur.execute("DELETE FROM notes WHERE id=?", (idNumber,))
        self.db.commit()

    def getPasswordById(self, idNumber):
        self.cur.execute("SELECT * FROM password WHERE id=?", (idNumber,))
        password = self.cur.fetchall()
        if password != []:
            password[0] = list(password[0])
            password[0][4] = self.encryptDecrypt(password[0][4], False).decode()
            return password[0]
        else:
            return password

    def getLoginById(self, idNumber):
        self.cur.execute("SELECT * FROM logins WHERE id=?", (idNumber,))
        login = self.cur.fetchall()
        if login != []:
            login[0] = list(login[0])
            login[0][5] = self.encryptDecrypt(login[0][5], False).decode()
            login[0][6] = self.encryptDecrypt(login[0][6], False).decode()
            login[0][7] = self.encryptDecrypt(login[0][7], False).decode()
            return login[0]
        else:
            return login

    def getNoteById(self, idNumber):
        self.cur.execute("SELECT * FROM notes WHERE id=?", (idNumber,))
        note = self.cur.fetchall()
        if note != []:
            note[0] = list(note[0])
            note[0][2] = self.encryptDecrypt(note[0][2], False).decode()
            note[0][3] = self.encryptDecrypt(note[0][3], False).decode()
            return note[0]
        else:
            return note

    def closeDB(self):
        self.db.close()

    # This funcktion gets new masterkey as argument then updates 'key.txt' file with new masterkey
    def updateData(self, newMasterKey):
        oldMasterkey = self.masterkey
        self.masterkey = newMasterKey
        password = hashPassword(newMasterKey)

        with open("key.txt", "r+") as file:
            fileContect = file.read()
            hashList = fileContect.split("<<!>>")
            # save the old password's hash in a variable so we can decrypt data with that
            hashedMasterKey = hashList[73]
            hashList[73] = password.decode()
            file.seek(0)
            file.truncate()
            file.close()
        with open("key.txt", "a") as updateFile:
            updateFile.write('<<!>>'.join(hashList))
            updateFile.close()

        # To complete the change masterkey process we need update the database as well
        masterKey = MasterKey()
        masterKey.createMasterKey(update=True)

        # Get the last id to loop over all the data and decrypt them with old password
        # Then encrypt them again with new password
        self.cur.execute("SELECT id FROM password ORDER BY id DESC LIMIT 1")
        lastPasswordId = self.cur.fetchall()
        self.cur.execute("SELECT id FROM logins ORDER BY id DESC LIMIT 1")
        lastLoginId = self.cur.fetchall()
        self.cur.execute("SELECT id FROM notes ORDER BY id DESC LIMIT 1")
        lastNoteId = self.cur.fetchall()
        # if the list wasn't empty
        if lastPasswordId:
            # count of the row in table password
            countOfRow = lastPasswordId[0][0]
            for idNumber in range(1, countOfRow + 1):
                self.cur.execute("SELECT * FROM password WHERE id=?", (idNumber,))
                row = self.cur.fetchall()
                # if row is empty means the data is dalated
                # And if it is not so the data should be decrypt with old password
                if row:
                    decryptedPassword = self.encryptDecrypt(row[0][4], False, oldKey=oldMasterkey, hashedKey=hashedMasterKey).decode()
                    # Encrypt the data with new password then update the database
                    self.updatePassword(decryptedPassword, idNumber)

        if lastLoginId:
            countOfRow = lastLoginId[0][0]
            for idNumber in range(1, countOfRow + 1):
                self.cur.execute("SELECT * FROM logins WHERE id=?", (idNumber,))
                row = self.cur.fetchall()
                if row:
                    decryptedPassword = self.encryptDecrypt(row[0][5], False, oldKey=oldMasterkey, hashedKey=hashedMasterKey).decode()
                    decryptedEmail = self.encryptDecrypt(row[0][6], False, oldKey=oldMasterkey, hashedKey=hashedMasterKey).decode()
                    decryptedPhone = self.encryptDecrypt(row[0][7], False, oldKey=oldMasterkey, hashedKey=hashedMasterKey).decode()
                    self.updateLogin(decryptedPassword, decryptedEmail, decryptedPhone, idNumber)

        if lastNoteId:
            countOfRow = lastNoteId[0][0]
            for idNumber in range(1, countOfRow + 1):
                self.cur.execute("SELECT * FROM notes WHERE id=?", (idNumber,))
                row = self.cur.fetchall()
                if row:
                    decryptedTitle = self.encryptDecrypt(row[0][2], False, oldKey=oldMasterkey, hashedKey=hashedMasterKey).decode()
                    decryptedText = self.encryptDecrypt(row[0][3], False, oldKey=oldMasterkey, hashedKey=hashedMasterKey).decode()
                    self.addNote(decryptedTitle, decryptedText, idNumber=idNumber)

    # Encrypt and decrypt the data
    def encryptDecrypt(self, password, encrypt, oldKey=None, hashedKey=None):
        def hashPassword(psw):
            # salt for hashing
            salt = b'\'xd5\x16\xbe\x97o\xe7z)\xed=a~Kn\xbeF\xe1\xc8\xd5+\x9d1iL3R\xac/I\x94\xb1\xa9'
            key = PBKDF2HMAC(algorithm=hashes.MD5(), salt=salt, iterations=1000, backend=default_backend(), length=32)
            return base64.urlsafe_b64encode(key.derive(psw.encode()))

        def hashMasterKey(psw):
            # salt for hashing
            salt = b'\x9a\x10\xa4\x8b\xc3y\xa0\xdcy\xd2\xe1\x8a?pu\x81\xab\xce\xf7\x8e\xc7A\xb8\\fC\x06=\x97\xa5(P'
            key = PBKDF2HMAC(algorithm=hashes.SHA1(), salt=salt, iterations=10000, backend=default_backend(), length=32)
            return base64.urlsafe_b64encode(key.derive(psw.encode()))

        with open("key.txt", "r") as file:
            hashList = file.read().split("<<!>>")
            for i in range(len(hashList)):
                if i == 73:
                    masterkey = hashList[73]
        key1 = Fernet(hashPassword(self.masterkey)) if oldKey == None else Fernet(hashPassword(oldKey))
        key2 = Fernet(masterkey.encode()) if hashedKey == None else Fernet(hashedKey.encode())
        key3 = Fernet(b'BhhyjjUPSBoJ1XUWLvrhr8M7CWM02Q5KqFVrB-spzNg=')
        multiFernet = MultiFernet([key1, key2, key3])
        if encrypt:
            ecnryptedPassword = multiFernet.encrypt(password.encode())
        else:
            ecnryptedPassword = multiFernet.decrypt(password.encode())

        return ecnryptedPassword
