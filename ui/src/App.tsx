import { Routes, Route, Navigate } from "react-router-dom";
import NavBar from "./components/NavBar.tsx";
import Ask from "./pages/Ask.tsx";
import Search from "./pages/Search.tsx";
import Chat from "./pages/Chat.tsx";

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <NavBar />
      <main className="max-w-5xl w-full mx-auto px-4 py-6 flex-1">
        <Routes>
          <Route path="/" element={<Navigate to="/chat" replace />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/ask" element={<Ask />} />
          <Route path="/search" element={<Search />} />
        </Routes>
      </main>
      <footer className="text-center text-xs text-gray-500 py-4">StartupScout</footer>
    </div>
  );
}

