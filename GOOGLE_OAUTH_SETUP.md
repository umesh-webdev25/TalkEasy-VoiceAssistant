# Google OAuth Setup Guide

This guide will help you set up "Sign in with Google" for your TalkEasy Voice Assistant.

## Prerequisites

- A Google Account
- Access to Google Cloud Console

## Step-by-Step Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "TalkEasy Voice Assistant")
5. Click "Create"

### 2. Enable Google+ API

1. In the left sidebar, go to **APIs & Services** > **Library**
2. Search for "Google+ API" or "People API"
3. Click on it and click **Enable**

### 3. Configure OAuth Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**
2. Select **External** as user type (unless you have Google Workspace)
3. Click **Create**
4. Fill in the required information:
   - **App name**: TalkEasy Voice Assistant
   - **User support email**: Your email
   - **Developer contact information**: Your email
5. Click **Save and Continue**
6. On the Scopes page, click **Add or Remove Scopes**
7. Add these scopes:
   - `openid`
   - `email`
   - `profile`
8. Click **Save and Continue**
9. Add test users (your email addresses that will test the app)
10. Click **Save and Continue**
11. Review and click **Back to Dashboard**

### 4. Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **+ Create Credentials** at the top
3. Select **OAuth client ID**
4. Choose **Web application** as application type
5. Enter a name (e.g., "TalkEasy Web Client")
6. Under **Authorized JavaScript origins**, add:
   ```
   http://localhost:8000
   http://127.0.0.1:8000
   ```
7. Under **Authorized redirect URIs**, add:
   ```
   http://127.0.0.1:8000/auth/callback/google
   http://localhost:8000/auth/callback/google
   ```
8. Click **Create**
9. Copy the **Client ID** and **Client Secret** - you'll need these!

### 5. Configure Your Application

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Google OAuth credentials:
   ```env
   GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your_client_secret_here
   OAUTH_REDIRECT_URI=http://127.0.0.1:8000/auth/callback/google
   ```

3. Also configure JWT secret:
   ```env
   JWT_SECRET=generate_a_random_secret_key_here
   ```
   
   You can generate a secure secret with:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

### 6. Install Required Dependencies

Make sure `authlib` is installed:
```bash
pip install authlib
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 7. Start Your Application

```bash
python main.py
```

### 8. Test Google Login

1. Navigate to `http://127.0.0.1:8000`
2. Click on "Sign in with Google" button
3. You should be redirected to Google's login page
4. After signing in, you'll be redirected back to your app with authentication tokens

## Troubleshooting

### 503 Service Unavailable Error

**Problem**: `/auth/login/google` returns 503 error

**Solution**: 
- Make sure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set in your `.env` file
- Restart the application after adding environment variables

### Redirect URI Mismatch Error

**Problem**: Google shows "redirect_uri_mismatch" error

**Solution**:
- Ensure the redirect URI in Google Cloud Console matches exactly: `http://127.0.0.1:8000/auth/callback/google`
- Check that `OAUTH_REDIRECT_URI` in `.env` matches the one configured in Google Cloud Console

### OAuth Not Configured Error

**Problem**: Application shows "OAuth not configured"

**Solution**:
- Verify environment variables are loaded correctly
- Check that `.env` file is in the root directory
- Restart the application

### Access Blocked: This app's request is invalid

**Problem**: Google shows this error when trying to sign in

**Solution**:
- Make sure you've added your email as a test user in OAuth consent screen
- Verify all required scopes are added (openid, email, profile)

## Frontend Integration

To add a "Sign in with Google" button to your frontend:

```html
<a href="/auth/login/google" class="google-login-btn">
    <img src="https://developers.google.com/identity/images/g-logo.png" alt="Google">
    Sign in with Google
</a>
```

Or use a button:
```html
<button onclick="window.location.href='/auth/login/google'">
    Sign in with Google
</button>
```

## Security Notes

1. **Never commit your `.env` file** - it contains secrets!
2. **Use HTTPS in production** - OAuth should always use secure connections
3. **Change JWT_SECRET** - Use a strong, random secret key
4. **Rotate credentials** - Periodically update your OAuth credentials
5. **Limit scopes** - Only request the permissions you need

## Production Deployment

For production deployment:

1. Update redirect URIs in Google Cloud Console to use your production domain
2. Update `OAUTH_REDIRECT_URI` in production environment variables
3. Use HTTPS for all OAuth flows
4. Set OAuth consent screen to "In Production" status
5. Add your production domain to authorized JavaScript origins

Example production URIs:
```
Authorized JavaScript origins:
https://your-domain.com

Authorized redirect URIs:
https://your-domain.com/auth/callback/google
```

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Authlib Documentation](https://docs.authlib.org/)
- [Google Cloud Console](https://console.cloud.google.com/)
