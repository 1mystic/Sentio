import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

export interface User {
  id: string;
  email: string;
  role?: string;

}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  signUp: (email: string, password: string, name: string) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  isAdmin: () => boolean;

}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Set up auth state listener
    // const { data: { subscription } } = supabase.auth.onAuthStateChange(
    //   (event, session) => {
    //     if (session && session.user) {
    //       setUser({
    //         id: session.user.id,
    //         email: session.user.email || "",
    //       });
    //     } else {
    //       setUser(null);
    //     }
    //     setIsLoading(false);
    //   }
    // );

    // Check for existing session
    // supabase.auth.getSession().then(({ data: { session } }) => {
    //   if (session && session.user) {
    //     setUser({
    //       id: session.user.id,
    //       email: session.user.email || "",
    //     });
    //   }
    //   setIsLoading(false);
    // });
    setIsLoading(false);

    // return () => {
    //   subscription.unsubscribe();
    // };
  }, []);

  const signUp = async (email: string, password: string, name: string) => {
    try {
      setIsLoading(true);
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: name,
          }
        }
      });

      if (error) throw error;
      
      toast.success("Sign up successful! You can now log in.");
      navigate("/login");
    } catch (error: any) {
      toast.error(error.message || "An error occurred during sign up");
      console.error("Sign up error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const signIn = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      // const { error } = await supabase.auth.signInWithPassword({
      //   email,
      //   password,
      // });

      // if (error) throw error;
      setUser({
        id: '1',
        email: email || "",
      });
      toast.success("Logged in successfully!");
      navigate("/dashboard");
    } catch (error: any) {
      toast.error(error.message || "An error occurred during login");
      console.error("Login error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const signOut = async () => {
    try {
      setIsLoading(true);
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
      
      toast.success("Logged out successfully");
      navigate("/");
    } catch (error: any) {
      toast.error(error.message || "An error occurred during logout");
      console.error("Logout error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const isAdmin = () => {
    return user?.role === 'admin' || user?.email === process.env.ADMIN_EMAIL;
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, signUp, signIn, signOut, isAdmin }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
