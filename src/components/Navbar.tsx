
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

const Navbar = () => {
  const { user, signOut, isLoading } = useAuth();

  return (
    <nav className="flex items-center justify-between p-4 border-b bg-white">
      <div className="flex items-center space-x-2">
        <Link to="/" className="text-2xl font-bold text-mind-purple-dark">MindNavigator</Link>
      </div>
      
      <div className="hidden md:flex items-center space-x-6">
        <Link to="/" className="text-mind-gray-dark hover:text-mind-purple-dark">
          Home
        </Link>
        <Link to="/about" className="text-mind-gray-dark hover:text-mind-purple-dark">
          About
        </Link>
        <Link to="/features" className="text-mind-gray-dark hover:text-mind-purple-dark">
          Features
        </Link>
      </div>
      
      <div className="flex items-center space-x-3">
        {user ? (
          <>
            <Link to="/dashboard">
              <Button variant="outline" className="border-mind-purple text-mind-purple-dark hover:bg-mind-purple-light">
                Dashboard
              </Button>
            </Link>
            <Button 
              className="bg-mind-purple-dark hover:bg-mind-purple-dark/90 text-white" 
              onClick={() => signOut()}
              disabled={isLoading}
            >
              Log out
            </Button>
          </>
        ) : (
          <>
            <Link to="/login">
              <Button variant="outline" className="border-mind-purple text-mind-purple-dark hover:bg-mind-purple-light">
                Log in
              </Button>
            </Link>
            <Link to="/signup">
              <Button className="bg-mind-purple-dark hover:bg-mind-purple-dark/90 text-white">
                Sign up
              </Button>
            </Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
