import { useEffect, useMemo, useState } from "react";
import { MOCK_VIDEOS } from "./mockData";
import VideoCard from "./components/VideoCard";
import SkeletonCard from "./components/SkeletonCard";

const ALL_TAGS = ["nature","ocean","city","mountain","timelapse","calm","blue","snow","night","drone","forest","waves","sunset","golden","lake","mist"];

export default function App() {
  const [query, setQuery] = useState("");
  const [activeTag, setActiveTag] = useState(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const pageSize = 12;

  // fake load for skeleton demo
  useEffect(() => {
    const t = setTimeout(() => setLoading(false), 700);
    return () => clearTimeout(t);
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return MOCK_VIDEOS.filter((v) => {
      const hitQ = !q || v.title.toLowerCase().includes(q) || (v.description||"").toLowerCase().includes(q);
      const hitT = !activeTag || (v.tags || []).includes(activeTag);
      return hitQ && hitT;
    });
  }, [query, activeTag]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const pageSafe = Math.min(page, totalPages);
  const slice = filtered.slice((pageSafe - 1) * pageSize, pageSafe * pageSize);

  useEffect(() => { setPage(1); }, [query, activeTag]);

  return (
    <>
      <nav className="nav">
        <div className="brand">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="9" stroke="white" opacity=".25"/>
            <path d="M8 12l3 3 5-6" stroke="white" strokeWidth="2" />
          </svg>
          <span>Reconova</span>
          <span className="badge">alpha</span>
        </div>
        <div className="nav-actions">
          <div className="search">
            <input
              value={query}
              onChange={(e)=>setQuery(e.target.value)}
              placeholder="Search videos…"
            />
            <button className="btn primary">Search</button>
          </div>
          <button className="btn">Sign in</button>
        </div>
      </nav>

      <div className="container">
        <div className="header">
          <div>
            <h1>Browse videos</h1>
            <div className="muted">{filtered.length} results</div>
          </div>
        </div>

        <div className="tags-wrap">
          <div className="tags">
            <button
              className={`tag ${!activeTag ? "active" : ""}`}
              onClick={()=>setActiveTag(null)}
            >all</button>
            {ALL_TAGS.map(t=>(
              <button
                key={t}
                className={`tag ${activeTag === t ? "active" : ""}`}
                onClick={()=>setActiveTag(t)}
              >{t}</button>
            ))}
          </div>
        </div>

        <section className="grid">
          {loading
            ? Array.from({ length: 12 }).map((_,i)=><SkeletonCard key={i} />)
            : slice.length > 0
              ? slice.map(v => <VideoCard key={v.id} video={v} />)
              : <div className="empty" style={{gridColumn:"1 / -1"}}>
                  No videos match your search. Try another keyword or tag.
                </div>
          }
        </section>

        <div className="footer">
          <button className="pagebtn" disabled={pageSafe===1} onClick={()=>setPage(p=>Math.max(1,p-1))}>← Prev</button>
          <div className="muted" style={{padding:"8px 12px"}}>Page {pageSafe} / {totalPages}</div>
          <button className="pagebtn" disabled={pageSafe===totalPages} onClick={()=>setPage(p=>Math.min(totalPages,p+1))}>Next →</button>
        </div>
      </div>
    </>
  );
}
