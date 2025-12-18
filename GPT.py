import streamlit as st
import numpy as np

st.set_page_config(
    page_title="SPACE KO Strategy Calculator",
    layout="centered"
)

# =========================
# Calculation Functions
# =========================

def bounty_in_bb(buy_in, starting_stack, current_bb, token_avg_eur):
    if starting_stack <= 0 or current_bb <= 0:
        return 0.0
    chip_value_eur = buy_in / starting_stack
    one_bb_in_eur = current_bb * chip_value_eur
    if one_bb_in_eur <= 0:
        return 0.0
    return token_avg_eur / one_bb_in_eur


def pot_odds(amount_to_call, pot_before, bounty_bb=0):
    if pot_before + amount_to_call <= 0:
        return 0.0, 0.0

    standard = amount_to_call / (pot_before + amount_to_call)

    with_bounty = amount_to_call / (
        pot_before + amount_to_call + max(bounty_bb, 0)
    )

    return standard * 100, with_bounty * 100


def spr(effective_stack, pot_flop):
    if pot_flop <= 0:
        return 0.0
    return effective_stack / pot_flop


def geometric_turn(effective_stack, pot):
    if pot <= 0:
        return 0.0
    ratio = effective_stack / pot
    # Solve: 2r + 2r^2 = ratio → 2r^2 + 2r - ratio = 0
    a, b, c = 2, 2, -ratio
    disc = b**2 - 4*a*c
    if disc < 0:
        return 0.0
    r = (-b + np.sqrt(disc)) / (2 * a)
    return max(r, 0.0) * 100


def geometric_river(effective_stack, pot):
    if pot <= 0:
        return 0.0
    ratio = effective_stack / pot
    # 4r^3 + 6r^2 + 3r - ratio = 0
    coeffs = [4, 6, 3, -ratio]
    roots = np.roots(coeffs)
    real_roots = [r.real for r in roots if abs(r.imag) < 1e-6 and r.real > 0]
    if not real_roots:
        return 0.0
    return min(real_roots) * 100


# =========================
# SIDEBAR — Tournament Setup
# =========================

st.sidebar.title("🎯 Tournament Setup")

buy_in = st.sidebar.number_input(
    "Tournament Buy-in (€)",
    min_value=0.01,
    step=0.01,
    value=10.00
)

starting_stack = st.sidebar.number_input(
    "Starting Stack (Chips)",
    min_value=1,
    step=1000,
    value=20000
)

st.sidebar.caption(
    "Values here set the chip-to-euro exchange rate.\n"
    "Adjust only when starting a new tournament."
)

# =========================
# MAIN PANEL — Hand Inputs
# =========================

st.title("SPACE KO In-Game Decision Assistant")

st.subheader("Hand Inputs")

current_bb = st.number_input(
    "Current Big Blind (Chips)",
    min_value=1,
    step=100,
    value=100
)

token_avg = st.number_input(
    "Villain's Token – Average Value (€)",
    min_value=0.0,
    step=0.01,
    help="Click on any opponent's token in your client to see this value."
)

st.divider()

with st.expander("Advanced: Pot & Bet Analysis"):

    pot_before = st.number_input(
        "Pot Size Before Facing Bet (BB)",
        min_value=0.0,
        step=0.5
    )

    amount_to_call = st.number_input(
        "Amount to Call (BB)",
        min_value=0.0,
        step=0.5
    )

    pot_flop = st.number_input(
        "Pot on Flop (BB)",
        min_value=0.0,
        step=0.5
    )

    effective_stack = st.number_input(
        "Effective Stack Behind (BB)",
        min_value=0.0,
        step=0.5,
        help="Smaller of your or villain’s remaining stack on the flop."
    )

# =========================
# CALCULATIONS
# =========================

bounty_bb = bounty_in_bb(
    buy_in, starting_stack, current_bb, token_avg
)

pot_odds_std, pot_odds_bounty = pot_odds(
    amount_to_call, pot_before, bounty_bb
)

spr_value = spr(effective_stack, pot_flop)

geo_turn = geometric_turn(effective_stack, pot_flop)
geo_river = geometric_river(effective_stack, pot_flop)

# =========================
# OUTPUTS & STRATEGY
# =========================

st.subheader("Outputs & Strategy")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        label="🎯 Target Bounty Value",
        value=f"{bounty_bb:.2f} BB",
        help="Added to the effective pot."
    )

with col2:
    st.metric(
        label="📊 Stack-to-Pot Ratio (SPR)",
        value=f"{spr_value:.2f}",
        help="SPR < 4: Commit with top pair+"
    )

st.divider()

st.markdown("### 🤔 Required Equity to Call")

c1, c2 = st.columns(2)
with c1:
    st.metric(
        "Without Bounty",
        f"{pot_odds_std:.1f}%"
    )
with c2:
    st.metric(
        "With Bounty",
        f"{pot_odds_bounty:.1f}%",
        delta="Equity Discount",
        delta_color="inverse"
    )

st.caption(
    f"Call if your hand's equity > {pot_odds_bounty:.1f}%"
)

st.divider()

st.markdown("### 📐 All-In Geometric Sizing (from Flop)")

c3, c4 = st.columns(2)
with c3:
    st.metric(
        "To Go All-In on TURN",
        f"Bet {geo_turn:.1f}% of Flop Pot"
    )
with c4:
    st.metric(
        "To Go All-In on RIVER",
        f"Bet {geo_river:.1f}% of Flop Pot"
    )
