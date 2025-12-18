import streamlit as st
import math

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="SPACE KO Strategy Calc", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for visual hierarchy
st.markdown("""
    <style>
    .main-header { font-size: 24px; font-weight: bold; color: #FF4B4B; margin-bottom: 10px; }
    .section-header { font-size: 20px; font-weight: 600; margin-top: 20px; border-bottom: 2px solid #f0f2f6; }
    .metric-container { background-color: #f9f9f9; padding: 15px; border-radius: 10px; border-left: 5px solid #FF4B4B; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: TOURNAMENT SETUP ---
with st.sidebar:
    st.header("🏆 Tournament Setup")
    buy_in = st.number_input("Buy-in (€)", min_value=0.01, value=10.00, step=1.0, help="Total entry fee")
    starting_stack = st.number_input("Starting Stack (Chips)", min_value=1, value=20000, step=1000)
    
    st.divider()
    st.caption("Settings are used to calculate the Euro-to-BB exchange rate.")

# --- INITIALIZE SESSION STATE ---
if 'bounty_bb' not in st.session_state:
    st.session_state.bounty_bb = 0.0

# --- MAIN PANEL ---
st.title("🚀 SPACE KO Strategy Calculator")

# SECTION 1: BOUNTY CONVERTER (The MVP)
st.markdown('<p class="section-header">1. Bounty Value Converter (BB)</p>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 3])

with col1:
    current_bb = st.number_input("Current Big Blind (Chips)", min_value=1, value=200, step=50)
    villain_token_avg = st.number_input("Villain's Token Avg Value (€)", min_value=0.0, value=5.00, step=0.5)

# Calculations
chip_value_eur = buy_in / starting_stack
value_of_one_bb_eur = current_bb * chip_value_eur
effective_bounty_eur = villain_token_avg * 0.5  # THE 50% RULE
bounty_bb = effective_bounty_eur / value_of_one_bb_eur if value_of_one_bb_eur > 0 else 0

st.session_state.bounty_bb = bounty_bb

with col2:
    # Color coding logic
    if bounty_bb < 3.0:
        color = "normal"
        label = "LOW IMPACT"
        st.success(f"Bounty is minor. Play close to GTO.")
    elif 3.0 <= bounty_bb <= 8.0:
        color = "off"
        label = "MEDIUM IMPACT"
        st.warning(f"Significant factor. Start widening ranges.")
    else:
        color = "inverse"
        label = "HIGH IMPACT 🚨"
        st.error(f"Major distortion! Defend and shove aggressively.")
    
    st.metric("Bounty Value in BB", f"{bounty_bb:.2f} BB", delta=label, delta_color=color)

with st.expander("View Exchange Rate Details"):
    st.write(f"Value of 1 BB: **€{value_of_one_bb_eur:.4f}**")
    st.write(f"Effective Bounty (Cash portion): **€{effective_bounty_eur:.2f}**")

st.divider()

# --- SECTION 2: PRE-FLOP ADVISOR ---
st.markdown('<p class="section-header">2. Pre-Flop All-In/Call Advisor</p>', unsafe_allow_html=True)

if st.session_state.bounty_bb <= 0:
    st.info("← Enter a Villain Token Value in Section 1 to enable the Call Advisor.")
else:
    c1, c2 = st.columns(2)
    with c1:
        pot_before = st.number_input("Pot Before Shove (BB)", min_value=0.0, value=2.25, help="Blinds + Antes + previous raises")
        to_call = st.number_input("Amount to Call (BB)", min_value=0.1, value=10.0)
    
    # Logic
    total_pot_std = pot_before + (to_call * 2)
    equity_std = (to_call / total_pot_std) * 100
    
    total_pot_ko = total_pot_std + st.session_state.bounty_bb
    equity_ko = (to_call / total_pot_ko) * 100
    reduction = equity_std - equity_ko

    with c2:
        st.markdown(f"**Standard Equity Needed:** {equity_std:.1f}%")
        st.markdown(f"**KO-Adjusted Equity Needed:** <span style='color:#FF4B4B; font-size:20px; font-weight:bold;'>{equity_ko:.1f}%</span>", unsafe_allow_html=True)
        
        if reduction < 3.0:
            st.info(f"Small Impact: Equity reduced by {reduction:.1f}%")
        elif 3.0 <= reduction <= 7.0:
            st.warning(f"Noticeable Impact ⚡: Equity reduced by {reduction:.1f}%")
        else:
            st.error(f"Significant Impact 🚨: Equity reduced by {reduction:.1f}%")

st.divider()

# --- SECTION 3: POST-FLOP PLANNING ---
st.markdown('<p class="section-header">3. Post-Flop Planning Matrix</p>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a:
    eff_stack = st.number_input("Effective Stack (BB)", min_value=0.0, value=40.0)
    flop_pot = st.number_input("Pot on Flop (BB)", min_value=0.1, value=6.0)

spr = eff_stack / flop_pot if flop_pot > 0 else 0

with col_b:
    st.metric("Stack-to-Pot Ratio (SPR)", f"{spr:.2f}")
    
    # Geometric Sizing
    # 2 streets (Flop -> Turn)
    geo_2 = (math.sqrt(2 * spr + 1) - 1) / 2 if spr > 0 else 0
    # 3 streets (Flop -> River) - Approximation
    geo_3 = (math.pow(1 + spr, 1/3) - 1) if spr > 0 else 0

st.subheader("Geometric Sizing (To go All-In by...)")
ga, gb = st.columns(2)
ga.write(f"**The TURN:** {geo_2*100:.0f}% pot ({flop_pot * geo_2:.1f} BB)")
gb.write(f"**The RIVER:** {geo_3*100:.0f}% pot ({flop_pot * geo_3:.1f} BB)")
