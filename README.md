### 📄 `README.md`

# 🗓️ Parents Days Calendar Automation (Google Calendar API)

This Python script adds **Mother's Day** (2nd Sunday in May) and **Father's Day** (3rd Sunday in June) to your **Google Calendar** for the next 100 years, and colours them **yellow** for easy identification.

You can also optionally remove old versions that were added without colour.

---

## ✨ Features

- Adds Mother's Day and Father's Day from **2025 to 2125**
- Marks them as **all-day** events
- Assigns **yellow colour** (`colorId = 5`)
- Optional cleanup script to remove previous uncoloured duplicates

---

## 🔐 Requirements

- Python 3.6+
- Google Cloud Project with Calendar API enabled
- OAuth 2.0 credentials for **Desktop App**

---

## 📦 Installation

### 1. Clone this repository

```bash
git clone https://github.com/yourusername/parents-days-calendar.git
cd parents-days-calendar
````

### 2. Install dependencies

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

---

## 🔑 Setup Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable **Google Calendar API**
3. Create **OAuth 2.0 Client ID** → Choose **Desktop App**
4. Download the `client_secret_XXXXX.json` file
5. Rename it to:

```
credentials.json
```

6. Place it in the project root

---

## 🚀 Running the Script

### Add Yellow-Coloured Events

```bash
python add_parents_days_api.py
```

This will prompt a browser window to authenticate and grant calendar access. It will create a `token.json` to store your credentials for next time.

---

### 🧽 Optional: Remove Uncoloured Duplicates

If you previously ran a version that added uncoloured events, use this cleanup script:

```bash
python remove_non_yellow_parents_days.py
```

---

## 🔒 Security

Be sure to **exclude sensitive files**:

* `.gitignore` includes `credentials.json` and `token.json`
* Do **not** share your credentials file

---

## 📁 Project Structure

```
📁 parents-days-calendar/
├── add_parents_days_api.py           # Adds Mother's and Father's Day (yellow)
├── remove_non_yellow_parents_days.py # Cleans up uncoloured duplicates
├── credentials.json                  # Your OAuth credentials (DO NOT COMMIT)
├── token.json                        # Auth token (auto-generated)
├── .gitignore
└── README.md
```

---

## 🧠 Notes

* Yellow in Google Calendar corresponds to `colorId: "5"`
* For a full list of supported colours, see [Calendar Colors API](https://developers.google.com/calendar/api/v3/reference/colors)

---

## 📬 License

MIT License

---

## 🤝 Author

Built with ❤️ by Roscoe at [ROSCODETECH](https://roscodetech.com)




