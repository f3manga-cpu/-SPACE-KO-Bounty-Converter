import streamlit as st
import numpy as np

# Page configuration
st.set_page_config(
    page_title="SPACE KO Strategy Calculator",
    page_icon="🎯",
    layout="wide"
)

# Title
st.title("🚀 SPACE KO Tournament Strategy Calculator")
st.markdown("**Real-time bounty conversion and strategic decision assistant**")
st.divider()

# ==================== CALCULATION FUNCTIONS ====================

def bounty_in_bb(buy_in, starting_stack, current_bb, token_avg_eur):
    """Convert opponent's bounty token value (€) to Big Blinds"""
    if starting_stack == 0 or current_bb == 0:
        return 0
    chip_value_eur = buy_in / starting_stack
    one_bb_in_eur = current_bb * chip_value_eur
    if one_bb_in_eur == 0:
        return 0
    return token_avg_eur / one_bb_in_eur

def calculate_pot_odds(pot_before, amount_to_call, bounty_bb=0):
    """Calculate required equity % to call (with and without bounty)"""
    total_pot = pot_before + amount_to_call
    if total_pot == 0:
        return 0, 0
    
    odds_without = (amount_to_call / total_pot) * 100
    odds_with = (amount_to_call / (total_pot + bounty_bb)) * 100
    
    return odds_without, odds_with

def calculate_spr(effective_stack, pot_on_flop):
    """Calculate Stack-to-Pot Ratio"""
    if pot_on_flop == 0:
        return 0
    return effective_stack / pot_on_flop

def geometric_bet_sizing(pot_on_flop, effective_stack):
    """
    Calculate optimal bet size as % of pot for geometric betting strategy.
    Returns: (flop_bet_pct_for_turn_allin, flop_bet_pct_for_river_allin)
    """
    if pot_on_flop == 0:
        return 0, 0
    
    ratio = effective_stack / pot_on_flop
    
    # For turn all-in (2 streets): 2r + 2r^2 = ratio
    # Rearranged: 2r^2 + 2r - ratio = 0
    coeffs_turn = [2, 2, -ratio]
    roots_turn = np.roots(coeffs_turn)
    # Take positive real root
    r_turn = max([r.real for r in roots_turn if r.real > 0 and abs(r.imag) < 1e-10], default=0)
    
    # For river all-in (3 streets): 4r^3 + 6r^2 + 3r - ratio = 0
    coeffs_river = [4, 6, 3, -ratio]
    roots_river = np.roots(coeffs_river)
    # Take positive real root
    r_river = max([r.real for r in roots_river if r.real > 0 and abs(r.imag) < 1e-10], default=0)
    
    return r_turn * 100, r_river * 100

def get_spr_interpretation(spr):
    """Provide strategic interpretation of SPR value"""
    if spr < 2:
        return "🔴 Very Low SPR: Commit with any pair or better"
    elif spr < 4:
        return "🟠 Low SPR: Commit with top pair or better"
    elif spr < 7:
        return "🟡 Medium SPR: Play cautiously, need strong hands"
    elif spr < 13:
        return "🟢 High SPR: Deep play, can bluff/fold more"
    else:
        return "🔵 Very High SPR: Maximum flexibility"

# ==================== SIDEBAR - TOURNAMENT SETUP ====================

with st.sidebar:
    st.header("⚙️ Tournament Setup")
    st.markdown("*Configure once per tournament*")
    
    buy_in = st.number_input(
        "Tournament Buy-in (€)",
        min_value=0.01,
        value=10.00,
        step=0.01,
        format="%.2f",
        help="Total buy-in amount (e.g., 10€ for a €10 SPACE KO)"
    )
    
    starting_stack = st.number_input(
        "Starting Stack (Chips)",
        min_value=1,
        value=20000,
        step=1000,
        help="Default for Winamax MTTs is 20,000 chips"
    )
    
    st.info("💡 These values set the chip-to-euro exchange rate. Adjust only when starting a new tournament.")
    
    # Display conversion rate
    chip_value = buy_in / starting_stack
    st.metric("Chip Value", f"€{chip_value:.6f} per chip")

# ==================== MAIN PANEL - HAND INPUTS ====================

st.header("🎴 Current Hand Analysis")

# Section 1: Essential Bounty Conversion
st.subheader("Essential Inputs")

col1, col2 = st.columns(2)

with col1:
    current_bb = st.number_input(
        "Current Big Blind (Chips)",
        min_value=0,
        value=200,
        step=50,
        help="The current big blind level (updates most frequently)"
    )

with col2:
    token_avg_eur = st.number_input(
        "Villain's Token - Average Value (€)",
        min_value=0.0,
        value=5.0,
        step=0.5,
        format="%.2f",
        help="Click on opponent's token in your poker client to see this value"
    )

# Calculate bounty in BB (always)
bounty_bb = bounty_in_bb(buy_in, starting_stack, current_bb, token_avg_eur)

# Section 2: Advanced Calculations
with st.expander("🔬 Advanced: Pot & Bet Analysis", expanded=False):
    st.markdown("*Optional: For detailed pot odds, SPR, and geometric sizing calculations*")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        pot_before = st.number_input(
            "Pot Before Facing Bet (BB)",
            min_value=0.0,
            value=10.0,
            step=0.5,
            format="%.1f",
            help="Total pot size before your opponent's bet"
        )
    
    with col_b:
        amount_to_call = st.number_input(
            "Amount to Call (BB)",
            min_value=0.0,
            value=5.0,
            step=0.5,
            format="%.1f",
            help="How many BB you need to call"
        )
    
    with col_c:
        pot_on_flop = st.number_input(
            "Pot on Flop (BB)",
            min_value=0.0,
            value=6.0,
            step=0.5,
            format="%.1f",
            help="Pot size on the flop (for SPR and geometric sizing)"
        )
    
    effective_stack = st.number_input(
        "Effective Stack Behind (BB)",
        min_value=0.0,
        value=100.0,
        step=5.0,
        format="%.1f",
        help="Smaller of yours or opponent's remaining stack on the flop"
    )

# ==================== OUTPUTS & STRATEGY ====================

st.divider()
st.header("📊 Strategic Outputs")

# Primary Output 1: Bounty Value
st.subheader("🎯 Target Bounty Value")
col_bounty1, col_bounty2, col_bounty3 = st.columns([2, 2, 3])

with col_bounty1:
    st.metric(
        label="Bounty in BB",
        value=f"{bounty_bb:.2f} BB",
        help="This value is added to the effective pot"
    )

with col_bounty2:
    st.metric(
        label="Bounty in €",
        value=f"€{token_avg_eur:.2f}"
    )

with col_bounty3:
    st.info("💡 **Usage:** Add this bounty value to the pot when calculating pot odds and making calling decisions.")

# Primary Output 2: Equity Required
if pot_before > 0 and amount_to_call > 0:
    st.subheader("🤔 Required Equity to Call")
    
    odds_without, odds_with = calculate_pot_odds(pot_before, amount_to_call, bounty_bb)
    
    col_eq1, col_eq2, col_eq3 = st.columns([2, 2, 3])
    
    with col_eq1:
        st.metric(
            label="Without Bounty",
            value=f"{odds_without:.1f}%"
        )
    
    with col_eq2:
        st.metric(
            label="⭐ With Bounty",
            value=f"{odds_with:.1f}%",
            delta=f"{odds_without - odds_with:.1f}%",
            delta_color="inverse"
        )
    
    with col_eq3:
        st.success(f"✅ **Call if your hand's equity > {odds_with:.1f}%**")
        st.caption(f"Bounty reduces required equity by {odds_without - odds_with:.1f} percentage points")

# Primary Output 3: Geometric Bet Sizing
if pot_on_flop > 0 and effective_stack > 0:
    st.subheader("📐 All-In Geometric Sizing (from Flop)")
    
    turn_pct, river_pct = geometric_bet_sizing(pot_on_flop, effective_stack)
    
    col_geo1, col_geo2 = st.columns(2)
    
    with col_geo1:
        st.metric(
            label="🎲 To Go All-In on TURN",
            value=f"{turn_pct:.1f}%",
            help="Bet this % of the flop pot"
        )
        st.caption(f"Bet Size: {turn_pct * pot_on_flop / 100:.1f} BB on the flop")
    
    with col_geo2:
        st.metric(
            label="🎰 To Go All-In on RIVER",
            value=f"{river_pct:.1f}%",
            help="Bet this % of the flop pot (and continue with same % on turn)"
        )
        st.caption(f"Bet Size: {river_pct * pot_on_flop / 100:.1f} BB on the flop")

# Secondary Output 4: SPR
if pot_on_flop > 0 and effective_stack > 0:
    st.subheader("📊 Stack-to-Pot Ratio (SPR)")
    
    spr = calculate_spr(effective_stack, pot_on_flop)
    spr_interpretation = get_spr_interpretation(spr)
    
    col_spr1, col_spr2 = st.columns([1, 2])
    
    with col_spr1:
        st.metric(
            label="SPR Value",
            value=f"{spr:.2f}",
            help="Effective Stack / Pot on Flop"
        )
    
    with col_spr2:
        st.info(spr_interpretation)

# Footer
st.divider()
st.caption("🎯 Built for Winamax SPACE KO tournaments | Real-time strategic decision support")
st.caption("💡 Tip: Keep this open in a separate window during your tournament for instant calculations")
