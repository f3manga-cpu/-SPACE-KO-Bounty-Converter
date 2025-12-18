import React, { useState, useMemo } from 'react';
import { Calculator, Trophy, Target, TrendingUp, Info, RotateCcw } from 'lucide-react';

// Token level constants from documentation
const TOKEN_LEVELS = [
  { level: 1, multiplier: 0.5, avgValue: (buyIn) => buyIn * 0.5, min: (buyIn) => buyIn * 0.2, max: (buyIn) => buyIn * 50 },
  { level: 2, multiplier: 0.6, avgValue: (buyIn) => buyIn * 0.6 },
  { level: 3, multiplier: 0.75, avgValue: (buyIn) => buyIn * 0.75 },
  { level: 4, multiplier: 1, avgValue: (buyIn) => buyIn * 1 },
  { level: 5, multiplier: 1.5, avgValue: (buyIn) => buyIn * 1.5 },
  { level: 6, multiplier: 2.5, avgValue: (buyIn) => buyIn * 2.5 },
  { level: 7, multiplier: 5, avgValue: (buyIn) => buyIn * 5 },
  { level: 8, multiplier: 10, avgValue: (buyIn) => buyIn * 10 },
  { level: 9, multiplier: 20, avgValue: (buyIn) => buyIn * 20 },
  { level: 10, multiplier: 50, avgValue: (buyIn) => buyIn * 50 },
  { level: 11, fixedMin: 10000 },
  { level: 12, fixedMin: 100000 },
  { level: 13, fixedMin: 333333 },
  { level: 14, fixedMin: 500000 },
];

const SpaceKOCompanion = () => {
  // Tournament Setup (Static)
  const [buyIn, setBuyIn] = useState(10);
  const [startingStack, setStartingStack] = useState(20000);
  const [bbSize, setBbSize] = useState(400);
  const [selectedTokenLevel, setSelectedTokenLevel] = useState(1);

  // Hand Details (Dynamic)
  const [villainStack, setVillainStack] = useState(15000);
  const [villainBounty, setVillainBounty] = useState(10);
  const [heroStack, setHeroStack] = useState(18000);
  const [currentPot, setCurrentPot] = useState(1200);
  const [amountToCall, setAmountToCall] = useState(800);
  const [potOnFlop, setPotOnFlop] = useState(1600);

  const [showResults, setShowResults] = useState(false);

  // Core Calculations
  const calculations = useMemo(() => {
    // Bounty to BB Conversion
    const chipValueEur = buyIn / startingStack;
    const bountyChips = villainBounty / chipValueEur;
    const bountyBB = bountyChips / bbSize;

    // Pot Odds with Bounty Adjustment
    const standardEquityReq = (amountToCall / (currentPot + amountToCall)) * 100;
    const bountyAdjustedPot = currentPot + bountyChips;
    const bountyEquityReq = (amountToCall / (bountyAdjustedPot + amountToCall)) * 100;
    const equityBargain = standardEquityReq - bountyEquityReq;

    // SPR Calculation
    const effectiveStack = Math.min(heroStack, villainStack);
    const spr = effectiveStack / potOnFlop;
    
    let sprStrategy = "";
    let sprColor = "";
    if (spr <= 3) {
      sprStrategy = "Commitment Zone - Consider shoving or calling shoves";
      sprColor = "bg-red-100 border-red-300 text-red-900";
    } else if (spr <= 10) {
      sprStrategy = "Standard Play - Balance value and bluff";
      sprColor = "bg-yellow-100 border-yellow-300 text-yellow-900";
    } else {
      sprStrategy = "Pot Control - Consider smaller bets or checking";
      sprColor = "bg-green-100 border-green-300 text-green-900";
    }

    // Geometric Bet Sizing - All-in by Turn
    const flopBetTurn = (effectiveStack - potOnFlop) / 3;
    const turnBetTurn = effectiveStack - flopBetTurn;
    const flopBetTurnPct = (flopBetTurn / potOnFlop) * 100;

    // Geometric Bet Sizing - All-in by River
    const r = (Math.sqrt(4 * effectiveStack / potOnFlop + 1) - 1) / 2;
    const flopBetRiver = r * potOnFlop;
    const turnBetRiver = r * (potOnFlop + 2 * flopBetRiver);
    const flopBetRiverPct = (flopBetRiver / potOnFlop) * 100;

    return {
      bountyBB: bountyBB.toFixed(2),
      bountyEur: villainBounty.toFixed(2),
      standardEquityReq: standardEquityReq.toFixed(1),
      bountyEquityReq: bountyEquityReq.toFixed(1),
      equityBargain: equityBargain.toFixed(1),
      bargainColor: equityBargain > 2 ? 'text-green-600' : equityBargain > 0 ? 'text-yellow-600' : 'text-red-600',
      spr: spr.toFixed(2),
      sprStrategy,
      sprColor,
      flopBetTurn: Math.round(flopBetTurn),
      flopBetTurnPct: flopBetTurnPct.toFixed(0),
      turnBetTurn: Math.round(turnBetTurn),
      flopBetRiver: Math.round(flopBetRiver),
      flopBetRiverPct: flopBetRiverPct.toFixed(0),
      turnBetRiver: Math.round(turnBetRiver),
    };
  }, [buyIn, startingStack, bbSize, villainBounty, villainStack, heroStack, currentPot, amountToCall, potOnFlop]);

  const handleCalculate = () => {
    setShowResults(true);
  };

  const handleReset = () => {
    setVillainStack(15000);
    setVillainBounty(10);
    setHeroStack(18000);
    setCurrentPot(1200);
    setAmountToCall(800);
    setPotOnFlop(1600);
    setShowResults(false);
  };

  const handleTokenLevelChange = (level) => {
    setSelectedTokenLevel(level);
    const tokenData = TOKEN_LEVELS[level - 1];
    if (tokenData.fixedMin) {
      setVillainBounty(tokenData.fixedMin);
    } else {
      setVillainBounty(tokenData.avgValue(buyIn));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-t-xl p-6 shadow-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Trophy className="w-10 h-10 text-yellow-300" />
              <div>
                <h1 className="text-3xl font-bold text-white">Space KO Companion</h1>
                <p className="text-purple-200 text-sm">Winamax Tournament Strategy Tool</p>
              </div>
            </div>
            <Calculator className="w-8 h-8 text-purple-200" />
          </div>
        </div>

        <div className="bg-white rounded-b-xl shadow-2xl p-6">
          {/* Tournament Setup */}
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-4">
              <Info className="w-5 h-5 text-blue-600" />
              <h2 className="text-xl font-bold text-gray-800">Tournament Setup</h2>
              <span className="text-xs text-gray-500">(Set once per tournament)</span>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Buy-in (€)</label>
                <input
                  type="number"
                  value={buyIn}
                  onChange={(e) => setBuyIn(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  min="1"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Starting Stack</label>
                <input
                  type="number"
                  value={startingStack}
                  onChange={(e) => setStartingStack(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  min="1"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Current BB Size</label>
                <input
                  type="number"
                  value={bbSize}
                  onChange={(e) => setBbSize(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  min="1"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Token Level Ref</label>
                <select
                  value={selectedTokenLevel}
                  onChange={(e) => handleTokenLevelChange(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  {TOKEN_LEVELS.map((token) => (
                    <option key={token.level} value={token.level}>
                      Level {token.level} {token.fixedMin ? `(€${token.fixedMin.toLocaleString()})` : `(${token.multiplier}x)`}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Hand Details */}
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-4">
              <Target className="w-5 h-5 text-green-600" />
              <h2 className="text-xl font-bold text-gray-800">Hand Details</h2>
              <span className="text-xs text-gray-500">(Update each hand)</span>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Villain Stack</label>
                <input
                  type="number"
                  value={villainStack}
                  onChange={(e) => setVillainStack(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  min="0"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Villain Bounty (€)</label>
                <input
                  type="number"
                  value={villainBounty}
                  onChange={(e) => setVillainBounty(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  min="0"
                  step="0.01"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Hero Stack</label>
                <input
                  type="number"
                  value={heroStack}
                  onChange={(e) => setHeroStack(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  min="0"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Current Pot</label>
                <input
                  type="number"
                  value={currentPot}
                  onChange={(e) => setCurrentPot(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  min="0"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Amount to Call</label>
                <input
                  type="number"
                  value={amountToCall}
                  onChange={(e) => setAmountToCall(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  min="0"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Pot on Flop</label>
                <input
                  type="number"
                  value={potOnFlop}
                  onChange={(e) => setPotOnFlop(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  min="0"
                />
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 mb-6">
            <button
              onClick={handleCalculate}
              className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg flex items-center justify-center gap-2"
            >
              <Calculator className="w-5 h-5" />
              Calculate
            </button>
            <button
              onClick={handleReset}
              className="bg-gray-200 text-gray-700 py-3 px-6 rounded-lg font-semibold hover:bg-gray-300 transition-all flex items-center justify-center gap-2"
            >
              <RotateCcw className="w-5 h-5" />
              Reset Hand
            </button>
          </div>

          {/* Results */}
          {showResults && (
            <div className="space-y-4 animate-fadeIn">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="w-5 h-5 text-purple-600" />
                <h2 className="text-xl font-bold text-gray-800">Results</h2>
              </div>

              {/* Top Row Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Bounty Conversion */}
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 border-2 border-blue-300 rounded-xl p-4 shadow-lg">
                  <h3 className="text-sm font-semibold text-blue-800 mb-2">Bounty Conversion</h3>
                  <div className="text-4xl font-bold text-blue-900">{calculations.bountyBB} BB</div>
                  <div className="text-sm text-blue-700 mt-1">(€{calculations.bountyEur})</div>
                </div>

                {/* Pot Odds Analysis */}
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 border-2 border-purple-300 rounded-xl p-4 shadow-lg">
                  <h3 className="text-sm font-semibold text-purple-800 mb-2">Pot Odds Analysis</h3>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-purple-700">Without bounty:</span>
                      <span className="font-bold text-purple-900">{calculations.standardEquityReq}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-purple-700">With bounty:</span>
                      <span className="font-bold text-purple-900">{calculations.bountyEquityReq}%</span>
                    </div>
                    <div className={`flex justify-between pt-2 border-t border-purple-300 ${calculations.bargainColor} font-bold`}>
                      <span>Bargain:</span>
                      <span>{calculations.equityBargain > 0 ? '-' : '+'}{Math.abs(calculations.equityBargain)}%</span>
                    </div>
                  </div>
                </div>

                {/* SPR */}
                <div className={`border-2 rounded-xl p-4 shadow-lg ${calculations.sprColor}`}>
                  <h3 className="text-sm font-semibold mb-2">Stack-to-Pot Ratio</h3>
                  <div className="text-4xl font-bold mb-2">{calculations.spr}</div>
                  <div className="text-xs font-medium">{calculations.sprStrategy}</div>
                </div>
              </div>

              {/* Geometric Bet Sizing */}
              <div className="bg-gradient-to-br from-green-50 to-green-100 border-2 border-green-300 rounded-xl p-6 shadow-lg">
                <h3 className="text-lg font-bold text-green-900 mb-4">Geometric Bet Sizing</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-white rounded-lg p-4 border border-green-300">
                    <div className="text-sm font-semibold text-green-800 mb-2">Strategy 1: All-in by Turn</div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-700">Flop Bet:</span>
                        <span className="font-bold text-green-900">{calculations.flopBetTurn.toLocaleString()} ({calculations.flopBetTurnPct}% pot)</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">Turn Bet:</span>
                        <span className="font-bold text-green-900">{calculations.turnBetTurn.toLocaleString()} (all-in)</span>
                      </div>
                    </div>
                  </div>
                  <div className="bg-white rounded-lg p-4 border border-green-300">
                    <div className="text-sm font-semibold text-green-800 mb-2">Strategy 2: All-in by River</div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-700">Flop Bet:</span>
                        <span className="font-bold text-green-900">{calculations.flopBetRiver.toLocaleString()} ({calculations.flopBetRiverPct}% pot)</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-700">Turn Bet:</span>
                        <span className="font-bold text-green-900">{calculations.turnBetRiver.toLocaleString()} ({calculations.flopBetRiverPct}% pot)</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Disclaimer */}
              <div className="bg-yellow-50 border border-yellow-300 rounded-lg p-3 text-xs text-yellow-800">
                <strong>Note:</strong> Bounty values shown are averages based on token level. Actual bounty may vary due to random multipliers. Always check opponent's exact bounty value at the table.
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-6 text-center text-purple-200 text-sm">
          <p>Built for Winamax Space KO Tournaments • Always verify bounty values in-game</p>
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};

export default SpaceKOCompanion;
