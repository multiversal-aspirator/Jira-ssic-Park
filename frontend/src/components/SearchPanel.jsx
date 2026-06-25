import { useState } from 'react';
import axios from 'axios';

export default function SearchPanel({ projectKey }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('ask'); // 'ask' or 'search'

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
          params: { query, limit: 10 },
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
          <button className={mode === 'ask' ? 'active' : ''} onClick={() => setMode('ask')}>Ask AI</button>
          <button className={mode === 'search' ? 'active' : ''} onClick={() => setMode('search')}>Semantic Search</button>
        </div>
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={mode === 'ask' ? 'Ask a question about your project...' : 'Search project knowledge...'}
          />
          <button type="submit" disabled={loading}>
            {loading ? '...' : mode === 'ask' ? 'Ask' : 'Search'}
          </button>
        </form>
      </div>

      {results?.type === 'answer' && (
        <div className="card">
          <h3>Answer</h3>
          <p className="ai-answer">{results.data.answer}</p>
          <div className="confidence-badge">
            Confidence: <span className={`badge badge-${results.data.confidence === 'high' ? 'low' : results.data.confidence === 'medium' ? 'medium' : 'high'}`}>
              {results.data.confidence}
            </span>
          </div>
          {results.data.sources?.length > 0 && (
            <details>
              <summary>Sources ({results.data.sources.length})</summary>
              <ul>
                {results.data.sources.map((s, i) => (
                  <li key={i}><small>[{s.collection}]</small> {s.document}</li>
                ))}
              </ul>
            </details>
          )}
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
