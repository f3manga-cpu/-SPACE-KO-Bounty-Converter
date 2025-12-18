import tkinter as tk
from tkinter import ttk, messagebox
import math

class SpaceKOCalculator:
    """
    Core calculation engine for Space KO poker tournaments.
    All calculations account for the 50% immediate bounty structure.
    """
    
    def __init__(self, buyin, starting_stack):
        self.buyin = buyin
        self.starting_stack = starting_stack
        # In Space KO: 40% goes to MTT prize pool, 50% to bounties, 10% rake
        # Chip value based on MTT portion only
        self.chip_value_per_euro = starting_stack / (buyin * 0.4)
    
    def calculate_bounty_chips(self, villain_bounty):
        """
        Calculate immediate bounty value in chips.
        Only 50% of bounty is immediate cash (dead money).
        """
        immediate_bounty_euros = villain_bounty / 2
        return immediate_bounty_euros * self.chip_value_per_euro
    
    def calculate_bounty_in_bb(self, villain_bounty, current_bb):
        """Convert immediate bounty to big blinds."""
        bounty_chips = self.calculate_bounty_chips(villain_bounty)
        return bounty_chips / current_bb if current_bb > 0 else 0
    
    def calculate_pot_odds(self, pot_size, bet_to_call, villain_bounty):
        """
        Calculate required equity with and without bounty consideration.
        Returns: (equity_with_bounty, equity_without_bounty, bargain)
        """
        bounty_chips = self.calculate_bounty_chips(villain_bounty)
        
        # Without bounty
        if bet_to_call + pot_size == 0:
            equity_no_bounty = 0
        else:
            equity_no_bounty = (bet_to_call / (bet_to_call + pot_size)) * 100
        
        # With bounty (add bounty to pot)
        total_pot_with_bounty = pot_size + bounty_chips
        if bet_to_call + total_pot_with_bounty == 0:
            equity_with_bounty = 0
        else:
            equity_with_bounty = (bet_to_call / (bet_to_call + total_pot_with_bounty)) * 100
        
        bargain = equity_no_bounty - equity_with_bounty
        
        return equity_with_bounty, equity_no_bounty, bargain
    
    def calculate_spr(self, effective_stack, pot_size):
        """Calculate Stack-to-Pot Ratio."""
        if pot_size == 0:
            return float('inf')
        return effective_stack / pot_size
    
    def get_spr_risk_level(self, spr):
        """Categorize SPR risk level."""
        if spr < 1:
            return "Very Low"
        elif spr < 3:
            return "Low"
        elif spr < 6:
            return "Medium"
        elif spr < 13:
            return "High"
        else:
            return "Very High"
    
    def calculate_geometric_sizing(self, effective_stack, pot_size, streets_remaining):
        """
        Calculate geometric bet size to set up all-in on next street.
        Formula: bet = (target_pot - current_pot) / 2
        where target_pot = effective_stack (for all-in)
        """
        if streets_remaining <= 0 or pot_size <= 0:
            return None, None
        
        # For going all-in on next street, we need:
        # After our bet: new_pot = pot + bet
        # After opponent calls: new_pot = pot + 2*bet
        # We want: effective_stack = bet_on_next_street
        # And: new_pot = effective_stack (to go all-in)
        
        # So: pot + 2*bet = effective_stack
        # Therefore: bet = (effective_stack - pot) / 2
        
        bet_size = (effective_stack - pot_size) / 2
        
        if bet_size <= 0 or bet_size > effective_stack:
            return None, None
        
        bet_percentage = (bet_size / pot_size) * 100 if pot_size > 0 else 0
        
        return bet_size, bet_percentage


class SpaceKOApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Space KO Poker Companion")
        self.root.geometry("700x650")
        self.root.resizable(False, False)
        
        self.calculator = None
        
        # Color scheme
        self.bg_color = "#1a1a2e"
        self.fg_color = "#eee"
        self.accent_color = "#16213e"
        self.highlight_color = "#0f3460"
        self.green_color = "#00ff88"
        self.yellow_color = "#ffd700"
        self.red_color = "#ff4444"
        
        self.root.configure(bg=self.bg_color)
        
        self.setup_styles()
        self.create_config_section()
        self.create_hand_section()
        self.create_results_section()
        
    def setup_styles(self):
        """Configure ttk styles for consistent appearance."""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Title.TLabel', 
                       background=self.bg_color, 
                       foreground=self.green_color,
                       font=('Arial', 14, 'bold'))
        
        style.configure('Normal.TLabel',
                       background=self.bg_color,
                       foreground=self.fg_color,
                       font=('Arial', 10))
        
        style.configure('TEntry',
                       fieldbackground=self.accent_color,
                       foreground=self.fg_color,
                       borderwidth=2)
        
        style.configure('TButton',
                       background=self.highlight_color,
                       foreground=self.fg_color,
                       borderwidth=1,
                       font=('Arial', 10, 'bold'))
        
    def create_config_section(self):
        """Tournament configuration section (set once per session)."""
        config_frame = tk.Frame(self.root, bg=self.accent_color, relief=tk.RIDGE, bd=2)
        config_frame.pack(padx=10, pady=10, fill=tk.X)
        
        title = ttk.Label(config_frame, text="⚙ TOURNAMENT SETTINGS", style='Title.TLabel')
        title.grid(row=0, column=0, columnspan=4, pady=10)
        
        # Buy-in
        ttk.Label(config_frame, text="Buy-in (€):", style='Normal.TLabel').grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.buyin_var = tk.StringVar(value="10")
        self.buyin_entry = ttk.Entry(config_frame, textvariable=self.buyin_var, width=12)
        self.buyin_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Starting stack
        ttk.Label(config_frame, text="Starting Stack:", style='Normal.TLabel').grid(row=1, column=2, padx=10, pady=5, sticky=tk.W)
        self.stack_var = tk.StringVar(value="20000")
        self.stack_entry = ttk.Entry(config_frame, textvariable=self.stack_var, width=12)
        self.stack_entry.grid(row=1, column=3, padx=10, pady=5)
        
        # Initialize button
        init_btn = ttk.Button(config_frame, text="Initialize Calculator", command=self.initialize_calculator)
        init_btn.grid(row=2, column=0, columnspan=4, pady=10)
        
    def create_hand_section(self):
        """Hand-specific inputs section."""
        hand_frame = tk.Frame(self.root, bg=self.accent_color, relief=tk.RIDGE, bd=2)
        hand_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        title = ttk.Label(hand_frame, text="🎯 HAND ANALYSIS", style='Title.TLabel')
        title.grid(row=0, column=0, columnspan=4, pady=10)
        
        # Row 1: Stacks
        ttk.Label(hand_frame, text="Our Stack:", style='Normal.TLabel').grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.our_stack_var = tk.StringVar(value="")
        ttk.Entry(hand_frame, textvariable=self.our_stack_var, width=12).grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(hand_frame, text="Villain Stack:", style='Normal.TLabel').grid(row=1, column=2, padx=10, pady=5, sticky=tk.W)
        self.villain_stack_var = tk.StringVar(value="")
        ttk.Entry(hand_frame, textvariable=self.villain_stack_var, width=12).grid(row=1, column=3, padx=10, pady=5)
        
        # Row 2: Bounty and BB
        ttk.Label(hand_frame, text="Villain Bounty (€):", style='Normal.TLabel').grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.villain_bounty_var = tk.StringVar(value="")
        ttk.Entry(hand_frame, textvariable=self.villain_bounty_var, width=12).grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(hand_frame, text="Current BB:", style='Normal.TLabel').grid(row=2, column=2, padx=10, pady=5, sticky=tk.W)
        self.current_bb_var = tk.StringVar(value="")
        ttk.Entry(hand_frame, textvariable=self.current_bb_var, width=12).grid(row=2, column=3, padx=10, pady=5)
        
        # Row 3: Pot and Bet
        ttk.Label(hand_frame, text="Pot Size:", style='Normal.TLabel').grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        self.pot_var = tk.StringVar(value="")
        ttk.Entry(hand_frame, textvariable=self.pot_var, width=12).grid(row=3, column=1, padx=10, pady=5)
        
        ttk.Label(hand_frame, text="Bet to Call:", style='Normal.TLabel').grid(row=3, column=2, padx=10, pady=5, sticky=tk.W)
        self.bet_var = tk.StringVar(value="")
        ttk.Entry(hand_frame, textvariable=self.bet_var, width=12).grid(row=3, column=3, padx=10, pady=5)
        
        # Row 4: Street selection
        ttk.Label(hand_frame, text="Current Street:", style='Normal.TLabel').grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        self.street_var = tk.StringVar(value="Flop")
        street_combo = ttk.Combobox(hand_frame, textvariable=self.street_var, 
                                    values=["Flop", "Turn", "River"], state="readonly", width=10)
        street_combo.grid(row=4, column=1, padx=10, pady=5)
        
        # Calculate button
        calc_btn = ttk.Button(hand_frame, text="CALCULATE", command=self.calculate)
        calc_btn.grid(row=5, column=0, columnspan=2, pady=15, padx=10, sticky=tk.EW)
        
        # Clear button
        clear_btn = ttk.Button(hand_frame, text="CLEAR HAND", command=self.clear_hand)
        clear_btn.grid(row=5, column=2, columnspan=2, pady=15, padx=10, sticky=tk.EW)
        
        # Bind all entry fields to auto-calculate on change
        for var in [self.our_stack_var, self.villain_stack_var, self.villain_bounty_var,
                    self.current_bb_var, self.pot_var, self.bet_var]:
            var.trace('w', lambda *args: self.auto_calculate())
        
    def create_results_section(self):
        """Results display section."""
        results_frame = tk.Frame(self.root, bg=self.highlight_color, relief=tk.RIDGE, bd=2)
        results_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        title = ttk.Label(results_frame, text="📊 SPACE KO ANALYSIS", style='Title.TLabel')
        title.pack(pady=10)
        
        # Results text widget
        self.results_text = tk.Text(results_frame, 
                                    height=12, 
                                    bg=self.accent_color, 
                                    fg=self.fg_color,
                                    font=('Courier', 11, 'bold'),
                                    relief=tk.SUNKEN,
                                    bd=2)
        self.results_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Configure text tags for color coding
        self.results_text.tag_config('green', foreground=self.green_color)
        self.results_text.tag_config('yellow', foreground=self.yellow_color)
        self.results_text.tag_config('red', foreground=self.red_color)
        self.results_text.tag_config('header', foreground=self.green_color, font=('Courier', 12, 'bold'))
        
    def initialize_calculator(self):
        """Initialize calculator with tournament settings."""
        try:
            buyin = float(self.buyin_var.get())
            starting_stack = float(self.stack_var.get())
            
            if buyin <= 0 or starting_stack <= 0:
                raise ValueError("Values must be positive")
            
            self.calculator = SpaceKOCalculator(buyin, starting_stack)
            messagebox.showinfo("Success", f"Calculator initialized!\n\nChip value: {self.calculator.chip_value_per_euro:.0f} chips per €")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
    
    def auto_calculate(self):
        """Auto-calculate when all required fields are filled."""
        # Check if all required fields have values
        if (self.calculator and 
            self.villain_bounty_var.get() and 
            self.current_bb_var.get() and
            self.pot_var.get()):
            self.calculate()
    
    def calculate(self):
        """Perform all calculations and display results."""
        if not self.calculator:
            messagebox.showwarning("Warning", "Please initialize calculator with tournament settings first!")
            return
        
        try:
            # Get inputs
            our_stack = float(self.our_stack_var.get()) if self.our_stack_var.get() else 0
            villain_stack = float(self.villain_stack_var.get()) if self.villain_stack_var.get() else 0
            villain_bounty = float(self.villain_bounty_var.get())
            current_bb = float(self.current_bb_var.get())
            pot_size = float(self.pot_var.get())
            bet_to_call = float(self.bet_var.get()) if self.bet_var.get() else 0
            street = self.street_var.get()
            
            # Validate inputs
            if villain_bounty < 0 or current_bb <= 0 or pot_size < 0:
                raise ValueError("Invalid input values")
            
            # Calculate bounty value
            bounty_bb = self.calculator.calculate_bounty_in_bb(villain_bounty, current_bb)
            bounty_chips = self.calculator.calculate_bounty_chips(villain_bounty)
            
            # Calculate pot odds
            equity_with, equity_without, bargain = self.calculator.calculate_pot_odds(
                pot_size, bet_to_call, villain_bounty
            )
            
            # Calculate SPR
            effective_stack = min(our_stack, villain_stack) if our_stack > 0 and villain_stack > 0 else 0
            spr = self.calculator.calculate_spr(effective_stack, pot_size) if effective_stack > 0 else 0
            spr_risk = self.calculator.get_spr_risk_level(spr)
            
            # Calculate geometric sizing
            streets_map = {"Flop": 2, "Turn": 1, "River": 0}
            streets_remaining = streets_map[street]
            geo_bet, geo_pct = None, None
            
            if effective_stack > 0 and streets_remaining > 0:
                geo_bet, geo_pct = self.calculator.calculate_geometric_sizing(
                    effective_stack, pot_size, streets_remaining
                )
            
            # Display results
            self.display_results(bounty_bb, bounty_chips, equity_with, equity_without, 
                               bargain, spr, spr_risk, geo_bet, geo_pct, street, 
                               bet_to_call, pot_size)
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
    
    def display_results(self, bounty_bb, bounty_chips, equity_with, equity_without, 
                       bargain, spr, spr_risk, geo_bet, geo_pct, street, 
                       bet_to_call, pot_size):
        """Display formatted results with color coding."""
        self.results_text.delete(1.0, tk.END)
        
        # Header
        self.results_text.insert(tk.END, "═══════════════════════════════════════════\n", 'header')
        self.results_text.insert(tk.END, "           SPACE KO ANALYSIS\n", 'header')
        self.results_text.insert(tk.END, "═══════════════════════════════════════════\n\n", 'header')
        
        # Bounty Value
        self.results_text.insert(tk.END, "💰 BOUNTY VALUE\n", 'green')
        self.results_text.insert(tk.END, f"   {bounty_bb:.1f} BB ", 'green')
        self.results_text.insert(tk.END, f"({bounty_chips:,.0f} chips)\n\n")
        
        # Pot Odds
        if bet_to_call > 0:
            self.results_text.insert(tk.END, "🎯 EQUITY REQUIRED\n")
            
            # Color code based on bargain
            equity_color = 'green' if bargain > 5 else 'yellow' if bargain > 2 else 'white'
            
            self.results_text.insert(tk.END, f"   With bounty:  ", 'yellow')
            self.results_text.insert(tk.END, f"{equity_with:.1f}%\n", equity_color)
            self.results_text.insert(tk.END, f"   No bounty:    {equity_without:.1f}%\n")
            self.results_text.insert(tk.END, f"   Bargain:      ", 'green')
            self.results_text.insert(tk.END, f"+{bargain:.1f}%", 'green')
            self.results_text.insert(tk.END, " equity discount\n\n")
            
            # Pot odds ratio
            if pot_size > 0:
                pot_odds_ratio = (pot_size + bounty_chips) / bet_to_call
                self.results_text.insert(tk.END, f"   Pot odds:     {pot_odds_ratio:.2f}:1\n\n")
        
        # SPR
        if spr > 0:
            self.results_text.insert(tk.END, "📊 STACK-TO-POT RATIO\n")
            
            # Color code SPR risk
            if spr < 3:
                spr_color = 'green'
            elif spr < 6:
                spr_color = 'yellow'
            else:
                spr_color = 'red'
            
            self.results_text.insert(tk.END, f"   SPR: {spr:.2f}  ", spr_color)
            self.results_text.insert(tk.END, f"[{spr_risk} commitment]\n\n", spr_color)
        
        # Geometric Sizing
        if geo_bet and geo_pct:
            next_street = "Turn" if street == "Flop" else "River"
            self.results_text.insert(tk.END, "📐 GEOMETRIC BET SIZING\n", 'yellow')
            self.results_text.insert(tk.END, f"   To go all-in {next_street}:\n")
            self.results_text.insert(tk.END, f"   Bet {geo_bet:,.0f} chips ", 'yellow')
            self.results_text.insert(tk.END, f"({geo_pct:.0f}% pot)\n\n")
        
        self.results_text.insert(tk.END, "═══════════════════════════════════════════\n", 'header')
    
    def clear_hand(self):
        """Clear hand-specific inputs while keeping tournament settings."""
        self.our_stack_var.set("")
        self.villain_stack_var.set("")
        self.villain_bounty_var.set("")
        self.current_bb_var.set("")
        self.pot_var.set("")
        self.bet_var.set("")
        self.street_var.set("Flop")
        self.results_text.delete(1.0, tk.END)


def main():
    root = tk.Tk()
    app = SpaceKOApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
