import { Link } from "react-router-dom";
import { Button } from "../components/ui";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-4 text-center">
      <p className="text-5xl font-bold text-primary">404</p>
      <p className="text-muted">We couldn't find that page.</p>
      <Link to="/">
        <Button>Back to dashboard</Button>
      </Link>
    </div>
  );
}
