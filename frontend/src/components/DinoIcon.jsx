// Larger, more detailed, front-facing 3D-style dinosaur SVG illustrations.
// Each dino has animated parts via CSS class hooks.
// No copyrighted assets — original creations.

function Stegosaurus({ accent }) {
  // Sprint Agent: steady, reliable
  return (
    <svg viewBox="0 0 140 140" className="dino dino--stego" role="img" aria-label="stegosaurus">
      <defs>
        <linearGradient id="stegoBody" x1="0" y1="0" x2="0.8" y2="1">
          <stop offset="0%" stopColor={accent} />
          <stop offset="60%" stopColor="#1f8c52" />
          <stop offset="100%" stopColor="#155e38" />
        </linearGradient>
        <radialGradient id="stegoHL" cx="0.35" cy="0.3" r="0.6">
          <stop offset="0%" stopColor="rgba(255,255,255,0.25)" />
          <stop offset="100%" stopColor="transparent" />
        </radialGradient>
      </defs>
      {/* back plates */}
      <g className="dino-body">
        <path d="M42 42 L48 20 L54 42 Z" fill="#e67e22" opacity="0.9" />
        <path d="M56 36 L63 12 L70 36 Z" fill="#f39c12" opacity="0.95" />
        <path d="M72 36 L78 14 L84 36 Z" fill="#f39c12" opacity="0.95" />
        <path d="M86 42 L92 22 L98 42 Z" fill="#e67e22" opacity="0.9" />
      </g>
      {/* tail */}
      <path className="dino-tail" d="M22 80 Q10 76 8 70 Q6 64 14 60 L18 64 Q12 68 16 74 Q22 78 30 78 Z" fill="url(#stegoBody)" />
      <circle cx="10" cy="62" r="3.5" fill="#c0392b" />
      <circle cx="14" cy="57" r="3" fill="#c0392b" />
      {/* legs */}
      <path d="M48 100 L44 122 Q44 126 48 126 L54 126 Q56 126 56 122 L56 100 Z" fill="#155e38" />
      <path d="M80 100 L78 122 Q78 126 82 126 L88 126 Q90 126 90 122 L92 100 Z" fill="#1a6b3f" />
      {/* body - chunky */}
      <path className="dino-body" d="M26 70 Q26 48 50 44 Q70 40 96 44 Q116 50 116 72 Q116 98 92 108 Q66 114 46 108 Q26 100 26 70 Z" fill="url(#stegoBody)" />
      <path d="M26 70 Q26 48 50 44 Q70 40 96 44 Q116 50 116 72 Q116 98 92 108 Q66 114 46 108 Q26 100 26 70 Z" fill="url(#stegoHL)" />
      {/* head */}
      <g className="dino-head">
        <path d="M96 62 Q118 52 128 60 Q132 68 126 76 Q118 82 104 78 Q96 74 96 62 Z" fill="url(#stegoBody)" />
        <path d="M96 62 Q118 52 128 60 Q132 68 126 76 Q118 82 104 78 Q96 74 96 62 Z" fill="url(#stegoHL)" />
        {/* eyes */}
        <ellipse className="dino-eye" cx="116" cy="64" rx="5" ry="5.5" fill="#1a1a1a" />
        <circle cx="114" cy="62" r="2" fill="rgba(255,255,255,0.7)" />
        {/* nostril */}
        <circle cx="126" cy="68" r="2" fill="#0d3b1f" />
        {/* mouth line */}
        <path className="dino-jaw" d="M120 74 Q126 76 130 74" stroke="#0d3b1f" strokeWidth="1.5" fill="none" strokeLinecap="round" />
      </g>
    </svg>
  );
}

function Trex({ accent }) {
  // Risk Agent: alert, powerful
  return (
    <svg viewBox="0 0 140 140" className="dino dino--trex" role="img" aria-label="t-rex">
      <defs>
        <linearGradient id="trexBody2" x1="0" y1="0" x2="0.7" y2="1">
          <stop offset="0%" stopColor={accent} />
          <stop offset="50%" stopColor="#bf6000" />
          <stop offset="100%" stopColor="#7a3e12" />
        </linearGradient>
        <radialGradient id="trexHL" cx="0.3" cy="0.25" r="0.5">
          <stop offset="0%" stopColor="rgba(255,255,255,0.2)" />
          <stop offset="100%" stopColor="transparent" />
        </radialGradient>
      </defs>
      {/* tail */}
      <path className="dino-tail" d="M18 86 Q4 82 4 72 Q4 62 12 58 L16 64 Q8 68 10 76 Q14 82 24 82 Z" fill="url(#trexBody2)" />
      {/* legs */}
      <path d="M48 102 L44 124 Q44 128 48 128 L56 128 Q58 128 58 124 L60 102 Z" fill="#7a3e12" />
      <path d="M78 100 L76 124 Q76 128 80 128 L88 128 Q90 128 90 124 L94 100 Z" fill="#8a4e1a" />
      {/* body */}
      <path className="dino-body" d="M22 80 Q22 50 46 44 Q56 34 70 32 Q88 32 98 44 Q118 56 114 82 Q110 104 82 110 Q54 114 36 106 Q22 98 22 80 Z" fill="url(#trexBody2)" />
      <path d="M22 80 Q22 50 46 44 Q56 34 70 32 Q88 32 98 44 Q118 56 114 82 Q110 104 82 110 Q54 114 36 106 Q22 98 22 80 Z" fill="url(#trexHL)" />
      {/* tiny arms */}
      <path d="M82 76 Q90 80 88 86 L86 84 Q86 80 80 78 Z" fill="#6d3510" />
      <path d="M72 78 Q78 82 76 88 L74 86 Q74 82 70 80 Z" fill="#6d3510" />
      {/* head - big, menacing but not scary */}
      <g className="dino-head">
        <path d="M86 40 Q110 28 126 38 Q134 48 130 60 Q124 72 106 72 Q90 70 86 56 Z" fill="url(#trexBody2)" />
        <path d="M86 40 Q110 28 126 38 Q134 48 130 60 Q124 72 106 72 Q90 70 86 56 Z" fill="url(#trexHL)" />
        {/* brow ridge */}
        <path d="M96 38 Q108 32 120 36" stroke="#5e2f0d" strokeWidth="3" fill="none" strokeLinecap="round" />
        {/* eye - big and alert */}
        <ellipse className="dino-eye" cx="110" cy="46" rx="6" ry="6.5" fill="#1a1000" />
        <circle cx="108" cy="44" r="2.5" fill="rgba(255,255,255,0.7)" />
        <circle cx="112" cy="48" r="1" fill="rgba(255,200,50,0.5)" />
        {/* nostrils */}
        <circle cx="128" cy="50" r="2.5" fill="#4a2000" />
        {/* jaw with teeth */}
        <g className="dino-jaw">
          <path d="M104 66 Q118 72 130 66" stroke="#4a2000" strokeWidth="2" fill="none" />
          <path d="M110 66 L111 70 L112 66" fill="#fff" />
          <path d="M118 66 L119 70 L120 66" fill="#fff" />
          <path d="M124 65 L125 69 L126 65" fill="#fff" />
        </g>
      </g>
    </svg>
  );
}

function Raptor({ accent }) {
  // Dependency Agent: fast, sharp
  return (
    <svg viewBox="0 0 140 140" className="dino dino--raptor" role="img" aria-label="velociraptor">
      <defs>
        <linearGradient id="raptorBody2" x1="0.2" y1="0" x2="0.8" y2="1">
          <stop offset="0%" stopColor={accent} />
          <stop offset="50%" stopColor="#1565c0" />
          <stop offset="100%" stopColor="#0d47a1" />
        </linearGradient>
        <radialGradient id="raptorHL" cx="0.3" cy="0.25" r="0.5">
          <stop offset="0%" stopColor="rgba(255,255,255,0.22)" />
          <stop offset="100%" stopColor="transparent" />
        </radialGradient>
      </defs>
      {/* tail - long sleek */}
      <path className="dino-tail" d="M14 78 Q2 72 4 62 Q8 54 16 56 L18 60 Q10 60 10 68 Q12 74 22 76 Z" fill="url(#raptorBody2)" />
      {/* legs - runner stance */}
      <path d="M56 98 L50 118 Q50 124 54 124 L60 124 L62 118 L64 98 Z" fill="#0d47a1" />
      <path d="M80 96 L78 118 Q78 124 82 124 L88 124 L90 118 L92 96 Z" fill="#1054a5" />
      {/* claws */}
      <path d="M54 124 L50 128 L56 126 Z" fill="#f57c00" />
      <path d="M82 124 L78 128 L84 126 Z" fill="#f57c00" />
      {/* body - sleek */}
      <path className="dino-body" d="M20 74 Q24 50 52 46 Q70 42 90 48 Q112 56 108 78 Q104 98 80 106 Q56 110 38 102 Q20 94 20 74 Z" fill="url(#raptorBody2)" />
      <path d="M20 74 Q24 50 52 46 Q70 42 90 48 Q112 56 108 78 Q104 98 80 106 Q56 110 38 102 Q20 94 20 74 Z" fill="url(#raptorHL)" />
      {/* arms with claws */}
      <path d="M82 70 Q92 72 94 80 L92 78 Q88 74 80 72 Z" fill="#0a3d80" />
      <path d="M94 80 L98 84 L96 80 Z" fill="#f57c00" />
      {/* head - sharp, angular */}
      <g className="dino-head">
        <path d="M92 48 Q114 36 128 44 Q134 52 130 62 Q122 70 108 68 Q94 64 92 52 Z" fill="url(#raptorBody2)" />
        <path d="M92 48 Q114 36 128 44 Q134 52 130 62 Q122 70 108 68 Q94 64 92 52 Z" fill="url(#raptorHL)" />
        {/* eye - sharp, intelligent */}
        <ellipse className="dino-eye" cx="114" cy="50" rx="5.5" ry="5" fill="#0a0a0a" />
        <circle cx="112" cy="48" r="2.2" fill="rgba(255,255,255,0.75)" />
        <ellipse cx="116" cy="52" rx="1" ry="1.5" fill="rgba(100,200,255,0.4)" />
        {/* snout */}
        <circle cx="130" cy="54" r="2" fill="#072f5e" />
        {/* jaw */}
        <g className="dino-jaw">
          <path d="M112 64 Q122 68 132 62" stroke="#072f5e" strokeWidth="1.8" fill="none" />
          <path d="M116 64 L117 67 L118 64" fill="#fff" />
          <path d="M122 64 L123 67 L124 64" fill="#fff" />
        </g>
      </g>
      {/* feather crest */}
      <path d="M94 40 Q98 32 104 36" stroke={accent} strokeWidth="2.5" fill="none" strokeLinecap="round" />
      <path d="M100 38 Q104 30 110 34" stroke={accent} strokeWidth="2" fill="none" strokeLinecap="round" />
    </svg>
  );
}

function Ptero({ accent }) {
  // Forecasting Agent: bird's-eye view
  return (
    <svg viewBox="0 0 140 140" className="dino dino--ptero" role="img" aria-label="pterodactyl">
      <defs>
        <linearGradient id="pteroBody2" x1="0.2" y1="0" x2="0.8" y2="1">
          <stop offset="0%" stopColor={accent} />
          <stop offset="60%" stopColor="#7b1fa2" />
          <stop offset="100%" stopColor="#4a148c" />
        </linearGradient>
        <radialGradient id="pteroHL" cx="0.3" cy="0.3" r="0.5">
          <stop offset="0%" stopColor="rgba(255,255,255,0.2)" />
          <stop offset="100%" stopColor="transparent" />
        </radialGradient>
      </defs>
      {/* wings - large and dramatic */}
      <path className="dino-wing dino-wing--l" d="M66 60 Q38 38 10 48 Q18 54 28 56 Q14 56 8 66 Q22 70 38 66 Q50 64 64 66 Z" fill="url(#pteroBody2)" opacity="0.9" />
      <path className="dino-wing dino-wing--r" d="M74 60 Q102 38 130 48 Q122 54 112 56 Q126 56 132 66 Q118 70 102 66 Q90 64 76 66 Z" fill="url(#pteroBody2)" opacity="0.9" />
      {/* wing membrane texture */}
      <path className="dino-wing dino-wing--l" d="M30 52 Q44 48 60 58" stroke="rgba(255,255,255,0.15)" strokeWidth="1" fill="none" />
      <path className="dino-wing dino-wing--r" d="M110 52 Q96 48 80 58" stroke="rgba(255,255,255,0.15)" strokeWidth="1" fill="none" />
      {/* body */}
      <path className="dino-body" d="M56 58 Q64 50 76 52 Q86 56 84 68 Q80 86 70 96 Q60 86 56 68 Z" fill="url(#pteroBody2)" />
      <path d="M56 58 Q64 50 76 52 Q86 56 84 68 Q80 86 70 96 Q60 86 56 68 Z" fill="url(#pteroHL)" />
      {/* feet */}
      <path d="M64 94 L62 104 L66 102 Z" fill="#4a148c" />
      <path d="M76 94 L78 104 L74 102 Z" fill="#4a148c" />
      {/* head + crest */}
      <g className="dino-head">
        <path d="M62 52 Q66 38 78 40 Q84 44 80 54 Q74 58 66 56 Z" fill="url(#pteroBody2)" />
        {/* crest */}
        <path d="M68 40 Q60 28 54 32" fill={accent} opacity="0.8" />
        <path d="M72 38 Q66 24 58 28" fill={accent} opacity="0.6" />
        {/* eye */}
        <ellipse className="dino-eye" cx="72" cy="47" rx="4.5" ry="4.5" fill="#1a001a" />
        <circle cx="70" cy="45" r="1.8" fill="rgba(255,255,255,0.7)" />
        {/* beak */}
        <g className="dino-jaw">
          <path d="M64 54 L56 58 L64 56 Z" fill="#4a148c" />
          <path d="M64 56 L56 60 L64 58 Z" fill="#38006b" />
        </g>
      </g>
    </svg>
  );
}

function Brachio({ accent }) {
  // Reporting Agent: calm, high-level overview
  return (
    <svg viewBox="0 0 140 140" className="dino dino--brachio" role="img" aria-label="brachiosaurus">
      <defs>
        <linearGradient id="brachioBody2" x1="0.2" y1="0" x2="0.8" y2="1">
          <stop offset="0%" stopColor={accent} />
          <stop offset="50%" stopColor="#558b2f" />
          <stop offset="100%" stopColor="#33691e" />
        </linearGradient>
        <radialGradient id="brachioHL" cx="0.3" cy="0.2" r="0.5">
          <stop offset="0%" stopColor="rgba(255,255,255,0.2)" />
          <stop offset="100%" stopColor="transparent" />
        </radialGradient>
      </defs>
      {/* tail */}
      <path className="dino-tail" d="M18 98 Q6 96 4 88 Q4 80 12 78 L14 82 Q8 84 8 90 Q10 96 20 96 Z" fill="url(#brachioBody2)" />
      {/* legs */}
      <path d="M38 108 L34 128 Q34 132 38 132 L46 132 Q48 132 48 128 L50 108 Z" fill="#33691e" />
      <path d="M68 108 L66 128 Q66 132 70 132 L78 132 Q80 132 80 128 L82 108 Z" fill="#3d7a24" />
      {/* body */}
      <path className="dino-body" d="M18 94 Q22 72 48 68 Q74 64 94 70 Q110 78 106 96 Q100 114 72 118 Q42 118 26 110 Q18 104 18 94 Z" fill="url(#brachioBody2)" />
      <path d="M18 94 Q22 72 48 68 Q74 64 94 70 Q110 78 106 96 Q100 114 72 118 Q42 118 26 110 Q18 104 18 94 Z" fill="url(#brachioHL)" />
      {/* long neck */}
      <g className="dino-neck">
        <path d="M88 72 Q94 44 102 28 Q108 18 114 16 Q122 16 124 24 Q124 34 118 46 Q112 58 100 70 Z" fill="url(#brachioBody2)" />
        <path d="M88 72 Q94 44 102 28 Q108 18 114 16 Q122 16 124 24 Q124 34 118 46 Q112 58 100 70 Z" fill="url(#brachioHL)" />
        {/* head */}
        <path d="M110 16 Q120 10 128 14 Q134 20 130 28 Q124 34 116 32 Q110 28 110 16 Z" fill="url(#brachioBody2)" />
        {/* eye */}
        <ellipse className="dino-eye" cx="122" cy="22" rx="4" ry="4.5" fill="#1a2e0a" />
        <circle cx="120" cy="20" r="1.8" fill="rgba(255,255,255,0.65)" />
        {/* nostril */}
        <circle cx="130" cy="22" r="1.8" fill="#1f3d10" />
        {/* mouth */}
        <path className="dino-jaw" d="M118 30 Q126 32 132 28" stroke="#1f3d10" strokeWidth="1.5" fill="none" strokeLinecap="round" />
      </g>
      {/* spots/texture */}
      <circle cx="50" cy="85" r="4" fill="rgba(255,255,255,0.08)" />
      <circle cx="70" cy="92" r="5" fill="rgba(255,255,255,0.06)" />
      <circle cx="88" cy="86" r="3.5" fill="rgba(255,255,255,0.07)" />
    </svg>
  );
}

const MAP = {
  stego: Stegosaurus,
  trex: Trex,
  raptor: Raptor,
  ptero: Ptero,
  brachio: Brachio,
};

export default function DinoIcon({ species = 'trex', accent = '#34c759', className = '' }) {
  const Comp = MAP[species] || Trex;
  return (
    <span className={`dino-wrap ${className}`}>
      <Comp accent={accent} />
    </span>
  );
}
