export default function Loader({ label = "Loading..." }: { label?: string }) {
    return (
      <div className="text-sm text-gray-600">{label}</div>
    );
  }
  