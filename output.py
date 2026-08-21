import json
from config import MARKTPLAATS_BASE, OUTPUT_JSON, OUTPUT_HTML
from rich.console import Console
from rich.table import Table

console = Console()


def print_table(listings: list[dict], top_n: int = 50) -> None:
    table = Table(title="Marktplaats Vintage Treasure Finder", show_lines=False)
    table.add_column("RANK", style="bold cyan", width=5)
    table.add_column("SCORE", style="bold green", width=6)
    table.add_column("PRICE", width=10)
    table.add_column("DIST", width=7)
    table.add_column("TITLE", width=40)
    table.add_column("URL")

    for i, listing in enumerate(listings[:top_n], 1):
        table.add_row(
            str(i),
            str(listing["_score"]),
            _format_price(listing),
            _format_distance(listing),
            listing.get("title", "")[:40],
            MARKTPLAATS_BASE + listing.get("vipUrl", ""),
        )
    console.print(table)


def save_json(listings: list[dict]) -> None:
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(listings, f, ensure_ascii=False, indent=2)
    console.print(f"[dim]Saved {len(listings)} results to {OUTPUT_JSON}[/dim]")


def save_html(listings: list[dict], top_n: int = 50) -> None:
    data = []
    for i, listing in enumerate(listings[:top_n], 1):
        pics = listing.get("pictures", [])
        data.append({
            "rank": i,
            "score": listing["_score"],
            "title": listing.get("title", ""),
            "description": listing.get("description", "")[:200],
            "price": _format_price(listing),
            "priceCents": listing.get("priceInfo", {}).get("priceCents", 0),
            "priceType": _normalize_price_type(listing.get("priceInfo", {})),
            "distance": _format_distance(listing),
            "distanceMeters": listing.get("location", {}).get("distanceMeters", 99999),
            "city": listing.get("location", {}).get("cityName", ""),
            "url": MARKTPLAATS_BASE + listing.get("vipUrl", ""),
            "thumb": pics[0].get("mediumUrl", "") if pics else "",
            "date": listing.get("date", ""),
            "seller": listing.get("sellerInformation", {}).get("sellerName", ""),
            "query": listing.get("_query", ""),
            "ai_reason": listing.get("_ai_reason", ""),
            "market_value": listing.get("_market_value", ""),
            "breakdown": listing.get("_breakdown", {}),
        })

    data_json = json.dumps(data, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <title>Marktplaats Treasure Finder</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['-apple-system', 'BlinkMacSystemFont', '"SF Pro Text"', '"Segoe UI"', 'sans-serif'],
          }}
        }}
      }}
    }}
  </script>
  <style>
    input[type=range] {{ accent-color: black; }}
    .line-clamp-2 {{ display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
    .line-clamp-3 {{ display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }}
  </style>
</head>
<body class="min-h-screen bg-neutral-100 text-black font-sans antialiased">

  <!-- Header -->
  <header class="bg-white/80 backdrop-blur sticky top-0 z-10 border-b border-neutral-200 px-6 py-4 flex items-center gap-3">
    <h1 class="text-sm font-semibold tracking-tight mr-2">Treasure Finder</h1>
    <div class="flex items-center gap-1">
      <button id="tab-all" onclick="setTab('all')"
        class="text-xs px-3 py-1.5 rounded-lg font-medium transition-colors bg-black text-white">
        All
      </button>
      <button id="tab-saved" onclick="setTab('saved')"
        class="text-xs px-3 py-1.5 rounded-lg font-medium transition-colors text-neutral-400 hover:text-black">
        Saved <span id="saved-count" class="ml-0.5"></span>
      </button>
    </div>
    <span id="count" class="text-xs text-neutral-400 tabular-nums ml-auto"></span>
    <button onclick="toggleSettings()"
      class="text-xs px-3 py-1.5 rounded-lg font-medium border border-neutral-200 hover:border-black transition-colors flex items-center gap-1.5">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-3.5 h-3.5">
        <path fill-rule="evenodd" d="M8.34 1.804A1 1 0 019.32 1h1.36a1 1 0 01.98.804l.295 1.473c.497.144.971.342 1.416.587l1.25-.834a1 1 0 011.262.125l.962.962a1 1 0 01.125 1.262l-.834 1.25c.245.445.443.919.587 1.416l1.473.294a1 1 0 01.804.98v1.361a1 1 0 01-.804.98l-1.473.295a6.95 6.95 0 01-.587 1.416l.834 1.25a1 1 0 01-.125 1.262l-.962.962a1 1 0 01-1.262.125l-1.25-.834a6.953 6.953 0 01-1.416.587l-.294 1.473a1 1 0 01-.98.804H9.32a1 1 0 01-.98-.804l-.295-1.473a6.957 6.957 0 01-1.416-.587l-1.25.834a1 1 0 01-1.262-.125l-.962-.962a1 1 0 01-.125-1.262l.834-1.25a6.957 6.957 0 01-.587-1.416l-1.473-.294A1 1 0 011 10.68V9.32a1 1 0 01.804-.98l1.473-.295c.144-.497.342-.971.587-1.416l-.834-1.25a1 1 0 01.125-1.262l.962-.962A1 1 0 015.38 3.03l1.25.834a6.957 6.957 0 011.416-.587L8.34 1.804zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd"/>
      </svg>
      Filters
    </button>
  </header>

  <!-- Controls bar -->
  <div id="controls" class="bg-white border-b border-neutral-200 px-6 py-3 flex flex-wrap gap-3 items-center">
    <input
      id="search"
      type="text"
      placeholder="Search listings..."
      class="flex-1 min-w-48 text-sm bg-neutral-100 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black/10 placeholder:text-neutral-400"
    >
    <select id="sort" class="text-sm bg-neutral-100 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black/10">
      <option value="score">Best match</option>
      <option value="price_asc">Price: low to high</option>
      <option value="price_desc">Price: high to low</option>
      <option value="distance">Nearest first</option>
    </select>
    <label class="text-xs text-neutral-500 flex items-center gap-2">
      Max €<span id="priceVal" class="text-black font-medium w-6 inline-block">500</span>
      <input type="range" id="maxPrice" min="0" max="500" step="5" value="500" class="w-24">
    </label>
    <label class="text-xs text-neutral-500 flex items-center gap-2">
      <span id="distVal" class="text-black font-medium w-4 inline-block">10</span>km
      <input type="range" id="maxDist" min="1" max="10" step="1" value="10" class="w-20">
    </label>
  </div>

  <!-- Settings panel (slide-in from right) -->
  <div id="settings-backdrop" onclick="toggleSettings()"
    class="fixed inset-0 bg-black/20 backdrop-blur-sm z-20 hidden"></div>
  <aside id="settings-panel"
    class="fixed top-0 right-0 h-full w-80 bg-white z-30 shadow-2xl overflow-y-auto translate-x-full transition-transform duration-300 ease-in-out">
    <div class="flex items-center justify-between px-5 py-4 border-b border-neutral-100">
      <h2 class="text-sm font-semibold">Filters</h2>
      <button onclick="toggleSettings()" class="text-neutral-400 hover:text-black transition-colors text-lg leading-none">×</button>
    </div>

    <!-- Min score -->
    <div class="px-5 py-4 border-b border-neutral-100">
      <div class="flex items-center justify-between mb-3">
        <p class="text-xs font-semibold uppercase tracking-wider text-neutral-500">Min. score</p>
        <span id="minScoreVal" class="text-sm font-bold">0</span>
      </div>
      <input type="range" id="minScore" min="0" max="90" step="5" value="0"
        class="w-full" oninput="document.getElementById('minScoreVal').textContent=this.value; filter()">
    </div>

    <!-- Price type -->
    <div class="px-5 py-4 border-b border-neutral-100">
      <p class="text-xs font-semibold uppercase tracking-wider text-neutral-500 mb-3">Price type</p>
      <div class="flex flex-col gap-2" id="priceTypeFilters">
        <label class="flex items-center gap-2 text-sm cursor-pointer">
          <input type="checkbox" value="FREE" checked onchange="filter()" class="rounded"> Gratis
        </label>
        <label class="flex items-center gap-2 text-sm cursor-pointer">
          <input type="checkbox" value="FIXED" checked onchange="filter()" class="rounded"> Fixed price
        </label>
        <label class="flex items-center gap-2 text-sm cursor-pointer">
          <input type="checkbox" value="MIN_BID" checked onchange="filter()" class="rounded"> Min. bid
        </label>
        <label class="flex items-center gap-2 text-sm cursor-pointer">
          <input type="checkbox" value="FAST_BID" checked onchange="filter()" class="rounded"> Auction
        </label>
      </div>
    </div>

    <!-- Query categories -->
    <div class="px-5 py-4 border-b border-neutral-100">
      <div class="flex items-center justify-between mb-3">
        <p class="text-xs font-semibold uppercase tracking-wider text-neutral-500">Search terms</p>
        <button onclick="toggleAllQueries(true)" class="text-xs text-neutral-400 hover:text-black">All</button>
      </div>
      <div class="space-y-3" id="queryGroups"></div>

      <!-- Custom query input -->
      <div class="mt-3 pt-3 border-t border-neutral-100">
        <p class="text-xs text-neutral-400 mb-2">Add a search term</p>
        <div class="flex gap-2">
          <input id="custom-query-input" type="text" placeholder="e.g. rookglas"
            class="flex-1 text-xs bg-neutral-100 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-black/10 placeholder:text-neutral-300"
            onkeydown="if(event.key==='Enter') addCustomQuery()">
          <button onclick="addCustomQuery()"
            class="text-xs font-semibold bg-black text-white rounded-lg px-3 py-2 hover:bg-neutral-700 transition-colors whitespace-nowrap">
            Add
          </button>
        </div>
        <div id="custom-query-status" class="text-xs mt-1.5 hidden"></div>
      </div>
    </div>

    <!-- Run button (only shown when server is available) -->
    <div id="run-section" class="px-5 py-4 border-b border-neutral-100 hidden">
      <p class="text-xs font-semibold uppercase tracking-wider text-neutral-500 mb-3">Fetch new results</p>
      <p class="text-xs text-neutral-400 mb-3">Re-run the fetcher using only the selected search terms above.</p>
      <button id="run-btn" onclick="runFetch()"
        class="w-full text-sm font-semibold bg-black text-white rounded-lg py-2.5 hover:bg-neutral-800 transition-colors flex items-center justify-center gap-2">
        <span id="run-label">Run selected queries</span>
      </button>
      <p id="run-status" class="text-xs text-neutral-400 text-center mt-2 hidden"></p>
    </div>

    <div class="px-5 py-4">
      <button onclick="resetSettings()"
        class="w-full text-xs text-neutral-400 hover:text-black border border-neutral-200 hover:border-black rounded-lg py-2 transition-colors">
        Reset all filters
      </button>
    </div>
  </aside>

  <!-- Grid -->
  <div id="grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 p-6"></div>

  <script>
    const ALL = {data_json};
    const grid = document.getElementById('grid');
    const countEl = document.getElementById('count');
    const savedCountEl = document.getElementById('saved-count');

    let liked = new Set(JSON.parse(localStorage.getItem('tf_liked') || '[]'));
    let currentTab = 'all';

    // Query groups for settings panel
    const QUERY_GROUPS = [
      {{ label: 'Urgency', queries: ['mag weg', 'zolder opruiming', 'gratis ophalen', 'gratis'] }},
      {{ label: 'Condition', queries: ['opknapper', 'defect', 'kapot', 'niet werkend'] }},
      {{ label: 'Style', queries: ['vintage', 'retro', 'industrieel', 'Deens design'] }},
      {{ label: 'Material', queries: ['teak', 'antiek'] }},
      {{ label: 'Era', queries: ['jaren 60', 'jaren 70'] }},
      {{ label: 'Art', queries: ['schilderij', 'kunstwerk', 'aquarel', 'sculptuur', 'beeld', 'beeldje', 'bronzen beeld', 'wanddecoratie', 'wandobject', 'wandsculptuur'] }},
      {{ label: 'Decoratie', queries: ['vaas', 'keramiek', 'aardewerk', 'steengoed', 'kandelaar', 'kaarsenhouder', 'kandelaars', 'dienblad', 'tray', 'serveerschaal', 'onderzetter', 'kurk onderzetter', 'decoratie', 'brocante', 'curiosa', 'olieverfschilij'] }},
    ];

    // #5 — restore persisted query prefs, fall back to all queries in current results
    const _allKnownQueries = new Set(ALL.map(d => d.query));
    const _saved = localStorage.getItem('tf_active_queries');
    let activeQueries = _saved
      ? new Set(JSON.parse(_saved).filter(q => _allKnownQueries.has(q) || true))
      : new Set(_allKnownQueries);

    function saveQueryPrefs() {{
      localStorage.setItem('tf_active_queries', JSON.stringify([...activeQueries]));
    }}

    // #2 — compute per-query stats from current results
    function queryStats() {{
      const stats = {{}};
      for (const d of ALL) {{
        if (!stats[d.query]) stats[d.query] = {{ count: 0, total: 0 }};
        stats[d.query].count++;
        stats[d.query].total += d.score;
      }}
      return stats;
    }}

    function buildQueryGroups() {{
      const stats = queryStats();
      const container = document.getElementById('queryGroups');
      container.innerHTML = QUERY_GROUPS.map(group => `
        <div>
          <p class="text-xs text-neutral-400 mb-1.5">${{group.label}}</p>
          <div class="flex flex-wrap gap-1.5">
            ${{group.queries.map(q => {{
              const s = stats[q];
              const badge = s
                ? `<span class="ml-1 opacity-60 font-normal">${{s.count}} · ${{Math.round(s.total/s.count)}}</span>`
                : '';
              const active = activeQueries.has(q);
              return `<button onclick="toggleQuery('${{q}}')" id="qtag-${{q.replace(/ /g,'_')}}"
                class="text-xs px-2.5 py-1 rounded-full border transition-colors ${{
                  active ? 'border-neutral-200 bg-black text-white' : 'border-neutral-200 bg-white text-neutral-400'
                }}">${{q}}${{badge}}</button>`;
            }}).join('')}}
          </div>
        </div>`).join('');
    }}

    function toggleQuery(q) {{
      activeQueries.has(q) ? activeQueries.delete(q) : activeQueries.add(q);
      saveQueryPrefs();
      const stats = queryStats();
      const s = stats[q];
      const badge = s ? `<span class="ml-1 opacity-60 font-normal">${{s.count}} · ${{Math.round(s.total/s.count)}}</span>` : '';
      const btn = document.getElementById('qtag-' + q.replace(/ /g,'_'));
      if (btn) {{
        btn.className = `text-xs px-2.5 py-1 rounded-full border transition-colors ${{
          activeQueries.has(q)
            ? 'border-neutral-200 bg-black text-white'
            : 'border-neutral-200 bg-white text-neutral-400'
        }}`;
        btn.innerHTML = q + badge;
      }}
      filter();
    }}

    function toggleAllQueries(on) {{
      activeQueries = on ? new Set(ALL.map(d => d.query)) : new Set();
      saveQueryPrefs();
      buildQueryGroups();
      filter();
    }}

    // Custom queries added this session (not in QUERY_GROUPS)
    const customQueries = JSON.parse(localStorage.getItem('tf_custom_queries') || '[]');

    function renderCustomGroup() {{
      const existing = document.getElementById('custom-group');
      if (existing) existing.remove();
      if (customQueries.length === 0) return;
      const stats = queryStats();
      const container = document.getElementById('queryGroups');
      const div = document.createElement('div');
      div.id = 'custom-group';
      div.innerHTML = `
        <p class="text-xs text-neutral-400 mb-1.5">Custom</p>
        <div class="flex flex-wrap gap-1.5">
          ${{customQueries.map(q => {{
            const s = stats[q];
            const badge = s ? `<span class="ml-1 opacity-60 font-normal">${{s.count}} · ${{Math.round(s.total/s.count)}}</span>` : '';
            const active = activeQueries.has(q);
            return `<button onclick="toggleQuery('${{q}}')" id="qtag-${{q.replace(/ /g,'_')}}"
              class="text-xs px-2.5 py-1 rounded-full border transition-colors ${{active ? 'border-neutral-200 bg-black text-white' : 'border-neutral-200 bg-white text-neutral-400'}}">${{q}}${{badge}}</button>`;
          }}).join('')}}
        </div>`;
      container.prepend(div);
    }}

    function addCustomQuery() {{
      const input = document.getElementById('custom-query-input');
      const statusEl = document.getElementById('custom-query-status');
      const q = input.value.trim().toLowerCase();
      if (!q) return;

      // Add to session
      if (!customQueries.includes(q)) {{
        customQueries.push(q);
        localStorage.setItem('tf_custom_queries', JSON.stringify(customQueries));
      }}
      activeQueries.add(q);
      saveQueryPrefs();
      renderCustomGroup();
      input.value = '';

      // Try to persist to config.py via server
      if (serverAvailable) {{
        statusEl.textContent = 'Saving…';
        statusEl.className = 'text-xs mt-1.5 text-neutral-400';
        statusEl.classList.remove('hidden');
        fetch(API + '/api/add-query', {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{ query: q }})
        }}).then(r => r.json()).then(data => {{
          if (data.ok) {{
            statusEl.textContent = `✓ "${{q}}" saved to config`;
            statusEl.className = 'text-xs mt-1.5 text-emerald-600';
          }} else {{
            statusEl.textContent = data.error || 'Saved for this session only';
            statusEl.className = 'text-xs mt-1.5 text-neutral-400';
          }}
          setTimeout(() => statusEl.classList.add('hidden'), 3000);
        }}).catch(() => {{
          statusEl.textContent = 'Session only (server unavailable)';
          statusEl.className = 'text-xs mt-1.5 text-neutral-400';
          setTimeout(() => statusEl.classList.add('hidden'), 3000);
        }});
      }} else {{
        statusEl.textContent = 'Added for this session';
        statusEl.className = 'text-xs mt-1.5 text-neutral-400';
        statusEl.classList.remove('hidden');
        setTimeout(() => statusEl.classList.add('hidden'), 2000);
      }}
    }}

    function toggleSettings() {{
      const panel = document.getElementById('settings-panel');
      const backdrop = document.getElementById('settings-backdrop');
      const open = panel.classList.contains('translate-x-full');
      panel.classList.toggle('translate-x-full', !open);
      panel.classList.toggle('translate-x-0', open);
      backdrop.classList.toggle('hidden', !open);
    }}

    function resetSettings() {{
      document.getElementById('minScore').value = 0;
      document.getElementById('minScoreVal').textContent = '0';
      document.querySelectorAll('#priceTypeFilters input').forEach(cb => cb.checked = true);
      localStorage.removeItem('tf_active_queries');
      toggleAllQueries(true);
    }}

    function saveLikes() {{
      localStorage.setItem('tf_liked', JSON.stringify([...liked]));
      const n = liked.size;
      savedCountEl.textContent = n > 0 ? `(${{n}})` : '';
    }}

    function toggleLike(e, itemId) {{
      e.preventDefault();
      e.stopPropagation();
      liked.has(itemId) ? liked.delete(itemId) : liked.add(itemId);
      saveLikes();
      const btn = e.currentTarget;
      btn.innerHTML = heartSvg(liked.has(itemId));
      btn.style.background = liked.has(itemId) ? 'black' : '';
      if (currentTab === 'saved') filter();
    }}

    function heartSvg(filled) {{
      return filled
        ? `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="w-4 h-4"><path d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 01-.383-.218 25.18 25.18 0 01-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0112 5.052 5.5 5.5 0 0116.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 01-4.244 3.17 15.247 15.247 0 01-.383.219l-.022.012-.007.004-.003.001a.752.752 0 01-.704 0l-.003-.001z"/></svg>`
        : `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4"><path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z"/></svg>`;
    }}

    function makeCard(d) {{
      const isLiked = liked.has(d.rank.toString());
      const img = d.thumb
        ? `<img src="${{d.thumb}}" loading="lazy" class="w-full h-48 object-cover" alt="">`
        : `<div class="w-full h-48 bg-neutral-100 flex items-center justify-center text-neutral-300 text-4xl">—</div>`;
      return `
        <div class="bg-white rounded-2xl overflow-hidden flex flex-col shadow-sm hover:shadow-md transition-shadow duration-200 group relative">
          <a href="${{d.url}}" target="_blank" class="block">${{img}}</a>
          <button onclick="toggleLike(event, '${{d.rank}}')"
            class="absolute top-3 right-3 w-8 h-8 rounded-full bg-black/30 backdrop-blur-sm flex items-center justify-center transition-colors hover:bg-black/60 text-white"
            style="${{isLiked ? 'background:black' : ''}}">
            ${{heartSvg(isLiked)}}
          </button>
          <a href="${{d.url}}" target="_blank" class="p-5 flex flex-col gap-3 flex-1">
            <p class="text-sm font-semibold leading-snug line-clamp-2 group-hover:underline decoration-1 underline-offset-2">${{d.title}}</p>
            <p class="text-xs text-neutral-400 leading-relaxed line-clamp-3 flex-1">${{d.description}}</p>
            <div class="flex items-center gap-1.5 pt-1 flex-wrap">
              <span class="score-badge relative group/score text-xs font-bold tabular-nums bg-black text-white px-2 py-0.5 rounded-full cursor-default select-none">
                ${{d.score}}
                ${{d.breakdown && Object.keys(d.breakdown).length ? `
                <span class="pointer-events-none absolute bottom-full left-0 mb-2 w-44 rounded-xl bg-neutral-900 text-white text-xs p-3 shadow-xl opacity-0 group-hover/score:opacity-100 transition-opacity duration-150 z-50">
                  <span class="block font-semibold mb-1.5 text-neutral-300">Score breakdown</span>
                  ${{[
                    ['Urgency',  d.breakdown.urgency],
                    ['Gem',      d.breakdown.gem],
                    ['Price',    d.breakdown.price],
                    ['Proximity',d.breakdown.proximity],
                    ['Penalty',  d.breakdown.penalty],
                    ['AI bonus', d.breakdown.ai],
                  ].filter(([,v]) => v !== undefined && v !== 0).map(([label, val]) =>
                    `<span class="flex justify-between gap-2"><span class="text-neutral-400">${{label}}</span><span class="${{val < 0 ? 'text-red-400' : 'text-green-400'}}">${{val > 0 ? '+' : ''}}${{val}}</span></span>`
                  ).join('')}}
                </span>` : ''}}
              </span>
              <span class="text-xs font-semibold text-neutral-700">${{d.price}}</span>
              ${{d.market_value ? `<span class="text-xs bg-emerald-50 text-emerald-700 border border-emerald-200 px-1.5 py-0.5 rounded-full font-medium">≈ ${{d.market_value}}</span>` : ''}}
              <span class="text-xs text-neutral-300">·</span>
              <span class="text-xs text-neutral-400">${{d.distance}}</span>
              <span class="text-xs text-neutral-300 ml-auto">${{d.date}}</span>
            </div>
            ${{d.ai_reason ? `<p class="text-xs text-amber-600 italic px-5 pb-4 -mt-1 line-clamp-2">✦ ${{d.ai_reason}}</p>` : ''}}
          </a>
        </div>`;
    }}

    function render(items) {{
      if (items.length === 0) {{
        const msg = currentTab === 'saved' ? 'No saved items yet.' : 'No results found.';
        grid.innerHTML = `<p class="col-span-full text-center text-neutral-400 text-sm py-24">${{msg}}</p>`;
        countEl.textContent = '0 results';
        return;
      }}
      grid.innerHTML = items.map(makeCard).join('');
      countEl.textContent = `${{items.length}} of ${{currentTab === 'saved' ? liked.size : ALL.length}}`;
    }}

    function setTab(tab) {{
      currentTab = tab;
      document.getElementById('tab-all').className = `text-xs px-3 py-1.5 rounded-lg font-medium transition-colors ${{tab === 'all' ? 'bg-black text-white' : 'text-neutral-400 hover:text-black'}}`;
      document.getElementById('tab-saved').className = `text-xs px-3 py-1.5 rounded-lg font-medium transition-colors ${{tab === 'saved' ? 'bg-black text-white' : 'text-neutral-400 hover:text-black'}}`;
      document.getElementById('controls').style.display = tab === 'saved' ? 'none' : '';
      filter();
    }}

    function filter() {{
      if (currentTab === 'saved') {{
        render(ALL.filter(d => liked.has(d.rank.toString())));
        return;
      }}
      const q = document.getElementById('search').value.toLowerCase();
      const sort = document.getElementById('sort').value;
      const maxPrice = parseInt(document.getElementById('maxPrice').value);
      const maxDist = parseInt(document.getElementById('maxDist').value) * 1000;
      const minScore = parseInt(document.getElementById('minScore').value);
      const enabledPriceTypes = new Set(
        [...document.querySelectorAll('#priceTypeFilters input:checked')].map(cb => cb.value)
      );

      let items = ALL.filter(d => {{
        if (q && !d.title.toLowerCase().includes(q) && !d.description.toLowerCase().includes(q)) return false;
        if (d.priceCents > 0 && d.priceCents / 100 > maxPrice) return false;
        if (d.distanceMeters > maxDist) return false;
        if (d.score < minScore) return false;
        if (!enabledPriceTypes.has(d.priceType)) return false;
        if (!activeQueries.has(d.query)) return false;
        return true;
      }});

      if (sort === 'price_asc') items.sort((a,b) => a.priceCents - b.priceCents);
      else if (sort === 'price_desc') items.sort((a,b) => b.priceCents - a.priceCents);
      else if (sort === 'distance') items.sort((a,b) => a.distanceMeters - b.distanceMeters);
      else items.sort((a,b) => b.score - a.score);

      render(items);
    }}

    document.getElementById('search').addEventListener('input', filter);
    document.getElementById('sort').addEventListener('change', filter);
    document.getElementById('maxPrice').addEventListener('input', e => {{
      document.getElementById('priceVal').textContent = e.target.value;
      filter();
    }});
    document.getElementById('maxDist').addEventListener('input', e => {{
      document.getElementById('distVal').textContent = e.target.value;
      filter();
    }});

    // Detect server and show run button
    let serverAvailable = false;
    let pollInterval = null;
    const API = window.location.protocol === 'file:' ? 'http://localhost:5001' : '';

    fetch(API + '/api/status').then(r => r.json()).then(() => {{
      serverAvailable = true;
      document.getElementById('run-section').classList.remove('hidden');
    }}).catch(() => {{}});

    function runFetch() {{
      if (!serverAvailable) return;
      const queries = [...activeQueries];
      if (queries.length === 0) {{
        alert('Select at least one search term.');
        return;
      }}
      const btn = document.getElementById('run-btn');
      const label = document.getElementById('run-label');
      const status = document.getElementById('run-status');
      btn.disabled = true;
      btn.classList.add('opacity-50', 'cursor-not-allowed');
      label.textContent = 'Fetching…';
      status.textContent = `Running ${{queries.length}} quer${{queries.length === 1 ? 'y' : 'ies'}}…`;
      status.classList.remove('hidden');

      fetch(API + '/api/run', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{ queries }})
      }}).then(r => r.json()).then(() => {{
        pollInterval = setInterval(checkDone, 2000);
      }}).catch(() => {{
        label.textContent = 'Run selected queries';
        status.textContent = 'Error starting run.';
        btn.disabled = false;
        btn.classList.remove('opacity-50', 'cursor-not-allowed');
      }});
    }}

    function checkDone() {{
      fetch(API + '/api/status').then(r => r.json()).then(data => {{
        if (!data.running) {{
          clearInterval(pollInterval);
          fetch(API + '/api/results').then(r => r.json()).then(results => {{
            // merge new results into ALL, preserving likes
            ALL.length = 0;
            results.forEach((d, i) => {{
              const pics = d.pictures || [];
              ALL.push({{
                rank: i + 1,
                score: d._score,
                title: d.title || '',
                description: (d.description || '').slice(0, 200),
                price: formatPrice(d),
                priceCents: (d.priceInfo || {{}}).priceCents || 0,
                priceType: normalizePriceType(d.priceInfo),
                distance: formatDist(d),
                distanceMeters: (d.location || {{}}).distanceMeters || 99999,
                city: (d.location || {{}}).cityName || '',
                url: 'https://www.marktplaats.nl' + (d.vipUrl || ''),
                thumb: pics.length ? pics[0].mediumUrl || '' : '',
                date: d.date || '',
                seller: (d.sellerInformation || {{}}).sellerName || '',
                query: d._query || '',
                ai_reason: d._ai_reason || '',
                market_value: d._market_value || '',
                breakdown: d._breakdown || {{}},
              }});
            }});
            const label = document.getElementById('run-label');
            const status = document.getElementById('run-status');
            const btn = document.getElementById('run-btn');
            label.textContent = 'Run selected queries';
            status.textContent = `Done — ${{ALL.length}} results loaded.`;
            btn.disabled = false;
            btn.classList.remove('opacity-50', 'cursor-not-allowed');
            // after a fresh run, add any new queries to activeQueries and persist
            ALL.map(d => d.query).forEach(q => activeQueries.add(q));
            saveQueryPrefs();
            buildQueryGroups();
            renderCustomGroup();
            filter();
          }});
        }}
      }});
    }}

    function formatPrice(d) {{
      const info = d.priceInfo || {{}};
      const cents = info.priceCents || 0;
      const pt = info.priceType || 'FIXED';
      if (pt === 'FREE' || (pt === 'FIXED' && cents === 0)) return 'Gratis';
      if (pt === 'FAST_BID' && cents === 0) return '€0 (bid)';
      if (pt === 'MIN_BID') return `€${{Math.floor(cents/100)}} (bod)`;
      return `€${{Math.floor(cents/100)}}`;
    }}

    function normalizePriceType(info) {{
      const pt = (info || {{}}).priceType || 'FIXED';
      const cents = (info || {{}}).priceCents || 0;
      return (pt === 'FREE' || (pt === 'FIXED' && cents === 0)) ? 'FREE' : pt;
    }}

    function formatDist(d) {{
      const m = (d.location || {{}}).distanceMeters || 0;
      return m >= 1000 ? `${{(m/1000).toFixed(1)}}km` : `${{m}}m`;
    }}

    buildQueryGroups();
    renderCustomGroup();
    saveLikes();
    filter();
  </script>
</body>
</html>"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    console.print(f"[dim]Saved HTML to {OUTPUT_HTML}[/dim]")


def _normalize_price_type(price_info: dict) -> str:
    pt = price_info.get("priceType", "FIXED")
    cents = price_info.get("priceCents", 0)
    if pt == "FREE" or (pt == "FIXED" and cents == 0):
        return "FREE"
    return pt


def _format_price(listing: dict) -> str:
    price_info = listing.get("priceInfo", {})
    price_type = _normalize_price_type(price_info)
    cents = price_info.get("priceCents", 0)
    if price_type == "FREE":
        return "Gratis"
    if price_type == "FAST_BID" and cents == 0:
        return "€0 (bid)"
    if price_type == "MIN_BID":
        return f"€{cents // 100} (bod)"
    return f"€{cents // 100}"


def _format_distance(listing: dict) -> str:
    d = listing.get("location", {}).get("distanceMeters", 0)
    if d >= 1000:
        return f"{d / 1000:.1f}km"
    return f"{d}m"
