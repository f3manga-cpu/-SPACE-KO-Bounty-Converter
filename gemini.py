import streamlit as st
import numpy as np

# Page Configuration
st.set_page_config(page_title="SPACE KO Bounty Assistant", layout="wide")
st.page_icon="🛸",
st.title("🛸 SPACE KO Strategy Calculator")
st.markdown("---")

# --- SIDEBAR: TOURNAMENT SETUP ---
with st.sidebar:
    st.header("⚙️ Tournament Setup")
    st.info("Set these at the start of the tournament.")
    
    buy_in = st.number_input("Tournament Buy-in (€)", min_value=0.1, value=10.0, step=1.0, help="Total entry cost")
    start_stack = st.number_input("Starting Stack (Chips)", min_value=1, value=20000, step=1000)
    
    st.divider()
    st.caption("How it works: 50% of the Buy-in goes to bounties. "
               "The app uses these to calculate Chip-to-Euro exchange rates.")

# --- MAIN PANEL: HAND INPUTS ---
col_in1, col_in2 = st.columns(2)

with col_in1:
    st.subheader("🃏 Current Hand")
    curr_bb_chips = st.number_input("Current Big Blind (Chips)", min_value=1, value=200, step=50)
    villain_bounty_eur = st.number_input("Villain's Token Avg Value (€)", min_value=0.0, value=5.0, step=0.5, 
                                         help="Click on the opponent's token in the Winamax client to see 'Moy.'")

with col_in2:
    st.subheader("💰 Pot & Call")
    pot_before_bb = st.number_input("Pot Size Before Call (BB)", min_value=0.1, value=10.0, step=1.0)
    call_amount_bb = st.number_input("Amount to Call (BB)", min_value=0.0, value=5.0, step=1.0)

with st.expander("📐 Advanced: SPR & Geometric Sizing"):
    col_adv1, col_adv2 = st.columns(2)
    with col_adv1:
        eff_stack_bb = st.number_input("Effective Stack Behind (BB)", min_value=0.0, value=50.0, step=1.0,
                                       help="The smaller of your or your opponent's remaining stack.")
    with col_adv2:
        pot_on_flop_bb = st.number_input("Pot on Flop (BB)", min_value=0.1, value=6.0, step=1.0)

# --- CALCULATIONS ---

# 1. Bounty Conversion
# Value of 1 BB in Euro = (Current BB Chips) * (Total Buy-in / Starting Stack)
# Note: SPACE KO uses the full buy-in logic for its internal math [cite: 3, 11]
chip_to_eur_ratio = buy_in / start_stack
one_bb_eur = curr_bb_chips * chip_to_eur_ratio
bounty_in_bb = villain_bounty_eur / one_bb_eur / 2 if one_bb_eur > 0 else 0

# 2. Equity Calculations
# Pot Odds = Call / (Pot + Call + Bounty)
standard_equity = (call_amount_bb / (pot_before_bb + call_amount_bb)) * 100 if (pot_before_bb + call_amount_bb) > 0 else 0
bounty_equity = (call_amount_bb / (pot_before_bb + call_amount_bb + bounty_in_bb)) * 100 if (pot_before_bb + call_amount_bb + bounty_in_bb) > 0 else 0

# 3. SPR
spr = eff_stack_bb / pot_on_flop_bb if pot_on_flop_bb > 0 else 0

# 4. Geometric Bet Sizing
def solve_geometric(streets, stack, pot):
    if pot <= 0 or stack <= 0: return 0
    # Formula: stack = pot * ((1 + 2r)^n - 1) / 2
    # We solve for r: (1 + 2r)^n = (2 * stack / pot) + 1
    # r = [((2 * stack / pot) + 1)^(1/n) - 1] / 2
    r = (((2 * stack / pot) + 1)**(1/streets) - 1) / 2
    return r * 100

geo_2_streets = solve_geometric(2, eff_stack_bb, pot_on_flop_bb)
geo_3_streets = solve_geometric(3, eff_stack_bb, pot_on_flop_bb)

# --- OUTPUT DISPLAY ---
st.markdown("---")
st.subheader("📊 Strategic Outputs")

m1, m2, m3 = st.columns(3)

with m1:
    st.metric("🎯 Bounty Value", f"{bounty_in_bb:.2f} BB", delta="Added to Pot")
    st.caption("Treat the pot as if it has these extra BBs.")

with m2:
    st.metric("🤔 Req. Equity (With Bounty)", f"{bounty_equity:.1f}%", 
              delta=f"{bounty_equity - standard_equity:.1f}% vs Raw Odds", delta_color="inverse")
    st.caption(f"Standard Odds: {standard_equity:.1f}%")

with m3:
    spr_desc = "Commit with TP+" if spr < 4 else "Deep Stacks"
    st.metric("📊 SPR", f"{spr:.2f}", spr_desc)

st.markdown("---")
st.subheader("📐 All-In Geometric Sizing (from Flop)")
g1, g2 = st.columns(2)

with g1:
    st.info(f"**To Shove TURN (2 Streets)**\n\nBet **{geo_2_streets:.1f}%** of pot on Flop and Turn.")

with g2:
    st.info(f"**To Shove RIVER (3 Streets)**\n\nBet **{geo_3_streets:.1f}%** of pot on Flop, Turn, and River.")

st.warning("⚠️ **Strategy Tip:** In Space KO, you win 50% of the drawn bounty instantly, and 50% is added to your own token value. ")
