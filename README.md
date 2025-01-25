# DocuSign to Notion Archive Extension

A lightweight integration that archives DocuSign envelopes to Notion. When documents are signed in DocuSign, this extension creates entries in a Notion database with document metadata and direct links to view the documents.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/docusign-notion-archive.git
cd docusign-notion-archive
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
flask run
```

## Local Development with ngrok

1. Install ngrok:

```bash
# Using npm
npm install ngrok -g

# Or download from ngrok.com
```

2. Start your Flask app:

```bash
flask run
```

3. In a new terminal, start ngrok:

```bash
ngrok http 3000
```

4. Copy your ngrok URL (e.g., `https://1234-your-ngrok-url.ngrok-free.app`)

5. Update your environment variables:

```env
NOTION_REDIRECT_URI=https://your-ngrok-url/api/oauth/notion/callback
```

6. Update your DocuSign extension settings with the new ngrok URL

Note: Your ngrok URL will change each time you restart ngrok unless you have a paid account. You'll need to update your environment variables and DocuSign settings with the new URL each time.

## Features

- OAuth authentication with DocuSign and Notion
- Automatic database creation in Notion
- Document metadata archival
- Direct DocuSign viewer links
- Environment-aware configuration

## Environment Setup

1. Copy the template environment file:

```bash
cp env.template .env
```

2. Update `.env` with your credentials:

```env
# OAuth (Notion)
OAUTH_CLIENT_ID=           # From your Notion integration
OAUTH_CLIENT_SECRET=       # From your Notion integration

# Security
JWT_SECRET_KEY=           # Generate a secure random key
AUTHORIZATION_CODE=       # Generate a secure random code

# Redirect URIs
NOTION_REDIRECT_URI=      # Your ngrok URL + /api/oauth/notion/callback

# Database
DATABASE_URL=             # Your database connection string

# Supabase
SUPABASE_URL=            # From your Supabase project
SUPABASE_KEY=            # From your Supabase project
SUPABASE_DATABASE_PASSWORD= # From your Supabase project

# DocuSign
DOCUSIGN_URL_BASE=apps-d.docusign.com  # Use apps.docusign.com for production
```

You can generate secure keys using:

```bash
# For JWT_SECRET_KEY and AUTHORIZATION_CODE
openssl rand -hex 64
```

## Prerequisites

### 1. Notion Setup

1. Go to [Notion Developers](https://developers.notion.com/)
2. Click "View my integrations"
3. Create a "New integration"
4. Copy your OAuth client ID and secret
5. Duplicate this template database: [DocuSign Contract Archive Template](https://www.notion.so/lunchpaillabs/1834768cac2d8040a7abc8d1c3337291?v=1834768cac2d804ea6fb000cee84fa42)

### 2. DocuSign Setup

1. Go to [DocuSign Developer Center](https://developers.docusign.com/)
2. Create a new application
3. Under "Extensions", add a new extension:
   - Type: File Archive Extension
   - Authentication: OAuth
   - Add redirect URI: `https://your-domain/api/oauth/callback`
4. Copy your integration key (client ID) and secret

## DocuSign Extension Setup

1. **Create the Extension**

   - Log in to DocuSign Developer Console
   - Select "+New App"
   - Fill out the file archive extension form
   - Fill out the OAuth form with the relevant details
   - Validate and Create App

2. **Test the Extension**
   - Run integration tests (connections and extensions)
   - Test with sample workflows
   - Preview in App Center

## Usage

1. Install the extension in DocuSign
2. Connect your Notion workspace
3. Configure a workflow in DocuSign:
   - Add "Archive to Notion" action
   - Select your Notion connection
4. When documents are signed, they'll appear in your Notion database

## Development Notes

- Use `apps-d.docusign.com` for development
- Switch to `apps.docusign.com` for production
- Test with ngrok for local development
- Database is created from template on first use
