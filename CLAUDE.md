# 🔑 Reddit API Setup Guide

## Quick Setup (5 minutes)

### Step 1: Create Reddit App

1. **Log in to Reddit** at https://www.reddit.com/
2. **Go to Reddit Apps**: https://www.reddit.com/prefs/apps
3. **Scroll down** and click **"create another app..."**

### Step 2: Fill Out App Info

- **Name**: `ContentBot` (or anything you want)
- **App type**: Select **"script"** (very important!)
- **Description**: `Automated content bot` (optional)
- **About URL**: Leave blank
- **Redirect URI**: `http://localhost:8080` (required but not used)

Click **"Create app"**

### Step 3: Get Your Credentials

After creating, you'll see:

```
ContentBot
personal use script
[CLIENT_ID is here - looks like: dj3F8sD_fj23fjSD]

secret: [CLIENT_SECRET is here - longer string]
```

- **CLIENT_ID**: The short string under your app name (14 characters)
- **CLIENT_SECRET**: The longer string next to "secret:" (27+ characters)

### Step 4: Add to .env File

Open your `.env` file and update these lines:

```bash
# Reddit API
REDDIT_CLIENT_ID=your_client_id_here      # Replace with your CLIENT_ID
REDDIT_CLIENT_SECRET=your_secret_here     # Replace with your CLIENT_SECRET
REDDIT_USER_AGENT=ContentBot/1.0          # Leave as is
```

**Example:**
```bash
REDDIT_CLIENT_ID=dj3F8sD_fj23fjSD
REDDIT_CLIENT_SECRET=fjSDf93jfSDjf93jfSD93jfSD
REDDIT_USER_AGENT=ContentBot/1.0
```

### Step 5: Test Connection

Run this to test your credentials:

```bash
python -m src.scrapers.reddit_scraper
```

You should see:
```
✅ Connected to Reddit API
📊 Top 5 posts by viral score:
...
```

---

## ✅ You're Done!

Now you can:

- **Scrape Reddit posts automatically**
- **Generate videos from real stories**
- **No more manual story writing**

---

## 🔧 Troubleshooting

### "Invalid credentials"
- Double-check your CLIENT_ID and CLIENT_SECRET
- Make sure there are no extra spaces
- Verify you selected "script" type (not "web app")

### "User agent required"
- Make sure REDDIT_USER_AGENT is set in .env
- Default: `ContentBot/1.0`

### "Rate limited"
- Reddit limits API calls
- Wait a few minutes and try again
- Don't make too many requests too quickly

---

## 📊 What Can You Scrape?

Default subreddits (best for viral content):
- r/AmItheAsshole
- r/relationship_advice
- r/entitledparents
- r/maliciouscompliance
- r/pettyrevenge
- r/tifu (Today I F'd Up)
- r/confession

All of these have **proven viral potential** and are **legal to use** (public Reddit text).

---

## 🚀 Next Steps

After setup, you can:

1. **Generate video from Reddit**:
   ```bash
   python create_video.py --reddit aita
   ```

2. **Scrape and preview posts**:
   ```bash
   python -m src.scrapers.reddit_scraper
   ```

3. **Batch generate 10 videos**:
   ```bash
   python batch_generate.py --count 10
   ```

---

## ⚠️ Reddit API Rules

**DO:**
- ✅ Use for content creation
- ✅ Respect rate limits
- ✅ Give credit to Reddit in video descriptions

**DON'T:**
- ❌ Spam or bot behavior
- ❌ Excessive API calls
- ❌ Vote manipulation
- ❌ Violate Reddit's Terms of Service

**Our bot is compliant:** We fetch public text content for transformative use (videos), which is allowed under Reddit's API terms.

---

## 📚 More Info

- **Reddit API Docs**: https://www.reddit.com/dev/api/
- **PRAW Documentation**: https://praw.readthedocs.io/
- **Reddit API Rules**: https://github.com/reddit-archive/reddit/wiki/API
