
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { useAuth } from "@/contexts/AuthContext";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";

const signupSchema = z.object({
  name: z.string().min(1, "Name is required"),
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(6, "Password must be at least 6 characters long"),
});

type SignupFormValues = z.infer<typeof signupSchema>;

const SignUp = () => {
  const { signUp, isLoading } = useAuth();
  const form = useForm<SignupFormValues>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      name: "",
      email: "",
      password: "",
    },
  });

  const onSubmit = async (values: SignupFormValues) => {
    await signUp(values.email, values.password, values.name);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      <div className="flex-grow flex items-center justify-center bg-mind-gray-light p-4">
        <div className="w-full max-w-md">
          <Card className="shadow-lg">
            <CardHeader>
              <h1 className="text-2xl font-bold text-center text-mind-purple-dark">Create your account</h1>
              <p className="text-mind-gray text-center mt-2">
                Join MindNavigator to start your self-improvement journey
              </p>
            </CardHeader>
            
            <CardContent>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Full Name</FormLabel>
                        <FormControl>
                          <Input 
                            placeholder="Enter your name" 
                            {...field} 
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Email</FormLabel>
                        <FormControl>
                          <Input 
                            type="email"
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
                            placeholder="Create a password" 
                            {...field} 
                          />
                        </FormControl>
                        <p className="text-xs text-mind-gray mt-1">
                          Must be at least 6 characters long
                        </p>
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
                      {isLoading ? "Signing Up..." : "Sign Up"}
                    </Button>
                  </div>
                </form>
              </Form>
              
              <div className="mt-6 text-center">
                <p className="text-sm text-mind-gray">
                  By signing up, you agree to our{" "}
                  <Link to="/terms" className="text-mind-purple-dark hover:underline">
                    Terms of Service
                  </Link>{" "}
                  and{" "}
                  <Link to="/privacy" className="text-mind-purple-dark hover:underline">
                    Privacy Policy
                  </Link>
                  .
                </p>
              </div>
            </CardContent>
            
            <CardFooter className="flex justify-center border-t bg-mind-gray-light/50">
              <p className="text-sm text-mind-gray">
                Already have an account?{" "}
                <Link to="/login" className="text-mind-purple-dark hover:underline">
                  Log in
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

export default SignUp;
