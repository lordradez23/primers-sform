'use client';

import React from 'react';
import { Shield, TrendingUp, Activity, DollarSign, Zap, Globe, AlertTriangle } from 'lucide-react';

interface ExecutiveDashboardProps {
  insights: any;
}

const ExecutiveDashboard: React.FC<ExecutiveDashboardProps> = ({ insights }) => {
  const metrics = insights.metrics || {};
  
  return (
    <div className="bg-neutral-900/40 border border-white/5 rounded-2xl overflow-hidden backdrop-blur-xl my-6 shadow-2xl">
      <div className="bg-gradient-to-r from-blue-600/10 to-purple-600/10 px-6 py-4 border-b border-white/5 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <Shield className="w-5 h-5 text-blue-400" />
          <span className="text-sm font-bold tracking-tight text-white/90">EXECUTIVE INTELLIGENCE DASHBOARD</span>
        </div>
        <span className="text-[10px] font-black bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded-full border border-blue-500/30 tracking-widest uppercase">
          Proprietary Heuristics v3.0
        </span>
      </div>

      <div className="p-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Architectural Health */}
          <div className="bg-white/5 border border-white/5 rounded-xl p-4 flex flex-col gap-2">
            <div className="flex justify-between items-start">
              <span className="text-[10px] font-bold text-white/40 uppercase tracking-wider">Architectural Health</span>
              <Activity className="w-4 h-4 text-blue-400/50" />
            </div>
            <div className="text-2xl font-black text-white">
              {metrics.architectural_health?.toFixed(1) || '0.0'}%
            </div>
            <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden mt-1">
              <div 
                className="bg-blue-500 h-full transition-all duration-1000" 
                style={{ width: `${metrics.architectural_health || 0}%` }}
              />
            </div>
          </div>

          {/* Adjusted Debt */}
          <div className="bg-white/5 border border-white/5 rounded-xl p-4 flex flex-col gap-2">
            <div className="flex justify-between items-start">
              <span className="text-[10px] font-bold text-white/40 uppercase tracking-wider">Adjusted Debt (V4)</span>
              <DollarSign className="w-4 h-4 text-red-400/50" />
            </div>
            <div className="text-2xl font-black text-red-400">
              ${metrics.technical_debt_cost?.toLocaleString() || '0'}
            </div>
            <span className="text-[10px] text-white/40">Risk Adjusted exposure</span>
          </div>

          {/* Debt Repaid */}
          <div className="bg-white/5 border border-white/5 rounded-xl p-4 flex flex-col gap-2">
            <div className="flex justify-between items-start">
              <span className="text-[10px] font-bold text-white/40 uppercase tracking-wider">Autonomous Value</span>
              <TrendingUp className="w-4 h-4 text-green-400/50" />
            </div>
            <div className="text-2xl font-black text-green-400">
              ${metrics.total_debt_repaid?.toLocaleString() || '0'}
            </div>
            <span className="text-[10px] text-white/40">Debt Repaid Automatically</span>
          </div>

          {/* PDM Multiplier */}
          <div className="bg-white/5 border border-white/5 rounded-xl p-4 flex flex-col gap-2">
            <div className="flex justify-between items-start">
              <span className="text-[10px] font-bold text-white/40 uppercase tracking-wider">PDM Multiplier</span>
              <Zap className="w-4 h-4 text-yellow-500/50" />
            </div>
            <div className="text-2xl font-black text-yellow-500">
              {metrics.pdm_multiplier || '1.00x'}
            </div>
            <span className="text-[10px] text-white/40">Structural friction</span>
          </div>

          {/* ROI */}
          <div className="bg-white/5 border border-white/5 rounded-xl p-4 flex flex-col gap-2">
            <div className="flex justify-between items-start">
              <span className="text-[10px] font-bold text-white/40 uppercase tracking-wider">Efficiency ROI</span>
              <Activity className="w-4 h-4 text-emerald-400/50" />
            </div>
            <div className="text-2xl font-black text-emerald-400">
              {metrics.efficiency_roi || '0.0%'}
            </div>
            <span className="text-[10px] text-white/40">Workflow acceleration</span>
          </div>

          {/* Compliance */}
          <div className="bg-white/5 border border-white/5 rounded-xl p-4 flex flex-col gap-2">
            <div className="flex justify-between items-start">
              <span className="text-[10px] font-bold text-white/40 uppercase tracking-wider">Compliance</span>
              <Globe className="w-4 h-4 text-blue-500/50" />
            </div>
            <div className="text-2xl font-black text-blue-400">
              {metrics.global_compliance_rating || '0%'}
            </div>
            <span className="text-[10px] text-white/40">Policy Governance</span>
          </div>
        </div>

        {/* Hotspots Section */}
        {metrics.fragility_hotspots && metrics.fragility_hotspots.length > 0 && (
          <div className="mt-8">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="w-4 h-4 text-red-400" />
              <span className="text-[10px] font-bold text-white/40 uppercase tracking-widest">Systemic Fragility Hotspots</span>
            </div>
            <div className="space-y-3">
              {metrics.fragility_hotspots.map((h: any, i: number) => (
                <div key={i} className="flex items-center justify-between p-3 bg-white/5 border border-white/5 rounded-lg group hover:border-red-500/30 hover:bg-red-500/5 transition-all">
                  <div className="flex flex-col">
                    <span className="text-xs font-bold text-white/80 group-hover:text-white transition-colors capitalize">{h.node}</span>
                    <span className="text-[10px] text-white/30">Blast Radius: {h.blast_radius}%</span>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className={`text-xs font-black ${h.score > 200 ? 'text-red-400' : 'text-yellow-400'}`}>{h.score}</span>
                    <span className="text-[10px] text-white/30 uppercase font-bold tracking-tighter">Risk Index</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ExecutiveDashboard;
