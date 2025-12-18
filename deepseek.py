import streamlit as st
import numpy as np
from math import isclose

# Page configuration
st.set_page_config(
    page_title="SPACE KO Strategy Calculator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4A00E0;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #4A00E0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .metric-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #4A00E0;
    }
    .metric-subtext {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .green-highlight {
        color: #00C853;
        font-weight: 700;
    }
    .section-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: #4A00E0;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E0E0E0;
    }
    .stNumberInput > div > div > input {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">🎯 SPACE KO Bounty Strategy Calculator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Convert bounty € values to BBs and optimize your Winamax tournament decisions</div>', unsafe_allow_html=True)

# Initialize session state for performance
if 'prev_values' not in st.session_state:
    st.session_state.prev_values = {}

# SIDEBAR - Tournament Setup
with st.sidebar:
    st.markdown("## 🏆 Tournament Setup")
    st.markdown("*Static configuration - set once per tournament*")
    
    col1, col2 = st.columns(2)
    with col1:
        buy_in = st.number_input(
            "Tournament Buy-in (€)",
            min_value=0.01,
            value=10.0,
            step=0.01,
            format="%.2f",
            help="Total buy-in including rake"
        )
    with col2:
        starting_stack = st.number_input(
            "Starting Stack (Chips)",
            min_value=1,
            value=20000,
            step=1000,
            help="Standard Winamax starting stack: 20,000 chips"
        )
    
    st.markdown("---")
    st.markdown("### 💡 How it works")
    st.info("""
    1. **50%** of buy-in → Bounty pool  
    2. **40%** → Regular prize pool  
    3. **10%** → Rake
    
    Starting bounty token value = **50% of buy-in**
    """)
    
    st.markdown("---")
    st.warning("⚠️ **Note**: Values here set the chip-to-euro exchange rate. Adjust only when starting a new tournament.")

# MAIN PANEL - Hand Inputs
col_main1, col_main2 = st.columns([1, 1])

with col_main1:
    st.markdown('<div class="section-header">📥 Hand Inputs</div>', unsafe_allow_html=True)
    
    # Essential Bounty Conversion
    st.markdown("#### Essential Bounty Conversion")
    
    current_bb = st.number_input(
        "Current Big Blind (Chips)",
        min_value=1,
        value=200,
        step=10,
        key="current_bb",
        help="The current big blind level in chips"
    )
    
    token_avg_eur = st.number_input(
        "Villain's Token - Average Value (€)",
        min_value=0.0,
        value=5.0,
        step=0.1,
        format="%.2f",
        key="token_value",
        help="Click on any opponent's token in your client to see this value"
    )
    
    # Advanced Section
    with st.expander("⚙️ **Advanced: Pot & Bet Analysis**", expanded=False):
        st.markdown("#### Pot & Stack Information")
        
        pot_before = st.number_input(
            "Pot Size Before Facing Bet (BB)",
            min_value=0.0,
            value=10.0,
            step=0.5,
            key="pot_before",
            help="Pot size in big blinds before you need to act"
        )
        
        amount_to_call = st.number_input(
            "Amount to Call (BB)",
            min_value=0.0,
            value=5.0,
            step=0.5,
            key="amount_to_call",
            help="How many BB you need to call to continue"
        )
        
        st.markdown("#### Flop Analysis")
        
        pot_on_flop = st.number_input(
            "Pot on Flop (BB)",
            min_value=0.0,
            value=10.0,
            step=0.5,
            key="pot_on_flop",
            help="Total pot size on the flop in BB"
        )
        
        effective_stack = st.number_input(
            "Effective Stack Behind (BB)",
            min_value=0.0,
            value=50.0,
            step=1.0,
            key="effective_stack",
            help="Smaller of your or opponent's remaining stack on flop"
        )

# CALCULATION FUNCTIONS
def calculate_bounty_in_bb(buy_in, starting_stack, current_bb, token_avg_eur):
    """Calculate bounty value in big blinds"""
    chip_value_eur = buy_in / starting_stack
    one_bb_in_eur = current_bb * chip_value_eur
    if one_bb_in_eur == 0:
        return 0
    return token_avg_eur / one_bb_in_eur

def calculate_required_equity(pot_before, amount_to_call, bounty_bb=0):
    """Calculate required equity to call with and without bounty"""
    if amount_to_call == 0:
        return 0, 0
    
    # Standard pot odds
    pot_odds_standard = amount_to_call / (pot_before + amount_to_call)
    
    # With bounty added to pot
    pot_odds_with_bounty = amount_to_call / (pot_before + amount_to_call + bounty_bb)
    
    return pot_odds_standard * 100, pot_odds_with_bounty * 100

def calculate_spr(effective_stack, pot_on_flop):
    """Calculate Stack-to-Pot Ratio"""
    if pot_on_flop == 0:
        return 0
    return effective_stack / pot_on_flop

def calculate_geometric_sizing(effective_stack, pot_on_flop, streets=2):
    """
    Calculate geometric bet sizing for all-in on turn (2 streets) or river (3 streets)
    Returns bet size as percentage of pot
    """
    if pot_on_flop == 0:
        return 0
    
    ratio = effective_stack / pot_on_flop
    
    if streets == 2:  # All-in on turn
        # Solve: ratio = 2r + 2r^2
        # Rearranged: 2r^2 + 2r - ratio = 0
        a, b, c = 2, 2, -ratio
        discriminant = b**2 - 4*a*c
        
        if discriminant < 0:
            return 0
        
        r1 = (-b + np.sqrt(discriminant)) / (2*a)
        r2 = (-b - np.sqrt(discriminant)) / (2*a)
        
        # Take positive solution between 0 and 2
        r = max(r1, r2) if r1 >= 0 and r1 <= 2 else r2
        return max(0, min(r * 100, 200))
    
    elif streets == 3:  # All-in on river
        # Solve cubic: 4r^3 + 6r^2 + 3r - ratio = 0
        coeffs = [4, 6, 3, -ratio]
        roots = np.roots(coeffs)
        
        # Find real root between 0 and 2
        for root in roots:
            if np.isreal(root) and 0 <= root.real <= 2:
                return max(0, min(root.real * 100, 200))
        
        return 0

# Perform calculations
bounty_bb = calculate_bounty_in_bb(buy_in, starting_stack, current_bb, token_avg_eur)
eq_standard, eq_with_bounty = calculate_required_equity(pot_before, amount_to_call, bounty_bb)
spr_value = calculate_spr(effective_stack, pot_on_flop)
geo_turn = calculate_geometric_sizing(effective_stack, pot_on_flop, streets=2)
geo_river = calculate_geometric_sizing(effective_stack, pot_on_flop, streets=3)

# MAIN PANEL - Outputs
with col_main2:
    st.markdown('<div class="section-header">📊 Strategy Outputs</div>', unsafe_allow_html=True)
    
    # Output Card 1: BOUNTY VALUE
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-title">🎯 Target Bounty Value</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{bounty_bb:.1f} BB</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-subtext">Added to the effective pot when calling</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Display euro value for reference
        st.markdown("**Token Value**")
        st.markdown(f"**{token_avg_eur:.2f} €**")
        st.markdown(f"*{bounty_bb/100:.1f}% of stack*")
    
    st.markdown("---")
    
    # Output Card 2: EQUITY BARGAIN
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<div class="metric-title">🤔 Required Equity to Call</div>', unsafe_allow_html=True)
    
    equity_col1, equity_col2 = st.columns(2)
    with equity_col1:
        st.markdown("**Without Bounty**")
        st.markdown(f"### {eq_standard:.1f}%")
    
    with equity_col2:
        st.markdown("**<span class='green-highlight'>With Bounty</span>**", unsafe_allow_html=True)
        st.markdown(f"### <span class='green-highlight'>{eq_with_bounty:.1f}%</span>", unsafe_allow_html=True)
    
    # Calculate equity reduction
    equity_reduction = eq_standard - eq_with_bounty
    if equity_reduction > 0:
        st.markdown(f'<div class="metric-subtext">Bounty reduces required equity by <strong>{equity_reduction:.1f}%</strong>. Call if your hand\'s equity > {eq_with_bounty:.1f}%</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="metric-subtext">Call if your hand\'s equity > {eq_with_bounty:.1f}%</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Output Cards 3 & 4 in columns
    col3, col4 = st.columns(2)
    
    with col3:
        # Output Card 3: GEOMETRIC BET SIZING
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-title">📐 Geometric Sizing (from Flop)</div>', unsafe_allow_html=True)
        
        if effective_stack > 0 and pot_on_flop > 0:
            geo_col1, geo_col2 = st.columns(2)
            with geo_col1:
                st.markdown("**All-in on TURN**")
                st.markdown(f"### {geo_turn:.1f}%")
                st.caption(f"Bet {geo_turn:.1f}% of pot")
            
            with geo_col2:
                st.markdown("**All-in on RIVER**")
                st.markdown(f"### {geo_river:.1f}%")
                st.caption(f"Bet {geo_river:.1f}% of pot")
            
            # Interpretation
            if geo_turn > 66:
                interpretation = "Large sizing needed → Polarized range"
            elif geo_turn > 33:
                interpretation = "Standard sizing → Balanced range"
            else:
                interpretation = "Small sizing → Linear range"
            
            st.markdown(f'<div class="metric-subtext">{interpretation}</div>', unsafe_allow_html=True)
        else:
            st.markdown("*Enter stack & pot values*")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        # Output Card 4: STACK TO POT RATIO
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-title">📊 Stack-to-Pot Ratio (SPR)</div>', unsafe_allow_html=True)
        
        if spr_value > 0:
            st.markdown(f'<div class="metric-value">{spr_value:.1f}</div>', unsafe_allow_html=True)
            
            # SPR Interpretation
            if spr_value < 2:
                interpretation = "🟢 **Very Low SPR**: Commit with top pair+, draws"
                advice = "Easy to get all-in, play aggressively"
            elif spr_value < 4:
                interpretation = "🟡 **Low SPR**: Commit with strong hands"
                advice = "Can commit with top pair good kicker+"
            elif spr_value < 10:
                interpretation = "🟠 **Medium SPR**: Play cautiously"
                advice = "Consider pot control, avoid bloating with marginal hands"
            else:
                interpretation = "🔴 **High SPR**: Play for stacks only with nuts"
                advice = "Deep stack poker, implied odds important"
            
            st.markdown(f'<div class="metric-subtext">{interpretation}<br>{advice}</div>', unsafe_allow_html=True)
        else:
            st.markdown("*Enter stack & pot values*")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Additional Info & Footer
st.markdown("---")
col_info1, col_info2, col_info3 = st.columns(3)

with col_info1:
    with st.expander("📈 **Current Exchange Rate**"):
        chip_value = buy_in / starting_stack
        st.metric("Chip Value", f"{chip_value:.4f} €")
        st.metric("1 BB Value", f"{current_bb * chip_value:.2f} €")
        st.caption(f"Based on {buy_in}€ / {starting_stack:,} chips")

with col_info2:
    with st.expander("🎯 **Bounty Value Insights**"):
        starting_bounty = buy_in * 0.5  # 50% of buy-in
        st.metric("Starting Bounty", f"{starting_bounty:.2f} €")
        
        if token_avg_eur > 0:
            multiplier = token_avg_eur / starting_bounty
            st.metric("Bounty Multiplier", f"{multiplier:.1f}x")
            
            if multiplier > 1.5:
                st.success("High value bounty - adjust strategy!")
            elif multiplier < 0.7:
                st.warning("Low value bounty - play standard")

with col_info3:
    with st.expander("⚡ **Quick Tips**"):
        st.markdown("""
        - **Bounties > 1BB**: Significantly change pot odds
        - **Low SPR + Bounty**: More inclined to commit
        - **Heads-up**: Bounty value is pure EV gain
        - **Multi-way**: Bounty equity is shared
        """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <i>SPACE KO Strategy Calculator • Built for Winamax tournaments • Updates in real-time</i><br>
    <i>Remember: Bounties change fundamental poker math. Adjust your ranges accordingly!</i>
    </div>
    """,
    unsafe_allow_html=True
)

# Performance optimization note
st.session_state.prev_values = {
    'buy_in': buy_in,
    'starting_stack': starting_stack,
    'current_bb': current_bb,
    'token_avg_eur': token_avg_eur
}
