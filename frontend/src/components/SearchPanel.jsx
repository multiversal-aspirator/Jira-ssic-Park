import { useState } from 'react';
import axios from 'axios';

export default function SearchPanel({ projectKey }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('ask'); // 'ask' or 'search'
  const [searchLimit, setSearchLimit] = useState(50);

  const switchMode = (nextMode) => {
    setMode(nextMode);
    setQuery('');
    setResults(null);
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setResults(null);

    try {
      if (mode === 'ask') {
        const { data } = await axios.post('/api/intelligence/ask', {
          question: query,
          project_key: projectKey || null,
        });
        setResults({ type: 'answer', data });
      } else {
        const { data } = await axios.get('/api/intelligence/search', {
          params: { query, limit: searchLimit },
        });
        setResults({ type: 'search', data });
      }
    } catch (err) {
      setResults({ type: 'error', data: err.response?.data?.detail || err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-panel">
      <div className="card">
        <h3>Project Intelligence</h3>
        <div className="search-mode-toggle">
          <button type="button" className={mode === 'ask' ? 'active' : ''} onClick={() => switchMode('ask')}>Ask AI</button>
          <button type="button" className={mode === 'search' ? 'active' : ''} onClick={() => switchMode('search')}>Semantic Search</button>
        </div>
        {mode === 'search' && (
          <div className="search-controls">
            <label htmlFor="search-limit">Result limit</label>
            <select
              id="search-limit"
              value={searchLimit}
              onChange={(e) => setSearchLimit(Number(e.target.value))}
            >
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
        )}
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={mode === 'ask' ? 'Ask a question about your project...' : 'Search project knowledge...'}
          />
          <button type="submit" disabled={loading} aria-label={loading ? 'Loading results' : mode === 'ask' ? 'Ask question' : 'Search'}>
            {loading ? '...' : mode === 'ask' ? 'Ask' : 'Search'}
          </button>
        </form>
      </div>

      {results?.type === 'answer' && (
        <div className="card">
          <h3>Answer</h3>
          <p className="ai-answer">{results.data.answer}</p>
          <div className="confidence-badge">
            Confidence: <span className={`badge badge-confidence-${results.data.confidence}`}>
              {results.data.confidence}
            </span>
          </div>
        </div>
      )}

      {results?.type === 'search' && (
        <div className="card">
          <h3>Search Results ({results.data.results?.length || 0})</h3>
          <ul className="search-results">
            {results.data.results?.map((r, i) => (
              <li key={i}>
                <span className="search-collection">[{r.collection}]</span>
                <span>{r.document}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {results?.type === 'error' && (
        <div className="error">{results.data}</div>
      )}
    </div>
  );
}
