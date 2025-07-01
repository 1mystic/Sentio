
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Lightbulb, Brain, Compass, Heart } from "lucide-react";

const Index = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      <main className="flex-grow">
        {/* Hero Section */}
        <section className="bg-gradient-to-b from-mind-purple-light to-white py-16 md:py-24">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl mx-auto text-center">
              <h1 className="text-4xl md:text-5xl font-bold text-mind-purple-dark mb-4">
                Understand Your Mind, Navigate Your Life
              </h1>
              <p className="text-xl text-mind-gray-dark mb-8 leading-relaxed">
                Discover cognitive patterns, manage anxiety, explore career paths, and improve 
                your mental wellbeing through evidence-based tools and insights.
              </p>
              
              <div className="disclaimer max-w-2xl mx-auto mb-8">
                <strong>Important:</strong> MindNavigator is a self-help tool, not therapy or diagnosis. 
                If you're experiencing a crisis, please seek professional help immediately.
                <Link to="/resources/crisis" className="underline ml-1 text-mind-purple-dark">
                  Access crisis resources here.
                </Link>
              </div>
              
              <Link to="/signup">
                <Button className="bg-mind-purple-dark hover:bg-mind-purple-dark/90 text-white px-8 py-6 text-lg">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </section>
        
        {/* Features Section */}
        <section className="py-16">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-bold text-center mb-12 text-mind-gray-dark">
              Discover a Better Understanding of Yourself
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              <Card className="card-hover">
                <CardContent className="pt-6">
                  <div className="mb-4 bg-mind-blue-light p-3 rounded-full w-12 h-12 flex items-center justify-center">
                    <Brain className="text-mind-blue-dark" size={24} />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Identify Biases</h3>
                  <p className="text-mind-gray">
                    Recognize cognitive biases that affect your decisions and learn strategies to overcome them.
                  </p>
                </CardContent>
              </Card>
              
              <Card className="card-hover">
                <CardContent className="pt-6">
                  <div className="mb-4 bg-mind-purple-light p-3 rounded-full w-12 h-12 flex items-center justify-center">
                    <Lightbulb className="text-mind-purple-dark" size={24} />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Manage Anxiety</h3>
                  <p className="text-mind-gray">
                    Learn evidence-based techniques to understand and manage feelings of anxiety and stress.
                  </p>
                </CardContent>
              </Card>
              
              <Card className="card-hover">
                <CardContent className="pt-6">
                  <div className="mb-4 bg-mind-blue-light p-3 rounded-full w-12 h-12 flex items-center justify-center">
                    <Compass className="text-mind-blue-dark" size={24} />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Explore Career Paths</h3>
                  <p className="text-mind-gray">
                    Clarify your values and strengths to make more informed career and life decisions.
                  </p>
                </CardContent>
              </Card>
              
              <Card className="card-hover">
                <CardContent className="pt-6">
                  <div className="mb-4 bg-mind-purple-light p-3 rounded-full w-12 h-12 flex items-center justify-center">
                    <Heart className="text-mind-purple-dark" size={24} />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Build Self-Compassion</h3>
                  <p className="text-mind-gray">
                    Develop a kinder relationship with yourself through guided exercises and reflections.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>
        
        {/* How It Works Section */}
        <section className="py-16 bg-mind-gray-light">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-bold text-center mb-12 text-mind-gray-dark">
              How It Works
            </h2>
            
            <div className="max-w-4xl mx-auto">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                <div className="text-center">
                  <div className="bg-white rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4 shadow-sm border">
                    <span className="text-2xl font-bold text-mind-purple-dark">1</span>
                  </div>
                  <h3 className="font-semibold mb-2">Assess</h3>
                  <p className="text-sm text-mind-gray">Complete assessments to understand your patterns</p>
                </div>
                
                <div className="text-center">
                  <div className="bg-white rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4 shadow-sm border">
                    <span className="text-2xl font-bold text-mind-purple-dark">2</span>
                  </div>
                  <h3 className="font-semibold mb-2">Reflect</h3>
                  <p className="text-sm text-mind-gray">Journal and engage with interactive tools</p>
                </div>
                
                <div className="text-center">
                  <div className="bg-white rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4 shadow-sm border">
                    <span className="text-2xl font-bold text-mind-purple-dark">3</span>
                  </div>
                  <h3 className="font-semibold mb-2">Learn</h3>
                  <p className="text-sm text-mind-gray">Explore modules with evidence-based content</p>
                </div>
                
                <div className="text-center">
                  <div className="bg-white rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4 shadow-sm border">
                    <span className="text-2xl font-bold text-mind-purple-dark">4</span>
                  </div>
                  <h3 className="font-semibold mb-2">Grow</h3>
                  <p className="text-sm text-mind-gray">Track insights and progress over time</p>
                </div>
              </div>
              
              <div className="text-center mt-12">
                <Link to="/signup">
                  <Button className="bg-mind-purple-dark hover:bg-mind-purple-dark/90 text-white">
                    Start Your Journey
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  );
};

export default Index;
