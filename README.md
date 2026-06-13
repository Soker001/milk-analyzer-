# 🐄 DairyDash — Milk Analyzer & Smart Pricing System

A full-stack web application for dairy cooperatives to manage farmers, analyze milk quality, detect adulteration, and calculate smart pricing based on state-wise formulas.

## 🚀 Features

- **Farmer Management** — Add, view, search, and delete farmer records
- **Milk Quality Analysis** — Analyze Fat %, SNF %, Protein, Lactose, Temperature
- **Adulteration Detection** — Detect Water, Urea, Starch, Detergent, Salt contamination
- **Smart Pricing** — State-wise pricing formulas (7 Indian states supported)
- **Payment Processing** — Calculate and record farmer payments
- **MongoDB Database** — All data persisted to MongoDB Atlas

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, JavaScript |
| Backend | Node.js, Express.js |
| Database | MongoDB (Mongoose ODM) |
| Pricing Engine | Python |
| Android App | Kotlin (Android SDK) |

## 📦 Project Structure

```
pdd/
├── config/
│   └── db.js                 # MongoDB connection
├── models/
│   ├── Farmer.js             # Farmer schema
│   ├── QualityRecord.js      # Quality analysis schema
│   └── Payment.js            # Payment transaction schema
├── public/
│   ├── css/style.css          # Dashboard styles
│   ├── js/app.js              # Frontend logic
│   └── index.html             # Main dashboard
├── app/                       # Android app (Kotlin)
├── server.js                  # Express server
├── pricing_engine.py          # Python pricing calculator
├── package.json
├── .env.example               # Environment variables template
└── .gitignore
```

## ⚡ Quick Start

### Prerequisites
- [Node.js](https://nodejs.org/) (v16+)
- [Python](https://python.org/) (v3.8+)
- [MongoDB Atlas](https://cloud.mongodb.com/) account (free tier)

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/dairydash.git
cd dairydash
npm install
```

### 2. Configure MongoDB

```bash
# Copy environment template
cp .env.example .env
```

Edit `.env` with your MongoDB Atlas connection string:
```
MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/dairydash?retryWrites=true&w=majority
PORT=3000
```

**How to get MongoDB URI:**
1. Go to [MongoDB Atlas](https://cloud.mongodb.com/) → Create free cluster
2. Database Access → Add a user with password
3. Network Access → Allow `0.0.0.0/0` (or your IP)
4. Connect → Drivers → Copy connection string

### 3. Run

```bash
npm start
```

Open **http://localhost:3000** in your browser.

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/farmers` | List all farmers |
| `POST` | `/api/farmers` | Add a farmer |
| `DELETE` | `/api/farmers/:id` | Delete a farmer |
| `GET` | `/api/quality` | List quality records |
| `POST` | `/api/quality` | Save quality analysis |
| `GET` | `/api/payments` | List all payments |
| `POST` | `/api/payments` | Save a payment |
| `GET` | `/api/payments/farmer/:id` | Payment history |
| `POST` | `/api/calculate-price` | Calculate pricing |
| `GET` | `/api/status` | Database status |

## 💰 Pricing Formulas (State-wise)

| State | Formula |
|-------|---------|
| Tamil Nadu | `(Fat × 7) + (SNF × 3)` |
| Kerala | `(Fat × 6.8) + (SNF × 3.2)` |
| Karnataka | `30 + FatIncentive + 5` |
| Gujarat | `(Fat × 6.5) + (SNF × 4)` |
| Maharashtra | `Fat × 8` |
| Punjab | `(Fat × 7.5) + (SNF × 2.5)` |
| Haryana | `(Fat × 7.2) + (SNF × 2.8)` |

Final Price = Base Price × (Quality Score / 100)

## 📱 Android App

The Android app is located in the `app/` directory. Build the APK:

```bash
cd app
./gradlew assembleDebug
```

APK will be at: `app/build/outputs/apk/debug/app-debug.apk`

## 📄 License

MIT
