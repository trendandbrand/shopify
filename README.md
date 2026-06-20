# Product2Shopify AI 🛍️🤖

Product2Shopify AI is a complete web application built with Streamlit, Python, and SQLAlchemy (supporting PostgreSQL and SQLite fallback). It extracts product details from URLs, cleans and rewrites titles/descriptions to avoid copyright violations, generates Shopify-compliant fields (SKUs, handles, tags, SEO metadata, prices), validates the data, and exports files ready for Shopify product imports.

---

## Features

1. **Dashboard:** Displays total products processed, export files generated, validation status details (missing images, missing prices, duplicate SKUs).
2. **Product Link Importer:** Pastes single or multiple URLs to scrape details using BeautifulSoup. Safely flags Amazon and other blocked sites for manual entry.
3. **Product Editor:** Provides detailed form editing for 30+ Shopify columns, plus a bulk spreadsheet grid editor. Features an **Auto-Rewrite** button.
4. **SKU Generator:** Automatically generates unique SKUs in `PREFIX-CATEGORY-COLOR-001` format. Prevents database duplicates.
5. **Price Calculator:** Models product cost, shipping cost, fees, markup %, and target profits. Applies calculations in bulk to database items.
6. **Tags & SEO Generator:** Generates handles, keyword tags, SEO titles (under 70 chars), and SEO descriptions (under 160 chars).
7. **Image Manager:** Displays gallery previews of URLs, validates HTTPS requirements, sets positions, and manages image alt tags.
8. **CSV Validator:** Scans and reports validation errors and warnings before exporting.
9. **Shopify CSV Exporter:** Generates Shopify import-ready CSVs (with sub-rows for multiple images) and Excel backups.
10. **Import History:** Log batches of export sheets and URL import extractions.

---

## Technology Stack

* **Frontend UI:** Streamlit
* **Database:** PostgreSQL (with automatic SQLAlchemy local SQLite fallback: `product2shopify.db`)
* **Libraries:** Pandas, SQLAlchemy, BeautifulSoup4, Requests, openpyxl, python-dotenv, psycopg2-binary

---

## Installation & Setup

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

### 2. Clone/Copy Project & Install Dependencies
Open your shell in the project folder and run:
```bash
pip install -r requirements.txt
```

### 3. Database Configurations
Copy the template `.env` or edit the existing `.env` file in the project root:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/product2shopify
```
* **PostgreSQL Setup:** If you have PostgreSQL running, create a database named `product2shopify`. The application will automatically connect and build tables.
* **SQLite Fallback:** If PostgreSQL is not running or port 5432 is blocked, the application will automatically create and connect to a local SQLite file named `product2shopify.db`. **No extra setup is required!**

---

## How to Run

Launch the application using Streamlit:
```bash
streamlit run app.py
```

---

## ⚠️ Safety & Copyright Warning

**IMPORTANT:** Do not blindly copy copyrighted Amazon or competitor content.
* Always check the **Auto-Rewrite** button in the Product Editor to convert raw titles and descriptions into unique, paraphrase-driven product descriptions.
* Ensure you use only images that you own, or those you are explicitly authorized to use by the manufacturer or supplier.

---

## Shopify Import Instructions

1. Generate your Shopify sheet using the **Shopify CSV Exporter** page.
2. Log in to your **Shopify Admin** panel.
3. Go to **Products** and click **Import** (top-right corner).
4. Add the generated CSV file.
5. Click **Upload and preview**, then click **Import products**.
"# shopify" 
