# HCA - Basketball Court Reservation System (TON)

🏀 **Hoops Court Arena** – A decentralized basketball court booking application with TON Wallet integration. Reserve your court, join matches, and manage your basketball playing profile.

## 🎯 Features

- **TON Wallet Authentication**: Secure login using TON blockchain wallet
- **Court Reservations**: Book basketball courts with crowdfunding support
- **Player Profiles**: Create and manage player profiles with skill levels and positions
- **Match Management**: Create matches, join games, and track player participation
- **Real-time Updates**: Async API using FastAPI with WebSocket support
- **Telegram Bot Integration**: Quick access via Telegram bot interface

## 📁 Project Structure

```
hca/
├── basket_bot_backend/          # Python FastAPI backend
│   ├── main.py                  # Core API endpoints
│   ├── models.py                # SQLAlchemy database models
│   ├── database.py              # Database configuration
│   ├── auth.py                  # TON wallet authentication
│   ├── requirements.txt          # Python dependencies
│   └── .env.example              # Environment variables template
├── basket_bot_frontend/         # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx              # Main React component
│   │   ├── main.jsx             # Application entry point
│   │   └── index.css            # Tailwind CSS styles
│   ├── package.json             # Node.js dependencies
│   └── vite.config.js           # Vite bundler configuration
├── README.md                    # This file
├── ARCHITECTURE.md              # Detailed system architecture
└── Procfile                     # Railway deployment configuration
```

## 🚀 Quick Start

### Prerequisites

- **Backend**: Python 3.10+, PostgreSQL (or SQLite for local dev)
- **Frontend**: Node.js 18+, npm
- **Telegram**: Bot token from BotFather
- **TON**: Wallet for testing (testnet)

### Backend Setup

1. **Clone and navigate**:
   ```bash
   git clone https://github.com/nikolalov3/hca.git
   cd hca/basket_bot_backend
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration:
   # DATABASE_URL=postgresql+asyncpg://...
   # BOT_TOKEN=your_telegram_bot_token
   # SECRET_KEY=your_secret_key
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server**:
   ```bash
   python main.py
   # API available at http://localhost:8000
   # Docs at http://localhost:8000/docs
   ```

### Frontend Setup

1. **Navigate to frontend**:
   ```bash
   cd ../basket_bot_frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Create environment file**:
   ```bash
   cat > .env.local << EOF
   VITE_API_URL=http://localhost:8000
   VITE_TELEGRAM_BOT_URL=https://t.me/your_bot_name
   EOF
   ```

4. **Start dev server**:
   ```bash
   npm run dev
   # App available at http://localhost:5173
   ```

## 🔗 API Endpoints

### Authentication
- `POST /api/auth/login` - Login with TON wallet signature
- `GET /api/auth/me` - Get current user (requires auth)

### Profile
- `GET /api/profile/me` - Get current player profile
- `POST /api/profile/me` - Update player profile
- `GET /api/profile/{telegram_id}` - Get player by Telegram ID

### Matches
- `GET /api/matches` - List all active matches
- `POST /api/matches` - Create new match
- `GET /api/matches-list` - Get detailed match information
- `POST /api/matches/{match_id}/join` - Join a match

## 🛠️ Technology Stack

**Backend**:
- FastAPI – Modern Python web framework
- SQLAlchemy – ORM for database
- PostgreSQL/SQLite – Data persistence
- Telegram.ext – Bot framework

**Frontend**:
- React 18 – UI library
- Vite – Build tool
- Tailwind CSS – Styling
- Axios – HTTP client (via fetch wrapper)
- TonConnect UI – TON wallet integration

**Deployment**:
- Railway – Backend hosting
- Vercel – Frontend hosting

## 📝 Environment Variables

See `.env.example` for complete list. Key variables:

```
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
BOT_TOKEN=your_telegram_bot_token
SECRET_KEY=your_jwt_secret
WEBAPP_URL=https://your-app.vercel.app
```

## 🔐 Security

- JWT token-based authentication
- TON wallet signature verification
- CORS protection
- Environment variables for sensitive data
- Async session handling

## 📚 Documentation

- **Architecture**: See `ARCHITECTURE.md` for system design
- **API Docs**: Available at `/docs` (Swagger UI)
- **Profile Format**: See `models.py` for database schema

## 🐛 Known Issues

- TON signature verification is currently stubbed (integration pending)
- WebSocket support coming in v2.0
- Rate limiting not yet implemented

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 📧 Contact

For questions or support, reach out via:
- GitHub Issues: [Create an issue](https://github.com/nikolalov3/hca/issues)
- Telegram: [@nikolalov3](https://t.me/nikolalov3)

---

**Made with ❤️ for basketball lovers and blockchain enthusiasts**
