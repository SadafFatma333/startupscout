import { Link, useLocation } from "react-router-dom";

export default function NavBar() {
  const { pathname } = useLocation();
  const linkCls = (path: string) =>
    `px-3 py-2 rounded-md text-sm font-medium ${
      pathname === path ? "bg-black text-white" : "text-gray-700 hover:bg-gray-200"
    }`;

  return (
    <header className="border-b bg-white">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <div className="font-semibold">StartupScout</div>
        <nav className="flex items-center gap-2">
          <Link className={linkCls("/chat")} to="/chat">Chat</Link>
          <Link className={linkCls("/ask")} to="/ask">Ask</Link>
          <Link className={linkCls("/search")} to="/search">Search</Link>
        </nav>
      </div>
    </header>
  );
}
