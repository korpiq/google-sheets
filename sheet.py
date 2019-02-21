import os
import sys
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


DEFAULT_CONF_DIR = os.path.join(os.environ['HOME'], '.google')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


AUTHORIZATION_GUIDANCE="""
Please download Google client configuration from ENABLE GOOGLE SHEETS API button
at https://developers.google.com/sheets/api/quickstart/python to "%s"
"""


USAGE="""
Usage: python3 sheet.py 'GOOGLE_SHEET_ID' [GOOGLE_SHEET_RANGE]
Outputs contents of specified range of specified Google spreadsheet.

Setup: ./setup.sh; source *-env/bin/activate

%s

First time usage opens browser with downloaded credentials to authorize. 
""" % (AUTHORIZATION_GUIDANCE % os.path.join(DEFAULT_CONF_DIR, 'credentials.json'))


def authorize(scopes=SCOPES, conf_dir=DEFAULT_CONF_DIR):
    """
    Expects Google `conf_dir/credentials.json` 
    """
    filename = os.path.join(conf_dir, 'credentials.json')

    try:
        flow = InstalledAppFlow.from_client_secrets_file(filename, scopes)
        return flow.run_local_server()
    except:
        sys.stderr.write(AUTHORIZATION_GUIDANCE % filename)
        os.makedirs(conf_dir, exist_ok=True) # help user ensure security while we are at it
        os.chmod(conf_dir, 0o700)
        sys.exit(1)


def get_credentials(scopes=SCOPES, conf_dir=DEFAULT_CONF_DIR):
    scopes = sorted(scopes)
    filepath = os.path.join(conf_dir, 'auth-token.pickle')
    scoped_credentials = None
    credentials = None

    try:
        with open(filepath, 'rb') as file_handle:
            scoped_credentials = pickle.load(file_handle)

        lacking_scopes = [elem for elem in scopes if elem not in scoped_credentials['scopes']]
        if lacking_scopes:
            raise('Stored auth token has different scopes: %s' % '; '.join(lacking_scopes))

        credentials = scoped_credentials['credentials']
        if not credentials.valid: raise('Invalid stored auth token')
    except Exception as e:

        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            sys.stderr.write("Authorization hickup: %s\n" % e)

            credentials = authorize(scopes, conf_dir)
            scoped_credentials = {
                'scopes': scopes,
                'credentials': credentials
            }

            with open(filepath, 'wb') as file_handle:
                pickle.dump(scoped_credentials, file_handle)

    return credentials


def get_sheet_data(sheet_id, range, credentials=None):
    service = build('sheets', 'v4', credentials=(credentials or get_credentials()))
    sheets = service.spreadsheets()
    result = sheets.values().get(spreadsheetId=sheet_id, range=range).execute()
    return result.get('values', [])


def main(sheet_id, range=None):
    if range is None:
        range='A1:ZZZ'
    for row in get_sheet_data(sheet_id, range):
        print(row)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(*sys.argv[1:])
    else:
        sys.stderr.write(USAGE)
        sys.exit(1)
