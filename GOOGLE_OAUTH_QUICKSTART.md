
# Google OAuth - Quick Start

## The 503 Error You're Seeing

The `503 Service Unavailable` error on `/auth/login/google` happens because Google OAuth credentials are not configured. The application needs `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` environment variables to work.

## Quick Setup (5 minutes)

### 1. Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project (or select existing)
3. Click **"+ Create Credentials"** → **"OAuth client ID"**
4. Choose **"Web application"**
5. Add authorized redirect URI:
   ```
   http://127.0.0.1:8000/auth/callback/google
   ```
6. Click **Create** and copy your:
   - Client ID
   - Client Secret

### 2. Configure Environment Variables

#### Option A: Use Setup Script (Recommended)

**Windows (PowerShell):**
```powershell
.\setup_google_oauth.ps1
```

**Linux/Mac:**
```bash
chmod +x setup_google_oauth.sh
./setup_google_oauth.sh
```

#### Option B: Manual Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```env
   GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your_client_secret_here
   OAUTH_REDIRECT_URI=http://127.0.0.1:8000/auth/callback/google
   
   # Also set a JWT secret (generate random string)
   JWT_SECRET=your_random_secret_key_here
   ```

### 3. Restart the Server

```bash
python main.py
```

### 4. Test Google Login

1. Open `http://127.0.0.1:8000/auth/login`
2. Click **"Sign in with Google"**
3. You should be redirected to Google's login page
4. After signing in, you'll be redirected back with authentication

## How It Works

```
User clicks "Sign in with Google"
         ↓
    /auth/login/google (redirects to Google)
         ↓
    Google Login Page
         ↓
    /auth/callback/google (handles response)
         ↓
    Creates/finds user → Issues JWT tokens → Redirects to app
```

## Current Features

✅ **Working Features:**
- Email/password registration
- Email/password login  
- Google OAuth login (when configured)
- JWT token-based authentication
- Email validation
- Protected routes

⏳ **To Be Configured:**
- Apple Sign-In (requires Apple Developer account)
- Email verification (requires SMTP setup)
- Password reset (requires SMTP setup)

## Troubleshooting

### Still getting 503 error?

Check these:

1. **Environment variables loaded?**
   ```python
   import os
   print(os.getenv('GOOGLE_CLIENT_ID'))  # Should not be None
   ```

2. **Restart after adding .env:**
   - The server must be restarted to load new environment variables

3. **Check logs:**
   ```bash
   python main.py
   ```
   Look for OAuth initialization messages

### Redirect URI mismatch?

Make sure the redirect URI in Google Cloud Console **exactly matches**:
```
http://127.0.0.1:8000/auth/callback/google
```

Common mistakes:
- Using `localhost` instead of `127.0.0.1`
- Missing `/auth/callback/google` path
- Using `https` instead of `http` (for local development)

## Need More Help?

See the detailed guide: **[GOOGLE_OAUTH_SETUP.md](./GOOGLE_OAUTH_SETUP.md)**

It includes:
- Step-by-step screenshots
- OAuth consent screen configuration
- Production deployment guide
- Security best practices
- Common errors and solutions
