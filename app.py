import { useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import { Trophy, Zap, Bot, History, Info, Sparkles, Loader2, TrendingUp, Target, Shield, AlertTriangle } from "lucide-react";
import { predictMatch, type Prediction } from "@/lib/predict.functions";
import oracleBg from "@/assets/oracle-bg.jpg";

type HistoryEntry = { id: string; home: string; away: string; bookmaker: string; prediction: Prediction; at: string };

const BOOKMAKERS = ["1XBET", "Bet365", "Winamax", "Betclic", "Unibet"];

export function LogicScoreApp() {
  const predict = useServerFn(predictMatch);
  const [tab, setTab] = useState<"predict" | "history" | "info">("predict");
  const [match, setMatch] = useState("");
  const [home, setHome] = useState("");
  const [away, setAway] = useState("");
  const [competition, setCompetition] = useState("");
  const [bookmaker, setBookmaker] = useState("1XBET");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Prediction | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const matchQuery = match.trim();
      const homeTeam = home.trim();
      const awayTeam = away.trim();
      const res = await predict({ data: { matchQuery, homeTeam, awayTeam, bookmaker, competition: competition.trim() } });
      if (!res.ok) setError(res.error);
      else {
        setResult(res.prediction);
        const [resolvedHome = homeTeam || matchQuery, resolvedAway = awayTeam] = res.prediction.matchup.split(/\s+(?:vs|v|contre|-)\s+/i).map((team) => team.trim());
        setHistory((h) => [{ id: crypto.randomUUID(), home: resolvedHome, away: resolvedAway, bookmaker, prediction: res.prediction, at: new Date().toLocaleString("fr-FR") }, ...h].slice(0, 20));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inattendue");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden">
      <img src={oracleBg} alt="" aria-hidden className="pointer-events-none absolute inset-0 h-full w-full object-cover opacity-30 mix-blend-luminosity" />
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-background/60 via-background/80 to-background" />

      <div className="relative mx-auto max-w-2xl px-5 py-10">
        <header className="flex flex-col items-center text-center">
          <div className="flex items-center gap-3">
            <div className="flex h-20 w-20 items-center justify-center rounded-2xl shadow-[var(--shadow-glow)]" style={{ background: "var(--gradient-logo)" }}>
              <Trophy className="h-10 w-10 text-primary-foreground" strokeWidth={2.5} />
            </div>
            <div className="text-left">
              <h1 className="text-4xl font-bold tracking-tight">
                <span className="text-foreground">Logic</span>
                <span style={{ background: "var(--gradient-logo)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>Score</span>
              </h1>
              <p className="mt-1 flex items-center gap-1 text-sm font-semibold text-warning"><Zap className="h-4 w-4 fill-warning" /> AI</p>
            </div>
          </div>
          <p className="mt-6 max-w-md text-balance text-lg text-muted-foreground">Prédictions de football basées sur l'intelligence artificielle et la modélisation statistique avancée</p>

          <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
            <Pill dot="bg-primary">Données en temps réel</Pill>
            <Pill dot="bg-warning">Modèle de Poisson</Pill>
            <Pill dot="bg-primary">Analyse H2H</Pill>
          </div>
          <div className="mt-3">
            <Pill dot="bg-primary" highlight>Bookmaker: {bookmaker}</Pill>
          </div>
        </header>

        <nav className="mt-8 flex items-center justify-center gap-1 rounded-2xl border border-border bg-card/60 p-1.5 backdrop-blur-xl">
          <TabBtn active={tab === "predict"} onClick={() => setTab("predict")} icon={<Bot className="h-5 w-5" />} />
          <TabBtn active={tab === "history"} onClick={() => setTab("history")} icon={<History className="h-5 w-5" />} />
          <TabBtn active={tab === "info"} onClick={() => setTab("info")} icon={<Info className="h-5 w-5" />} />
        </nav>

        <main className="mt-8">
          {tab === "predict" && (
            <section className="rounded-3xl border border-border bg-card/70 p-6 shadow-[var(--shadow-card)] backdrop-blur-xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/15 text-primary"><Sparkles className="h-5 w-5" /></div>
                  <h2 className="text-2xl font-bold">Configurer l'analyse</h2>
                </div>
                <span className="rounded-md bg-primary/15 px-2.5 py-1 text-xs font-semibold text-primary">{bookmaker}</span>
              </div>

              <form onSubmit={onSubmit} className="mt-6 space-y-5">
                <Field label="Match">
                  <input value={match} onChange={(e) => setMatch(e.target.value)} placeholder="Ex: PSG OM, Real Madrid Barcelona" className="w-full rounded-xl border border-border bg-input/60 px-4 py-3 text-foreground placeholder:text-muted-foreground/60 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30" />
                </Field>
                <div className="grid grid-cols-2 gap-3">
                  <Field label="Domicile (optionnel)">
                    <input value={home} onChange={(e) => setHome(e.target.value)} placeholder="PSG" className="w-full rounded-xl border border-border bg-input/60 px-4 py-3 text-foreground placeholder:text-muted-foreground/60 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30" />
                  </Field>
                  <Field label="Extérieur (optionnel)">
                    <input value={away} onChange={(e) => setAway(e.target.value)} placeholder="OM" className="w-full rounded-xl border border-border bg-input/60 px-4 py-3 text-foreground placeholder:text-muted-foreground/60 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30" />
                  </Field>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <Field label="Compétition (optionnel)">
                    <input value={competition} onChange={(e) => setCompetition(e.target.value)} placeholder="Ligue 1" className="w-full rounded-xl border border-border bg-input/60 px-4 py-3 text-foreground placeholder:text-muted-foreground/60 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30" />
                  </Field>
                  <Field label="Bookmaker">
                    <select value={bookmaker} onChange={(e) => setBookmaker(e.target.value)} className="w-full rounded-xl border border-border bg-input/60 px-4 py-3 text-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30">
                      {BOOKMAKERS.map((b) => <option key={b} value={b}>{b}</option>)}
                    </select>
                  </Field>
                </div>

                <button disabled={loading} type="submit" className="group relative flex w-full items-center justify-center gap-2 overflow-hidden rounded-xl py-3.5 text-base font-bold text-primary-foreground transition-all hover:shadow-[var(--shadow-glow)] disabled:opacity-60" style={{ background: "var(--gradient-logo)" }}>
                  {loading ? <><Loader2 className="h-5 w-5 animate-spin" /> Analyse en cours…</> : <><Sparkles className="h-5 w-5" /> Lancer l'analyse AI</>}
                </button>

                {error && (
                  <div className="flex items-start gap-2 rounded-xl border border-destructive/40 bg-destructive/10 p-3 text-sm text-destructive-foreground">
                    <AlertTriangle className="mt-0.5 h-4 w-4 flex-shrink-0 text-destructive" />
                    <p>{error}</p>
                  </div>
                )}
              </form>

              {result && <ResultView prediction={result} />}
            </section>
          )}

          {tab === "history" && (
            <section className="rounded-3xl border border-border bg-card/70 p-6 backdrop-blur-xl">
              <h2 className="text-xl font-bold">Historique des analyses</h2>
              {history.length === 0 ? (
                <p className="mt-4 text-sm text-muted-foreground">Aucune analyse encore. Lance ta première prédiction.</p>
              ) : (
                <ul className="mt-4 space-y-3">
                  {history.map((h) => (
                    <li key={h.id} className="rounded-xl border border-border bg-secondary/40 p-4">
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-semibold">{h.home} vs {h.away}</span>
                        <span className="text-xs text-muted-foreground">{h.at}</span>
                      </div>
                      <div className="mt-2 flex items-center gap-3 text-sm">
                        <span className="rounded-md bg-primary/15 px-2 py-0.5 text-xs font-semibold text-primary">{h.bookmaker}</span>
                        <span className="text-muted-foreground">Score prédit:</span>
                        <span className="font-bold text-foreground">{h.prediction.predictedScore.home} - {h.prediction.predictedScore.away}</span>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          )}

          {tab === "info" && (
            <section className="space-y-4 rounded-3xl border border-border bg-card/70 p-6 backdrop-blur-xl">
              <h2 className="text-xl font-bold">À propos de LogicScore AI</h2>
              <p className="text-sm leading-relaxed text-muted-foreground">LogicScore combine la distribution de Poisson, l'analyse Head-to-Head et les forces statistiques pour générer des prédictions football calibrées par une IA experte.</p>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>• Modèle Poisson sur xG attaque/défense</li>
                <li>• Analyse de la forme récente des deux équipes</li>
                <li>• Probabilités 1X2 + marchés alternatifs</li>
                <li>• Niveau de risque par recommandation</li>
              </ul>
              <p className="text-xs text-muted-foreground">⚠️ Les prédictions sont indicatives. Pariez de manière responsable.</p>
            </section>
          )}
        </main>

        <footer className="mt-10 text-center text-xs text-muted-foreground">Propulsé par Lovable AI • LogicScore © 2026</footer>
      </div>
    </div>
  );
}

function Pill({ children, dot, highlight }: { children: React.ReactNode; dot?: string; highlight?: boolean }) {
  return (
    <span className={`inline-flex items-center gap-2 rounded-full border px-3.5 py-1.5 text-sm backdrop-blur-md ${highlight ? "border-primary/50 bg-primary/10 text-primary" : "border-border bg-card/50 text-foreground/90"}`}>
      {dot && <span className={`h-1.5 w-1.5 rounded-full ${dot}`} />} {children}
    </span>
  );
}

function TabBtn({ active, onClick, icon }: { active: boolean; onClick: () => void; icon: React.ReactNode }) {
  return (
    <button onClick={onClick} className={`flex flex-1 items-center justify-center rounded-xl py-3 transition-all ${active ? "bg-primary text-primary-foreground shadow-[var(--shadow-glow)]" : "text-muted-foreground hover:text-foreground"}`}>
      {icon}
    </button>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-semibold text-foreground">{label}</span>
      {children}
    </label>
  );
}

function ResultView({ prediction }: { prediction: Prediction }) {
  const p = prediction;
  return (
    <div className="mt-6 space-y-4">
      <div className="rounded-2xl border border-primary/40 bg-gradient-to-br from-primary/15 to-accent/10 p-5">
        <p className="text-xs uppercase tracking-wider text-muted-foreground">Score prédit</p>
        <p className="mt-1 text-4xl font-bold tracking-tight">{p.predictedScore.home} <span className="text-muted-foreground">-</span> {p.predictedScore.away}</p>
        <p className="mt-2 text-sm text-muted-foreground">{p.matchup}</p>
      </div>

      <div className="grid grid-cols-3 gap-2">
        <ProbBox label="Domicile" value={p.poisson.homeWinProb} accent="primary" />
        <ProbBox label="Nul" value={p.poisson.drawProb} accent="muted" />
        <ProbBox label="Extérieur" value={p.poisson.awayWinProb} accent="accent" />
      </div>

      <div className="grid grid-cols-2 gap-2 text-sm">
        <Stat icon={<TrendingUp className="h-4 w-4" />} label="xG Domicile" value={p.poisson.homeExpectedGoals.toFixed(2)} />
        <Stat icon={<TrendingUp className="h-4 w-4" />} label="xG Extérieur" value={p.poisson.awayExpectedGoals.toFixed(2)} />
      </div>

      <div className="rounded-2xl border border-border bg-secondary/40 p-4">
        <h3 className="flex items-center gap-2 text-sm font-bold"><Target className="h-4 w-4 text-primary" /> Meilleurs picks</h3>
        <ul className="mt-3 space-y-2">
          {p.topPicks.map((pick, i) => (
            <li key={i} className="rounded-xl border border-border bg-card/60 p-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase text-muted-foreground">{pick.market}</p>
                  <p className="text-base font-bold">{pick.pick}</p>
                </div>
                <span className="rounded-md bg-primary/15 px-2.5 py-1 text-sm font-bold text-primary">{Math.round(pick.confidence)}%</span>
              </div>
              <p className="mt-2 text-xs text-muted-foreground">{pick.reasoning}</p>
            </li>
          ))}
        </ul>
      </div>

      <div className="grid grid-cols-1 gap-2">
        <InfoBlock title="Analyse H2H" body={p.h2hAnalysis} />
        <InfoBlock title={`Forme — ${p.matchup.split(/vs|—|-/)[0]?.trim() || "Domicile"}`} body={p.formAnalysis.home} />
        <InfoBlock title={`Forme — ${p.matchup.split(/vs|—|-/)[1]?.trim() || "Extérieur"}`} body={p.formAnalysis.away} />
      </div>

      <div className="flex items-center justify-between rounded-2xl border border-border bg-secondary/40 p-4">
        <div className="flex items-center gap-2 text-sm"><Shield className="h-4 w-4 text-primary" /> Niveau de risque</div>
        <span className={`rounded-md px-2.5 py-1 text-xs font-bold ${p.riskLevel === "Faible" ? "bg-success/20 text-success" : p.riskLevel === "Modéré" ? "bg-warning/20 text-warning" : "bg-destructive/20 text-destructive"}`}>{p.riskLevel}</span>
      </div>

      <p className="rounded-2xl border border-border bg-card/40 p-4 text-sm text-muted-foreground">{p.summary}</p>
    </div>
  );
}

function ProbBox({ label, value, accent }: { label: string; value: number; accent: "primary" | "accent" | "muted" }) {
  const color = accent === "primary" ? "text-primary" : accent === "accent" ? "text-accent" : "text-muted-foreground";
  return (
    <div className="rounded-xl border border-border bg-secondary/40 p-3 text-center">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className={`mt-1 text-2xl font-bold ${color}`}>{Math.round(value)}%</p>
    </div>
  );
}

function Stat({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-border bg-secondary/40 px-3 py-2.5">
      <span className="flex items-center gap-2 text-muted-foreground">{icon}{label}</span>
      <span className="font-bold">{value}</span>
    </div>
  );
}

function InfoBlock({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-2xl border border-border bg-card/40 p-4">
      <p className="text-xs font-bold uppercase tracking-wider text-primary">{title}</p>
      <p className="mt-2 text-sm leading-relaxed text-foreground/90">{body}</p>
    </div>
  );
}
