try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    print("google-auth-oauthlib is installed.")
except ImportError:
    print("google-auth-oauthlib is not installed.")

try:
    from googleapiclient.discovery import build
    print("google-api-python-client is installed.")
except ImportError:
    print("google-api-python-client is not installed.")
