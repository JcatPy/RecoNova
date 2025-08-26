export default function SkeletonCard() {
  return (
    <div className="skel">
      <div className="thumb"></div>
      <div className="meta">
        <div className="bar" style={{ width: "70%" }}></div>
        <div className="bar" style={{ width: "90%" }}></div>
        <div className="bar" style={{ width: "50%" }}></div>
      </div>
    </div>
  );
}
