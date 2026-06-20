# Product2Shopify AI Deployment Guide 🚀

This guide explains how to deploy **Product2Shopify AI** using a hybrid model:
1. **Application Backend:** Run the Streamlit app on **Streamlit Community Cloud** (free, supports Python long-running servers, SQlite database, and scraping engines).
2. **SEO & Domain Gateway:** Serve the static files from your **Hostinger Shared Hosting** account under the domain `ecomtool.online` (provides instant loading speeds, security controls, and global SEO crawlability).

---

## Part 1: Deploy the Streamlit Application (Backend)

Streamlit Community Cloud is a free hosting platform managed by Streamlit (Snowflake) that runs your Python files natively.

### Step 1: Push your Code to GitHub
1. Log in to [GitHub](https://github.com/) (create an account if you don't have one).
2. Create a new repository named `product2shopify` (can be public or private).
3. Push your codebase to this GitHub repository. Ensure your files (`app.py`, `requirements.txt`, `pages/`, `services/`, `database/`, `.streamlit/`) are in the root directory.
   > *Note: Do not commit your local `.env` or `product2shopify.db` database to public repositories to keep keys and data safe. A new SQLite database will automatically be generated on the cloud server.*

### Step 2: Deploy on Streamlit Community Cloud
1. Visit [Streamlit Share](https://share.streamlit.io/) and log in with your GitHub account.
2. Click **Create app** (top-right corner).
3. Fill in the deployment details:
   - **Repository:** Choose your `product2shopify` repository.
   - **Branch:** `main` (or your active branch).
   - **Main file path:** `app.py`.
   - **App URL:** Customize the subdomain prefix if desired (e.g., `ecomtool-online`).
4. Click **Deploy!**
5. Streamlit will install the dependencies from `requirements.txt` and boot the server. This may take 2-4 minutes on the first run.

### Step 3: Copy Your App Embed URL
1. Once the application loads successfully on Streamlit Cloud, copy the URL from the browser address bar (e.g., `https://ecomtool-online.streamlit.app/`).
2. To embed the app cleanly (without Streamlit's menus, headers, or watermarks), append `?embed=true` to the URL:
   `https://ecomtool-online.streamlit.app/?embed=true`

---

## Part 2: Deploy to Hostinger Shared Hosting (Frontend & SEO)

Now we will configure the static files in the `hostinger_deploy/` directory to serve as the gateway on your domain `ecomtool.online`.

### Step 1: Update Iframe Link
1. Open [index.html](file:///c:/Users/Mr%20Professor/Desktop/shopify/hostinger_deploy/index.html) in a text editor.
2. Search for the `<iframe>` tag (around line 324).
3. Replace the `src` attribute with your actual Streamlit Cloud URL (with `?embed=true` appended):
   ```html
   <iframe src="https://YOUR-APP-SUBDOMAIN.streamlit.app/?embed=true" allow="clipboard-write"></iframe>
   ```
4. Save the file.

### Step 2: Upload Files to Hostinger File Manager
1. Log in to your **Hostinger hPanel** (https://hpanel.hostinger.com).
2. Go to **Websites** and click **Manage** next to `ecomtool.online`.
3. Open the **File Manager** (under the "Files" section).
4. Navigate into the **`public_html`** folder. (Delete default placeholder files like `default.php` if present).
5. Upload the following files from your local `hostinger_deploy/` folder directly into `public_html`:
   - `index.html`
   - `privacy.html`
   - `terms.html`
   - `sitemap.xml`
   - `robots.txt`
   - `.htaccess`
   *(Ensure `.htaccess` starts with a dot so the Apache server reads it as a configuration file).*

### Step 3: Enable SSL on Hostinger
1. In hPanel, go to **Security** > **SSL**.
2. Select `ecomtool.online` and click **Install SSL** (Hostinger provides free lifetime SSL certificates).
3. The `.htaccess` file you uploaded will automatically redirect all visitors from insecure `http://` to secure `https://ecomtool.online`.

---

## Part 3: Verify Global SEO Setup

To ensure search engines can index your site for maximum global reach:

1. **Google Search Console:** 
   - Go to [Google Search Console](https://search.google.com/search-console).
   - Add your property: `https://ecomtool.online/`.
   - Submit your sitemap by going to **Sitemaps** and typing `sitemap.xml`.
2. **Meta Auditing:**
   - The static HTML files contain complete structured **JSON-LD Schema Markup** and **Meta Tags** describing the e-commerce helper application, enabling Google search engines to render premium rich result cards for searchers.
