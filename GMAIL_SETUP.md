# Gmail SMTP Setup Guide

## Problem
Gmail error: `Username and Password not accepted` (Error 535)

## Solution: Use App Password

### Step-by-Step Instructions

#### 1️⃣ Enable 2-Factor Authentication
1. Go to: https://myaccount.google.com/security
2. Click on **2-Step Verification**
3. Follow the prompts to enable it (if not already enabled)

#### 2️⃣ Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
   - Or search "App passwords" in Google Account settings
2. Select app: **Mail**
3. Select device: **Other (Custom name)**
4. Enter name: `TalkEasy Voice Assistant`
5. Click **Generate**
6. **Copy the 16-character password** (format: `xxxx xxxx xxxx xxxx`)
   - ⚠️ Remove spaces when pasting into .env file

#### 3️⃣ Update Your .env File
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=abcdefghijklmnop  # ⚠️ Use App Password here (no spaces)
SMTP_FROM=your-email@gmail.com
```

#### 4️⃣ Restart Your Application
After updating the .env file, restart your FastAPI server:
```powershell
# Stop the current server (Ctrl+C)
# Then restart
python main.py
```

## Alternative Email Providers

If you don't want to use Gmail, here are alternatives:

### Outlook/Hotmail
```env
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=your-email@outlook.com
SMTP_PASS=your-password
```

### SendGrid (Recommended for production)
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=your-sendgrid-api-key
```

### Mailgun
```env
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=your-mailgun-username
SMTP_PASS=your-mailgun-password
```

## Testing

After configuration, test the email service by triggering a password reset or registration email from your app.

## Troubleshooting

### Still getting authentication errors?
- ✅ Verify 2FA is enabled
- ✅ Make sure you're using the App Password, not your Gmail password
- ✅ Remove any spaces from the App Password
- ✅ Check that SMTP_USER matches your Gmail address
- ✅ Restart your application after changing .env

### App Password option not available?
- Your Google Workspace admin might have disabled this feature
- Contact your admin or use a personal Gmail account

### Emails not sending?
- Check your spam folder
- Verify the recipient email is valid
- Check application logs for detailed error messages
