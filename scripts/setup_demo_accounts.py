"""Create a test administrator or activate/reset a test doctor/patient login.

Only run on a BACKUP of Phrase3 containing synthetic test data.
No existing medical records are modified.
"""
import argparse
import getpass
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from werkzeug.security import generate_password_hash
from db import get_connection


def main():
    parser = argparse.ArgumentParser(description='MediConnect demo account setup')
    parser.add_argument('--role', choices=['ADMIN','DOCTOR','PATIENT'], required=True)
    parser.add_argument('--username', help='Unique username for a newly created account')
    parser.add_argument('--profile-id', type=int, help='Required DoctorID or Patient ID for role DOCTOR/PATIENT')
    args = parser.parse_args()
    if args.role != 'ADMIN' and not args.profile_id:
        parser.error('DOCTOR/PATIENT require --profile-id')
    if args.role == 'ADMIN' and not args.username:
        parser.error('ADMIN requires --username')
    p1 = getpass.getpass('Password (>=8 characters): ')
    p2 = getpass.getpass('Confirm password: ')
    if len(p1) < 8 or p1 != p2:
        sys.exit('Password too short or mismatch; no changes made.')
    print('Warning: ONLY use this script on synthetic test data / a backup of Phrase3.')
    if input('Type YES to continue: ').strip() != 'YES':
        print('Cancelled.')
        return
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    locked = False
    try:
        cur.execute("SELECT GET_LOCK('MC_PHASE4_WRITE', 10) AS acquired")
        locked = bool(cur.fetchone()['acquired'])
        if not locked:
            raise RuntimeError('Could not acquire write lock')
        if args.role == 'ADMIN':
            cur.execute('SELECT UserID FROM USER_ACCOUNT WHERE Username=%s', (args.username,))
            if cur.fetchone():
                raise RuntimeError('Username already exists; choose a new one')
            cur.execute('SELECT COALESCE(MAX(UserID),0)+1 AS id FROM USER_ACCOUNT')
            uid = cur.fetchone()['id']
            cur.execute('INSERT INTO USER_ACCOUNT (UserID,Username,PasswordHash,Role) VALUES (%s,%s,%s,%s)',
                        (uid, args.username, generate_password_hash(p1), 'ADMIN'))
            result_username = args.username
        else:
            table = 'DOCTOR' if args.role == 'DOCTOR' else 'PATIENT'
            pk = 'DoctorID' if args.role == 'DOCTOR' else 'Patient'
            cur.execute(f'SELECT UserID FROM {table} WHERE {pk}=%s', (args.profile_id,))
            record = cur.fetchone()
            if not record:
                raise RuntimeError(f'{table} profile ID does not exist')
            if record['UserID'] is not None:
                uid = record['UserID']
                cur.execute('SELECT Username,Role FROM USER_ACCOUNT WHERE UserID=%s', (uid,))
                account = cur.fetchone()
                if not account or account['Role'] != args.role:
                    raise RuntimeError('Existing account is not of the requested role')
                if input(f'Reset password for existing {account["Username"]}? Type RESET: ').strip() != 'RESET':
                    raise RuntimeError('Reset cancelled')
                cur.execute('UPDATE USER_ACCOUNT SET PasswordHash=%s WHERE UserID=%s',
                            (generate_password_hash(p1), uid))
                result_username = account['Username']
            else:
                result_username = args.username or f'mc_demo_{args.role.lower()}_{args.profile_id}'
                cur.execute('SELECT UserID FROM USER_ACCOUNT WHERE Username=%s', (result_username,))
                if cur.fetchone():
                    raise RuntimeError('Username already exists')
                cur.execute('SELECT COALESCE(MAX(UserID),0)+1 AS id FROM USER_ACCOUNT')
                uid = cur.fetchone()['id']
                cur.execute('INSERT INTO USER_ACCOUNT (UserID,Username,PasswordHash,Role) VALUES (%s,%s,%s,%s)',
                            (uid,result_username,generate_password_hash(p1),args.role))
                cur.execute(f'UPDATE {table} SET UserID=%s WHERE {pk}=%s', (uid,args.profile_id))
        conn.commit()
        print('Success. Username:', result_username, '| role:', args.role)
    except Exception:
        conn.rollback()
        raise
    finally:
        if locked:
            try:
                cur.execute("SELECT RELEASE_LOCK('MC_PHASE4_WRITE')")
                cur.fetchone()
            except Exception:
                pass
        cur.close()
        conn.close()


if __name__ == '__main__':
    main()
