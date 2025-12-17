import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="Space KO Calculator",
    page_icon="🛸",
    layout="centered"
)

# --- Custom CSS for Poker Interface ---
# This makes the numbers big and readable for "glance value" while multi-tabling
st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .cash-value {
        color: #2ecc71; /* Green for Cash */
        font-size: 40px;
        font-weight: 800;
    }
    .total-value {
        color: #3498db; /* Blue for Total Equity */
        font-size: 24px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 35px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🛸 SPACE KO Bounty converter")
st.caption("Winamax SPACE KO • Live BB Conversion")

# --- Sidebar: Tournament Config ---
with st.sidebar:
    st.header("⚙️ Tournament Setup")
    st.info("Set these once at the start of the session.")
    buy_in = st.number_input("Tournament Buy-in (€)", value=10.0, step=5.0, format="%.2f")
    start_stack = st.number_input("Starting Stack (Chips)", value=20000, step=1000)
    
    # Calculate Chip Value constant
    if start_stack > 0:
        chip_value = buy_in / start_stack
        st.markdown(f"**Chip Value:** `€{chip_value:.6f}` / chip")
    else:
        chip_value = 0

# --- Main Interface ---

# 1. Game State Inputs (The things that change)
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Blinds")
    current_bb = st.number_input(
        "Current BB (Chips)", 
        value=1000, 
        step=100, 
        help="Enter the current Big Blind amount (e.g. 1000 for 500/1000)"
    )

with col2:
    st.subheader("2. Villain Token")
    bounty_euro = st.number_input(
        "Token Avg Value (€)", 
        value=5.0, 
        step=0.5,
        format="%.2f",
        help="Look at the 'Avg' value on opponent's token"
    )

st.markdown("---")

# --- The Calculation Engine ---
if current_bb > 0 and start_stack > 0:
    # A. Cost of 1 BB in Real Money
    bb_cost_euro = current_bb * chip_value
    
    # B. Conversion: How many BBs can we buy with the Bounty Value?
    total_bounty_bb = bounty_euro / bb_cost_euro
    
    # C. Space KO Rule: 50% Cash, 50% Value to Token
    cash_bb = total_bounty_bb * 0.5
    
    # --- Display Results ---
    
    # Primary Result: IMMEDIATE CASH (For Pot Odds)
    st.markdown("### ⚡ Decision Helper")
    
    c1, c2 = st.columns([1.5, 1])
    
    with c1:
        st.markdown('<p class="total-value">Immediate Cash Value</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="cash-value">{cash_bb:.1f} BB</p>', unsafe_allow_html=True)
        st.caption(f"Add this to the pot size when calculating calling odds.")
        
    with c2:
        st.metric(label="Total Equity Value", value=f"{total_bounty_bb:.1f} BB")
        st.caption("Full value (Cash + Your Token Increase)")

    # --- Debug / Verification Strip ---
    with st.expander("Show Calculation Details"):
        st.write(f"**1 Big Blind Cost:** €{bb_cost_euro:.4f}")
        st.write(f"**Formula:** €{bounty_euro} / €{bb_cost_euro:.4f} = {total_bounty_bb:.2f} BB")
        st.write("**Space KO Split:**")
        st.write(f"- Pocket Cash: {cash_bb:.2f} BB")
        st.write(f"- Added to your Token: {cash_bb:.2f} BB")

else:
    st.warning("Please verify your tournament inputs in the sidebar.")
