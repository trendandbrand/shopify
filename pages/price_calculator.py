import streamlit as st
from database.db import get_db_session, ShopifyProduct
from services.price_service import calculate_price
from services.validator import validate_product_record

def show_price_calculator():
    st.title("🧮 Price Calculator & Sandbox")
    st.markdown("Calculate your recommended selling prices, markups, and profit margins. You can also apply these calculations in bulk to your database products.")

    session = get_db_session()

    # Create two columns: left for interactive calculator, right for database bulk updater
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("🧪 Pricing Sandbox Simulator")
        st.markdown("Test pricing scenarios. This does not modify the database.")
        
        sim_cost = st.number_input("Product Cost ($):", min_value=0.00, value=15.00, step=0.50, key="sim_cost")
        sim_shipping = st.number_input("Shipping Cost ($):", min_value=0.00, value=4.50, step=0.50, key="sim_shipping")
        sim_fee = st.number_input("Platform Transaction Fee ($):", min_value=0.00, value=1.50, step=0.10, key="sim_fee")
        
        st.markdown("---")
        st.markdown("**Pricing Strategy (Choose one or combine):**")
        sim_markup = st.number_input("Markup Percentage (%):", min_value=0.0, value=40.0, step=5.0, key="sim_markup", 
                                     help="Adds a percentage on top of cost + shipping + fee.")
        sim_profit = st.number_input("Additional Desired Profit ($):", min_value=0.0, value=5.0, step=1.0, key="sim_profit",
                                     help="Flat rate profit added to the final price.")
                                     
        # Calculate
        pricing = calculate_price(sim_cost, sim_shipping, sim_fee, sim_profit, sim_markup)
        
        # Display output card
        st.success("📊 **Simulation Results**")
        st.markdown(f"""
        * **Total Base Cost:** `${pricing['base_cost']:.2f}`
        * **Recommended Selling Price:** `${pricing['selling_price']:.2f}`
        * **Compare At Price (30% Discount Display):** `${pricing['compare_at_price']:.2f}`
        * **Estimated Net Profit:** `${pricing['net_profit']:.2f}`
        * **Profit Margin:** `%{pricing['profit_margin']:.1f}`
        """)

    with col_right:
        st.subheader("⚙️ Apply Pricing to Database")
        st.markdown("Apply parameters to update product listings in the database.")
        
        total_products = session.query(ShopifyProduct).count()
        if total_products == 0:
            st.info("No products in database to apply pricing to.")
        else:
            # Inputs for bulk application
            bulk_shipping = st.number_input("Shipping Cost to apply ($):", min_value=0.00, value=5.00, step=0.50, key="bulk_shipping")
            bulk_fee = st.number_input("Platform Fee to apply ($):", min_value=0.00, value=2.00, step=0.50, key="bulk_fee")
            bulk_markup = st.number_input("Markup Percentage to apply (%):", min_value=0.0, value=30.0, step=5.0, key="bulk_markup")
            bulk_profit = st.number_input("Desired Profit to apply ($):", min_value=0.0, value=5.0, step=1.0, key="bulk_profit")
            
            # Selector for products
            st.markdown("---")
            apply_target = st.selectbox("Apply to:", ["All Products", "Products with 0.00 Price Only"])
            
            if st.button("💰 Update Product Prices in DB", type="primary"):
                # Run query
                if apply_target == "All Products":
                    products_to_update = session.query(ShopifyProduct).all()
                else:
                    products_to_update = session.query(ShopifyProduct).filter(
                        (ShopifyProduct.variant_price == 0.0) | (ShopifyProduct.variant_price == None)
                    ).all()
                    
                updated_count = 0
                for p in products_to_update:
                    # Retrieve the item's cost (defaulting to 0.0 if not set)
                    cost = float(p.cost_per_item or 0.0)
                    
                    pricing_res = calculate_price(
                        product_cost=cost,
                        shipping_cost=bulk_shipping,
                        platform_fee=bulk_fee,
                        desired_profit=bulk_profit,
                        markup_percentage=bulk_markup
                    )
                    
                    p.variant_price = pricing_res["selling_price"]
                    p.variant_compare_at_price = pricing_res["compare_at_price"]
                    p.shipping_cost = bulk_shipping
                    p.platform_fee = bulk_fee
                    
                    # Re-run validation
                    val_res = validate_product_record(p, db_session=session)
                    p.validation_status = val_res["status"]
                    
                    updated_count += 1
                    
                session.commit()
                st.success(f"Prices updated and validated successfully for {updated_count} products!")
                st.rerun()

    session.close()

if __name__ == "__main__":
    show_price_calculator()
