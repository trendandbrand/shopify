import os
import logging
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Boolean, DateTime, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db")

Base = declarative_base()

class RawProduct(Base):
    __tablename__ = 'products_raw'
    
    id = Column(Integer, primary_key=True)
    source_url = Column(Text)
    raw_title = Column(Text)
    raw_price = Column(Numeric(10, 2))
    raw_description = Column(Text)
    raw_images = Column(Text)
    raw_vendor = Column(Text)
    extraction_status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class ShopifyProduct(Base):
    __tablename__ = 'shopify_products'
    
    id = Column(Integer, primary_key=True)
    source_url = Column(Text)
    handle = Column(Text)
    title = Column(Text)
    body_html = Column(Text)
    vendor = Column(Text)
    product_category = Column(Text)
    product_type = Column(Text)
    tags = Column(Text)
    published = Column(Text, default='true')
    option1_name = Column(Text)
    option1_value = Column(Text)
    option2_name = Column(Text)
    option2_value = Column(Text)
    option3_name = Column(Text)
    option3_value = Column(Text)
    variant_sku = Column(Text)
    variant_grams = Column(Integer, default=0)
    variant_inventory_tracker = Column(Text, default='shopify')
    variant_inventory_qty = Column(Integer, default=1)
    variant_inventory_policy = Column(Text, default='deny')
    variant_fulfillment_service = Column(Text, default='manual')
    variant_price = Column(Numeric(10, 2), default=0.00)
    variant_compare_at_price = Column(Numeric(10, 2), default=0.00)
    variant_requires_shipping = Column(Boolean, default=True)
    variant_taxable = Column(Boolean, default=True)
    variant_barcode = Column(Text)
    image_src = Column(Text)
    image_position = Column(Integer)
    image_alt_text = Column(Text)
    gift_card = Column(Text, default='false')
    seo_title = Column(Text)
    seo_description = Column(Text)
    google_shopping_category = Column(Text)
    google_shopping_gender = Column(Text)
    google_shopping_age_group = Column(Text)
    google_shopping_mpn = Column(Text)
    google_shopping_condition = Column(Text, default='new')
    google_shopping_custom_product = Column(Text, default='true')
    variant_image = Column(Text)
    variant_weight_unit = Column(Text, default='lb')
    variant_tax_code = Column(Text)
    cost_per_item = Column(Numeric(10, 2), default=0.00)
    shipping_cost = Column(Numeric(10, 2), default=0.00)
    platform_fee = Column(Numeric(10, 2), default=0.00)
    status = Column(Text, default='draft')
    validation_status = Column(Text, default='Needs Validation')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExportHistory(Base):
    __tablename__ = 'export_history'
    
    id = Column(Integer, primary_key=True)
    export_file_name = Column(Text)
    total_products = Column(Integer)
    export_type = Column(Text)
    export_status = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database Engine Setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/product2shopify")
SQLITE_URL = "sqlite:///product2shopify.db"

engine = None
SessionLocal = None
using_sqlite = False

def init_db():
    global engine, SessionLocal, using_sqlite
    
    # Try PostgreSQL first
    try:
        logger.info(f"Attempting connection to PostgreSQL database at {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
        engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 3})
        # Try to connect to verify
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Successfully connected to PostgreSQL.")
        using_sqlite = False
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed: {e}. Falling back to SQLite database.")
        try:
            engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to SQLite.")
            using_sqlite = True
        except Exception as sq_err:
            logger.error(f"SQLite connection failed as well: {sq_err}")
            raise sq_err

    # Create tables
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize database
init_db()

def get_db():
    """Dependency helper to yield database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    """Helper to get a direct database session instance (not generator)."""
    return SessionLocal()
