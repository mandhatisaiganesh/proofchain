// ─── ProofChain App ──────────────────────────────────────────────────
import { useState } from 'react';
import {
  LayoutDashboard, FileText, GitBranch, AlertTriangle,
  Shield, Zap, Network, Play, ChevronRight,
} from 'lucide-react';
import './index.css';

import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import Commitments from './pages/Commitments';
import Conflicts from './pages/Conflicts';
import Risks from './pages/Risks';
import Actions from './pages/Actions';
import Graph from './pages/Graph';
import Analysis from './pages/Analysis';

// ─── Types ───────────────────────────────────────────────────────────
type PageId =
  | 'dashboard'
  | 'documents'
  | 'commitments'
  | 'conflicts'
  | 'risks'
  | 'actions'
  | 'graph'
  | 'analysis';

interface NavEntry {
  id: PageId;
  label: string;
  icon: React.ComponentType<{ size?: number }>;
  section?: string;
  badge?: string;
  badgeClass?: string;
}

const NAV: NavEntry[] = [
  { id: 'dashboard',   label: 'Dashboard',    icon: LayoutDashboard, section: 'Overview' },
  { id: 'analysis',    label: 'Run Analysis', icon: Play,            section: 'Intelligence' },
  { id: 'commitments', label: 'Commitments',  icon: GitBranch },
  { id: 'graph',       label: 'Graph',        icon: Network },
  { id: 'conflicts',   label: 'Conflicts',    icon: AlertTriangle,   section: 'Issues' },
  { id: 'risks',       label: 'Risk Center',  icon: Shield },
  { id: 'actions',     label: 'Actions',      icon: Zap },
  { id: 'documents',   label: 'Documents',    icon: FileText,        section: 'Data' },
];

const PAGE_TITLES: Record<PageId, string> = {
  dashboard:   'Dashboard',
  analysis:    'Run Analysis',
  commitments: 'Commitments',
  graph:       'Commitment Graph',
  conflicts:   'Conflicts',
  risks:       'Risk Center',
  actions:     'Actions & Approvals',
  documents:   'Documents',
};

const WORKSPACE_ID = 'demo-workspace';

// ─── Sidebar ─────────────────────────────────────────────────────────
function Sidebar({ active, onNav }: { active: PageId; onNav: (p: PageId) => void }) {
  const sections: string[] = [];
  const grouped: Record<string, NavEntry[]> = {};

  NAV.forEach(entry => {
    const section = entry.section || '__none__';
    if (!grouped[section]) {
      grouped[section] = [];
      sections.push(section);
    }
    grouped[section].push(entry);
  });

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">🔗</div>
        <div className="sidebar-logo-text">
          <span className="sidebar-logo-name">ProofChain</span>
          <span className="sidebar-logo-tag">Commitment Intelligence</span>
        </div>
      </div>

      {/* Nav */}
      <nav className="sidebar-nav">
        {sections.map(section => (
          <div key={section}>
            {section !== '__none__' && (
              <div className="nav-section-label">{section}</div>
            )}
            {grouped[section].map(entry => {
              const Icon = entry.icon;
              const isActive = active === entry.id;
              return (
                <div
                  key={entry.id}
                  className={`nav-item ${isActive ? 'active' : ''}`}
                  onClick={() => onNav(entry.id)}
                >
                  <span className="nav-item-icon"><Icon size={15} /></span>
                  <span>{entry.label}</span>
                  {entry.badge && (
                    <span className={`nav-badge ${entry.badgeClass ?? ''}`}>{entry.badge}</span>
                  )}
                  {isActive && <ChevronRight size={12} style={{ marginLeft: 'auto', opacity: 0.5 }} />}
                </div>
              );
            })}
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        <div className="workspace-pill">
          <span className="workspace-dot" />
          <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {WORKSPACE_ID}
          </span>
        </div>
      </div>
    </aside>
  );
}

// ─── Top Bar ─────────────────────────────────────────────────────────
function TopBar({ page }: { page: PageId }) {
  return (
    <header className="topbar">
      <span className="topbar-title">
        {PAGE_TITLES[page]}
        <span className="topbar-sub">— AWS Agents for Humans</span>
      </span>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span className="badge badge-green" style={{ fontSize: 11 }}>● API Connected</span>
        <div style={{
          width: 28, height: 28, borderRadius: '50%',
          background: 'linear-gradient(135deg, var(--indigo), var(--purple))',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 11, fontWeight: 700, color: 'white',
        }}>P</div>
      </div>
    </header>
  );
}

// ─── Page Renderer ────────────────────────────────────────────────────
function PageContent({ page }: { page: PageId }) {
  switch (page) {
    case 'dashboard':   return <Dashboard   workspaceId={WORKSPACE_ID} />;
    case 'documents':   return <Documents   workspaceId={WORKSPACE_ID} />;
    case 'commitments': return <Commitments workspaceId={WORKSPACE_ID} />;
    case 'conflicts':   return <Conflicts   workspaceId={WORKSPACE_ID} />;
    case 'risks':       return <Risks       workspaceId={WORKSPACE_ID} />;
    case 'actions':     return <Actions     workspaceId={WORKSPACE_ID} />;
    case 'graph':       return <Graph       workspaceId={WORKSPACE_ID} />;
    case 'analysis':    return <Analysis    workspaceId={WORKSPACE_ID} />;
    default:            return null;
  }
}

// ─── App Root ─────────────────────────────────────────────────────────
export default function App() {
  const [page, setPage] = useState<PageId>('dashboard');

  return (
    <>
      <Sidebar active={page} onNav={setPage} />
      <div className="main-content">
        <TopBar page={page} />
        <main className="page-content">
          <PageContent page={page} />
        </main>
      </div>
    </>
  );
}
