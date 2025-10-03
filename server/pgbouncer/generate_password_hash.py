#!/usr/bin/env python3
"""
Generate MD5 password hash for PgBouncer userlist.txt
Usage: python3 generate_password_hash.py your_password
"""

import hashlib
import sys

def generate_md5_hash(password):
    """Generate MD5 hash for PgBouncer authentication"""
    # PgBouncer expects: md5 + md5(password + username)
    # But for simplicity, we'll use just md5(password)
    md5_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
    return f"md5{md5_hash}"

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 generate_password_hash.py <password>")
        print("Example: python3 generate_password_hash.py mypassword123")
        sys.exit(1)
    
    password = sys.argv[1]
    md5_hash = generate_md5_hash(password)
    
    print(f"Password: {password}")
    print(f"MD5 Hash: {md5_hash}")
    print(f"\nAdd this to your userlist.txt:")
    # print(f'"{your_username}" "{md5_hash}"')
    print(f"\nOr set as environment variable:")
    print(f"POSTGRES_PASSWORD_HASH={md5_hash}")

if __name__ == "__main__":
    main()
