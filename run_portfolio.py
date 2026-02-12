from agents.portfolio_manager import PortfolioManager
import json
import os

def run():
    # Load tickers from config
    with open("config.json", "r") as f:
        config = json.load(f)
    
    watchlist = config.get("watchlist", [])
    
    if not watchlist:
        print("Watchlist empty. Check config.json")
        return

    print(f"Running Portfolio Analysis for: {watchlist}")
    
    pm = PortfolioManager(watchlist, period="2y")
    pm.load_data()
    
    # 1. Correlation
    print("Generating Correlation Matrix...")
    pm.plot_correlation_matrix()
    
    # 2. Optimization
    
    # 2. Optimization Scenarios
    print("\nCALCULATING SCENARIOS...")
    
    # Scene A: Conservative (Min Vol)
    res_con = pm.optimize_min_volatility()
    
    # Scene B: Balanced (Max Sharpe)
    res_bal = pm.optimize_efficient_frontier()
    
    # Scene C: Aggressive (Target 30% Vol)
    res_agg = pm.optimize_target_risk(target_volatility=0.40) # 40% Vol limit
    
    scenarios = [res_con, res_bal, res_agg]
    labels = ["CONSERVATIVE (Min Vol)", "BALANCED (Max Sharpe)", "AGGRESSIVE (40% Vol)"]
    
    for label, res in zip(labels, scenarios):
        if not res: continue
        print(f"\n{label}")
        print(f"  Return: {res['return']*100:.2f}% | Risk: {res['volatility']*100:.2f}% | Sharpe: {res['sharpe']:.2f}")
        
        # Show top 5 allocations
        alloc = res['allocation']
        sorted_alloc = dict(sorted(alloc.items(), key=lambda item: item[1], reverse=True))
        top_5 = list(sorted_alloc.items())[:5]
        print("  Top Holdings:")
        for ticker, weight in top_5:
            if weight > 0.01:
                print(f"    {ticker:<8}: {weight*100:.1f}%")

if __name__ == "__main__":
    run()
