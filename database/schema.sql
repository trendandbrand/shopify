-- PostgreSQL schema for Product2Shopify AI
-- Will also be used to initialize the SQLite database if PostgreSQL is not available

CREATE TABLE IF NOT EXISTS products_raw (
    id SERIAL PRIMARY KEY,
    source_url TEXT,
    raw_title TEXT,
    raw_price NUMERIC,
    raw_description TEXT,
    raw_images TEXT, -- stored as newline/comma separated text
    raw_vendor TEXT,
    extraction_status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS shopify_products (
    id SERIAL PRIMARY KEY,
    source_url TEXT,
    handle TEXT,
    title TEXT,
    body_html TEXT,
    vendor TEXT,
    product_category TEXT,
    product_type TEXT,
    tags TEXT,
    published TEXT DEFAULT 'true',
    option1_name TEXT,
    option1_value TEXT,
    option2_name TEXT,
    option2_value TEXT,
    option3_name TEXT,
    option3_value TEXT,
    variant_sku TEXT,
    variant_grams INTEGER DEFAULT 0,
    variant_inventory_tracker TEXT DEFAULT 'shopify',
    variant_inventory_qty INTEGER DEFAULT 1,
    variant_inventory_policy TEXT DEFAULT 'deny',
    variant_fulfillment_service TEXT DEFAULT 'manual',
    variant_price NUMERIC DEFAULT 0.00,
    variant_compare_at_price NUMERIC DEFAULT 0.00,
    variant_requires_shipping BOOLEAN DEFAULT TRUE,
    variant_taxable BOOLEAN DEFAULT TRUE,
    variant_barcode TEXT,
    image_src TEXT,
    image_position INTEGER,
    image_alt_text TEXT,
    gift_card TEXT DEFAULT 'false',
    seo_title TEXT,
    seo_description TEXT,
    google_shopping_category TEXT,
    google_shopping_gender TEXT,
    google_shopping_age_group TEXT,
    google_shopping_mpn TEXT,
    google_shopping_condition TEXT DEFAULT 'new',
    google_shopping_custom_product TEXT DEFAULT 'true',
    variant_image TEXT,
    variant_weight_unit TEXT DEFAULT 'lb',
    variant_tax_code TEXT,
    cost_per_item NUMERIC DEFAULT 0.00,
    shipping_cost NUMERIC DEFAULT 0.00,
    platform_fee NUMERIC DEFAULT 0.00,
    status TEXT DEFAULT 'draft',
    validation_status TEXT DEFAULT 'Needs Validation',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS export_history (
    id SERIAL PRIMARY KEY,
    export_file_name TEXT,
    total_products INTEGER,
    export_type TEXT,
    export_status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
