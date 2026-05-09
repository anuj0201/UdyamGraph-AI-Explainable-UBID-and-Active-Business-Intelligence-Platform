import Link from "next/link";

export default function Navbar() {
  return (
    <div className="navbar">
      <div><b>UdyamGraph AI</b></div>
      <div>
        <Link href="/">Home</Link>
        <Link href="/reviews">Review Queue</Link>
        <Link href="/graph">Graph</Link>
        <Link href="/records">Records</Link>
      </div>
    </div>
  );
}