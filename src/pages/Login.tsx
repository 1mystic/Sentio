
import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { useAuth } from "@/contexts/AuthContext";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";

const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(6, "Password must be at least 6 characters long"),
});

type LoginFormValues = z.infer<typeof loginSchema>;

const Login = () => {
  const { signIn, isLoading } = useAuth();
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const onSubmit = async (values: LoginFormValues) => {
    await signIn(values.email, values.password);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      <div className="flex-grow flex items-center justify-center bg-mind-gray-light p-4">
        <div className="w-full max-w-md">
          <Card className="shadow-lg">
            <CardHeader>
              <h1 className="text-2xl font-bold text-center text-mind-purple-dark">Welcome back</h1>
              <p className="text-mind-gray text-center mt-2">
                Log in to continue your self-improvement journey
              </p>
            </CardHeader>
            
            <CardContent>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Email</FormLabel>
                        <FormControl>
                          <Input 
                            placeholder="Enter your email" 
                            {...field} 
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="password"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Password</FormLabel>
                        <FormControl>
                          <Input 
                            type="password" 
                            placeholder="Enter your password" 
                            {...field} 
                          />
                        </FormControl>
                        <div className="flex justify-end mt-1">
                          <Link to="/forgot-password" className="text-xs text-mind-purple-dark hover:underline">
                            Forgot password?
                          </Link>
                        </div>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <div className="mt-2">
                    <Button 
                      type="submit" 
                      className="w-full bg-mind-purple-dark hover:bg-mind-purple-dark/90"
                      disabled={isLoading}
                    >
                      {isLoading ? "Logging in..." : "Log In"}
                    </Button>
                  </div>
                </form>
              </Form>
            </CardContent>
            
            <CardFooter className="flex justify-center border-t bg-mind-gray-light/50">
              <p className="text-sm text-mind-gray">
                Don't have an account?{" "}
                <Link to="/signup" className="text-mind-purple-dark hover:underline">
                  Sign up
                </Link>
              </p>
            </CardFooter>
          </Card>
          
          <div className="disclaimer mt-6 text-center">
            <strong>Note:</strong> MindNavigator is not a substitute for professional mental health treatment.
          </div>
        </div>
      </div>
      
      <Footer />
    </div>
  );
};

export default Login;
