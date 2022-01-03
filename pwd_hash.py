import bcrypt

def validate_pass(passwd, pdb):
    _hashed = str(pdb)
    if bcrypt.checkpw(passwd.encode('utf-8'), _hashed.encode('utf-8')):
        return "sukses"
    else:
        return "salah"
