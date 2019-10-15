
import hashlib
import random
import string

def make_salt(): # internal function
   return ''.join([random.choice(string.ascii_letters) for x in range(5)])

def make_pw_hash(password, salt=None): # called in main.py
    
   if not salt:
      salt = make_salt()
   hash = hashlib.sha256(str.encode(password + salt)).hexdigest() 
   return '{0},{1}'.format(hash, salt)

def check_pw_hash(password, hash): # called in main.py
   salt = hash.split(',')[1]   # get salt from database

   if make_pw_hash(password, salt) == hash:
      return True

   return False