import sys

def get_input(prompt, entry_type=float):
    """Helper to ensure valid numeric input."""
    while True:
        try:
            return entry_type(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    print("=== Winamax Space KO Poker Companion ===")
    
    # 1. INITIAL TOURNAMENT SETTINGS
    buy_in = get_input("Tournament Buy-in (€): ")
    starting_stack = get_input("Starting Stack (chips): ")
    bb_value = get_input("Current Big Blind (chips): ")

    # Calculate Chip Value based on 40% Regular Prize Pool 
    # Euro_per_chip = (Buy_in * 0.40) / Starting_Stack
    chip_euro_value = (buy_in * 0.4) / starting_stack
    
    # 2. TOKEN VALUE MAPPING (Multipliers based on source [cite: 11])
    token_multipliers = {
        1: 0.5, 2: 0.6, 3: 0.75, 4: 1.0, 5: 1.5,
        6: 2.5, 7: 5.0, 8: 10.0, 9: 20.0, 10: 50.0
    }

    print("\n--- Setup Complete. Entering Active Play Mode ---")
    
    while True:
        print("\n--- NEW HAND ---")
        try:
            villain_shove = get_input("Villain's Total Shove (chips): ")
            current_pot = get_input("Current Pot before Shove (chips): ")
            villain_lvl = get_input("Villain's Token Level (1-10, or 11+): ", int)
            hero_call_amount = get_input("Amount you need to call (chips): ")

            # Calculate Average Bounty Value [cite: 9, 11]
            if villain_lvl >= 11:
                print("\n[!] HIGH VALUE TARGET: Token Lvl 11+ has a massive fixed minimum. [cite: 11]")
                avg_bounty_total = buy_in * 1000  # Simplified logic for Lvl 11+
            else:
                multiplier = token_multipliers.get(villain_lvl, 0.5)
                avg_bounty_total = buy_in * multiplier

            # 50/50 Split Logic: Only 50% is immediate cash value [cite: 4, 22, 40]
            immediate_cash_bounty = avg_bounty_total * 0.5
            future_token_equity = avg_bounty_total * 0.5
            
            # Convert Bounty Cash to "Chip Equivalent"
            bounty_in_chips = immediate_cash_bounty / chip_euro_value

            # 3. MATHEMATICAL CALCULATIONS
            # Standard Pot Odds: Call / (Pot + Call)
            total_pot_standard = current_pot + villain_shove + hero_call_amount
            standard_equity_needed = (hero_call_amount / total_pot_standard) * 100

            # Space KO Adjusted Pot Odds (Adding Bounty Chips to the Pot)
            total_pot_ko = total_pot_standard + bounty_in_chips
            ko_equity_needed = (hero_call_amount / total_pot_ko) * 100

            # 4. OUTPUT DISPLAY
            print("-" * 30)
            print(f"Bounty Value in Chips: {bounty_in_chips:.0f} chips")
            print(f"Standard Equity Needed: {standard_equity_needed:.2f}%")
            print(f"Space KO Equity Needed: {ko_equity_needed:.2f}%")
            print(f"NOTE: Winning also adds ~€{future_token_equity:.2f} to your FUTURE Token value! [cite: 22]")
            
            # 5. RANGE ADVICE
            print("\nSUGGESTED STRATEGY:")
            if ko_equity_needed < 15:
                print(">> CALL WITH ANY 2 CARDS (ATC) <<")
            elif 15 <= ko_equity_needed < 25:
                print(">> CALL EXTREMELY WIDE: Any Broadway, Any Pair, Any Suited, Any Ace. <<")
            elif 25 <= ko_equity_needed < 35:
                print(">> CALL WIDE: Gappers, K-high, all Aces. <<")
            else:
                print(">> Standard calling range applies. <<")
            print("-" * 30)

        except KeyboardInterrupt:
            print("\nExiting Tool...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
