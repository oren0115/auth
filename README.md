# Authentication Service

Layanan autentikasi modular dan scalable berbasis FastAPI, MySQL, dan Prisma.

## Fitur

- ✅ Registrasi & Login (email/username + password)
- ✅ Google OAuth 2.0
- ✅ Reset Password via Email
- ✅ JWT Access & Refresh Tokens
- ✅ Rate Limiting
- ✅ CORS Support
- ✅ Arsitektur Modular

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: MySQL
- **ORM**: Prisma (prisma-client-py)
- **Authentication**: JWT (Access + Refresh tokens)
- **OAuth**: Google OAuth 2.0
- **Password Hashing**: bcrypt
- **Email**: SMTP (Zoho Mail)
- **Rate Limiting**: slowapi

## Struktur Project

```
be/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── config/                 # Konfigurasi
│   │   ├── env.py             # Environment settings
│   │   ├── database.py        # Database connection
│   │   ├── security.py        # JWT & hashing
│   │   └── email.py           # Email configuration
│   ├── modules/
│   │   └── auth/              # Authentication module
│   │       ├── auth.router.py # API routes
│   │       ├── auth.service.py# Business logic
│   │       ├── auth.schema.py # Pydantic models
│   │       ├── auth.repository.py # Data access
│   │       ├── auth.utils.py  # Helper functions
│   │       └── oauth/
│   │           └── google.py  # Google OAuth
│   ├── common/                 # Shared utilities
│   │   ├── exceptions.py      # Custom exceptions
│   │   ├── response.py        # Response models
│   │   └── dependencies.py    # FastAPI dependencies
│   └── prisma/
│       └── schema.prisma      # Prisma schema
├── requirements.txt
├── env.example                # Template environment variables
├── run.py                     # Script untuk menjalankan aplikasi
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Konfigurasi Environment

Copy `env.example` ke `.env` di root directory dan isi konfigurasi:

```bash
cp env.example .env
```

**Catatan Penting untuk Zoho Mail**: Gunakan **App Password** (bukan password biasa) untuk `SMTP_PASSWORD`. Generate di: Zoho Mail → Settings → Security → App Passwords

### 3. Setup Database

```bash
cd app
prisma generate
prisma db push
```

Atau gunakan migrations:

```bash
cd app
prisma migrate dev --name init
```

### 4. Jalankan Aplikasi

```bash
# Dari root directory
python run.py
```

Atau dengan uvicorn langsung:

```bash
python -m uvicorn app.main:app --reload
```

API tersedia di `http://localhost:8000`  
Dokumentasi API: `http://localhost:8000/docs`

## API Endpoints

### Authentication

- `POST /auth/register` - Registrasi user baru
- `POST /auth/login` - Login dengan email/username + password
- `POST /auth/google` - Login/Registrasi dengan Google OAuth
- `POST /auth/reset/request` - Request reset password
- `POST /auth/reset/confirm` - Konfirmasi reset password
- `POST /auth/refresh` - Refresh access token

### Contoh Request

**Register**
```json
POST /auth/register
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Login**
```json
POST /auth/login
{
  "identifier": "user@example.com",
  "password": "securepassword123"
}
```

**Google OAuth**
```json
POST /auth/google
{
  "id_token": "google-id-token-here"
}
```

**Request Password Reset**
```json
POST /auth/reset/request
{
  "email": "user@example.com"
}
```

**Confirm Password Reset**
```json
POST /auth/reset/confirm
{
  "token": "reset-token-from-email",
  "new_password": "newsecurepassword123"
}
```

**Refresh Token**
```json
POST /auth/refresh
{
  "refresh_token": "refresh-token-here"
}
```

## Security Features

- Password hashing dengan bcrypt
- JWT tokens dengan expiration (15 menit access, 7 hari refresh)
- Refresh token rotation
- One-time use reset tokens
- Rate limiting (5/min untuk register/login, 3/min untuk reset)
- User enumeration prevention
- OAuth token verification server-side

## Development

### Database Migrations

```bash
cd app
prisma migrate dev --name migration_name
```

## License

MIT
