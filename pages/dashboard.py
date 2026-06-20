import streamlit as st
from database.db import get_db_session, RawProduct, ShopifyProduct, ExportHistory
from sqlalchemy import func


def show_dashboard():
    # ─── Hero Banner ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(99, 102, 241, 0.05) 50%, rgba(9, 13, 22, 0.2) 100%);
                border-radius: 16px; padding: 36px 40px; margin-bottom: 28px;
                border: 1px solid rgba(139, 92, 246, 0.15); position: relative; overflow: hidden;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);">
        <div style="position:absolute; top:-30px; right:-30px; width:160px; height:160px;
                    background: radial-gradient(circle, rgba(139, 92, 246, 0.2) 0%, transparent 70%);
                    border-radius: 50%;"></div>
        <div style="position:absolute; bottom:-40px; left:30%; width:200px; height:200px;
                    background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 70%);
                    border-radius: 50%;"></div>
        <div style="position: relative; z-index:1;">
            <h1 style="border:none !important; margin:0 !important; padding:0 !important;
                        font-family:'Plus Jakarta Sans', sans-serif !important;
                        font-size:2.2rem !important; color:#ffffff !important; font-weight:800 !important;
                        letter-spacing:-0.03em !important;">
                📊 Dashboard
            </h1>
            <p style="color:#9ca3af; margin:10px 0 20px; font-size:0.95rem; font-family:'Plus Jakarta Sans', sans-serif;">
                Monitor your Shopify catalog pipeline — imports, edits, validation, and exports.
            </p>
            <a href="https://www.trendandbrands.com/" target="_blank"
               style="display:inline-flex; align-items:center; gap:6px; background:rgba(139, 92, 246, 0.12);
                      color:#c084fc; padding:8px 18px; border-radius:20px; font-size:0.8rem;
                      font-weight:700; text-decoration:none; border:1px solid rgba(139, 92, 246, 0.25);
                      transition: all 0.2s ease;">
                🏷️ Trend & Brand ↗
              </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    session = get_db_session()

    try:
        # ─── Fetch DB Stats ────────────────────────────────────────────────────
        total_raw      = session.query(RawProduct).count()
        total_shopify  = session.query(ShopifyProduct).count()
        total_exports  = session.query(ExportHistory).count()
        ready_count    = session.query(ShopifyProduct).filter(ShopifyProduct.validation_status == 'Ready').count()
        needs_fixing   = total_shopify - ready_count
        missing_images = session.query(ShopifyProduct).filter(
            (ShopifyProduct.image_src == None) | (ShopifyProduct.image_src == "")
        ).count()
        missing_price  = session.query(ShopifyProduct).filter(
            (ShopifyProduct.variant_price == None) | (ShopifyProduct.variant_price == 0.0)
        ).count()
        sku_dupes = len(
            session.query(ShopifyProduct.variant_sku)
                   .group_by(ShopifyProduct.variant_sku)
                   .having(func.count(ShopifyProduct.variant_sku) > 1).all()
        )
        last_export_date = session.query(func.max(ExportHistory.created_at)).scalar()
        last_export_str  = last_export_date.strftime("%d %b %Y, %H:%M") if last_export_date else "Never"

        # ─── Top-Level Metrics ────────────────────────────────────────────────
        st.markdown("### 📈 Pipeline Overview")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("URLs Imported",   total_raw,     help="Total product URLs added to the scraper")
        with c2:
            st.metric("Products Created", total_shopify, help="Shopify product entries in the database")
        with c3:
            st.metric("Exports Generated", total_exports, help="CSV/Excel batches ever exported")
        with c4:
            st.metric("Last Export",     last_export_str, help="Date of the most recent export batch")

        # ─── Validation Health ─────────────────────────────────────────────────
        st.markdown("### ✅ Catalog Health")
        v1, v2, v3, v4, v5 = st.columns(5)
        with v1:
            st.metric("✅ Ready to Export", ready_count)
        with v2:
            st.metric("🔴 Needs Fixing",   needs_fixing,   delta=f"-{needs_fixing}" if needs_fixing else None, delta_color="inverse")
        with v3:
            st.metric("🖼️ Missing Images", missing_images, delta=f"-{missing_images}" if missing_images else None, delta_color="inverse")
        with v4:
            st.metric("💰 Zero Price",     missing_price,  delta=f"-{missing_price}" if missing_price else None,  delta_color="inverse")
        with v5:
            st.metric("⚠️ Duplicate SKUs", sku_dupes,     delta=f"-{sku_dupes}" if sku_dupes else None,          delta_color="inverse")

        # ─── Copyright Warning ─────────────────────────────────────────────────
        st.warning("⚠️ **Copyright & Safety Reminder:** Do not publish copyrighted Amazon or competitor content. Use the **Auto-Rewrite** feature in the Product Editor to create unique copy, and always use authorized manufacturer or supplier images.")

        # ─── Quick Action Cards ────────────────────────────────────────────────
        st.markdown("### 🚀 Quick Actions")
        qa1, qa2, qa3, qa4 = st.columns(4)
        with qa1:
            st.markdown("""
            <div class="quick-action-card">
                <div class="card-icon">📥</div>
                <div class="card-title">Import Products</div>
                <div class="card-desc">Paste URLs, scan seller page or parse sitemap XML</div>
            </div>
            """, unsafe_allow_html=True)
        with qa2:
            st.markdown("""
            <div class="quick-action-card">
                <div class="card-icon">🔎</div>
                <div class="card-title">Hunt on Amazon</div>
                <div class="card-desc">Search keywords to find trending items and import</div>
            </div>
            """, unsafe_allow_html=True)
        with qa3:
            st.markdown("""
            <div class="quick-action-card">
                <div class="card-icon">✅</div>
                <div class="card-title">Validate Catalog</div>
                <div class="card-desc">Check SEO, images, prices, and SKUs before exporting</div>
            </div>
            """, unsafe_allow_html=True)
        with qa4:
            st.markdown("""
            <div class="quick-action-card">
                <div class="card-icon">📤</div>
                <div class="card-title">Export to Shopify</div>
                <div class="card-desc">Download Shopify import-ready CSV & Excel files</div>
            </div>
            """, unsafe_allow_html=True)

        # ─── Recent Products ───────────────────────────────────────────────────
        st.markdown("### 🛒 Recent Products")
        recent = session.query(ShopifyProduct).order_by(ShopifyProduct.updated_at.desc()).limit(10).all()

        if recent:
            rows = []
            for p in recent:
                status_icon = "🟢" if p.validation_status == "Ready" else "🔴"
                rows.append({
                    "Status": f"{status_icon} {p.validation_status}",
                    "Title":  (p.title or "")[:55],
                    "SKU":    p.variant_sku or "—",
                    "Price":  f"${float(p.variant_price or 0):.2f}",
                    "Vendor": p.vendor or "—",
                    "Store Status": p.status or "draft",
                })
            st.dataframe(rows, width="stretch", hide_index=True)
        else:
            st.markdown("""
            <div style="background:#1a1a2e; border:1px dashed #2d3748; border-radius:12px;
                        padding:40px; text-align:center; color:#4a5568;">
                <div style="font-size:3rem; margin-bottom:12px;">📭</div>
                <div style="font-size:1rem; font-weight:600; color:#718096;">No products yet</div>
                <div style="font-size:0.85rem; margin-top:6px;">
                    Use <strong>Product Link Importer</strong> or <strong>Amazon Product Hunting</strong> to get started.
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ─── Recent Exports ────────────────────────────────────────────────────
        if total_exports > 0:
            st.markdown("### 📤 Recent Exports")
            recent_exports = session.query(ExportHistory).order_by(ExportHistory.created_at.desc()).limit(5).all()
            exp_rows = [{"File": e.export_file_name, "Products": e.total_products,
                         "Type": e.export_type, "Date": e.created_at.strftime("%d %b %Y %H:%M")}
                        for e in recent_exports]
            st.dataframe(exp_rows, width="stretch", hide_index=True)

    except Exception as e:
        st.error(f"Error loading dashboard: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    show_dashboard()
