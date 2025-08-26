export default function VideoCard({ video }) {
  // spotlight hover position
  const onMove = (e) => {
    const r = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - r.left) / r.width) * 100;
    e.currentTarget.style.setProperty("--mx", `${x}%`);
  };

  return (
    <article className="card" onMouseMove={onMove}>
      <img className="thumb" src={video.thumb_url} alt={video.title} loading="lazy" />
      <div className="meta">
        <div className="title">{video.title}</div>
        <div className="desc">{video.description}</div>
        <div className="row">
          <div className="pillset">
            {(video.tags || []).slice(0, 2).map((t) => (
              <span key={t} className="pill">{t}</span>
            ))}
          </div>
          <div className="actions">
            <button className="btn iconbtn" title="Like">👍</button>
            <a className="btn primary" href={video.source_url}>▶ Play</a>
          </div>
        </div>
      </div>
    </article>
  );
}
