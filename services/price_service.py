def calculate_price(product_cost, shipping_cost, platform_fee, desired_profit=0.0, markup_percentage=0.0):
    """
    Calculates selling price, compare-at price, net profit, and profit margin.
    
    Formulas:
    Base Cost = Product Cost + Shipping Cost + Platform Fee
    Selling Price = Base Cost * (1 + Markup%) + Desired Profit
    Net Profit = Selling Price - Base Cost
    Profit Margin = (Net Profit / Selling Price) * 100
    Compare At Price = Selling Price * 1.3 (suggested 30% markup markdown)
    """
    cost = float(product_cost or 0.0)
    shipping = float(shipping_cost or 0.0)
    fee = float(platform_fee or 0.0)
    profit_target = float(desired_profit or 0.0)
    markup = float(markup_percentage or 0.0)
    
    base_cost = cost + shipping + fee
    
    # Determine selling price
    selling_price = base_cost
    if markup > 0:
        selling_price = base_cost * (1 + (markup / 100.0))
        
    selling_price += profit_target
    
    # Keep selling price positive and avoid division by zero
    if selling_price <= 0:
        selling_price = 0.01
        
    net_profit = selling_price - base_cost
    profit_margin = (net_profit / selling_price) * 100.0
    
    # Default Compare At Price is 30% higher
    compare_at_price = selling_price * 1.3
    
    return {
        "selling_price": round(selling_price, 2),
        "compare_at_price": round(compare_at_price, 2),
        "net_profit": round(net_profit, 2),
        "profit_margin": round(profit_margin, 2),
        "base_cost": round(base_cost, 2)
    }
