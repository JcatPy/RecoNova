export const MOCK_VIDEOS = Array.from({ length: 24 }).map((_, i) => {
  const id = i + 1;
  const names = ["Forest Dawn", "Ocean Breeze", "City Nights", "Snowy Peaks", "Golden Fields", "Lakeside Calm"];
  const tagsets = [
    ["nature","forest","calm"],
    ["ocean","waves","blue"],
    ["city","night","timelapse"],
    ["mountain","drone","snow"],
    ["field","sunset","golden"],
    ["lake","morning","mist"]
  ];
  const title = `${names[i % names.length]} ${Math.floor(Math.random()*90)+10}`;
  const tags = tagsets[i % tagsets.length];
  return {
    id,
    title,
    description: "A soothing clip showcasing beautiful scenery and atmospheric vibes.",
    thumb_url: `https://picsum.photos/seed/${id+30}/640/360`,
    source_url: "#",
    uploaded_at: new Date(Date.now() - i * 86400000).toISOString(),
    tags,
  };
});
